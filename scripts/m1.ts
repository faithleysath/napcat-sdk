import { Project, ts } from "ts-morph";
import { createGenerator, type Config } from "ts-json-schema-generator";
import { writeFileSync, unlinkSync, existsSync } from "node:fs";
import * as path from "node:path";
import { createActionMap } from 'napcat-onebot/action';
import { ActionName } from 'napcat-onebot/action/router';

// 配置常量
const CONFIG = {
    tsConfig: "tsconfig.json",
    sourceRoot: "NapCatQQ/packages/napcat-onebot/action",
    outputFile: "openapi.json",
    tempFile: path.resolve(process.cwd(), `__temp_schema_gen_${Date.now()}.ts`)
};

const EXPAND_HELPER = `
    type ExpandRecursively<T> = T extends (...args: any[]) => any
        ? never 
        : T extends Date | Buffer
        ? string 
        : T extends object
        ? T extends infer O ? { [K in keyof O]: ExpandRecursively<O[K]> } : never
        : T;
`;

// --- Import 管理器 (保持不变，用于清洗 import) ---
class ImportManager {
    private importMap = new Map<string, string>();
    private usedNames = new Set<string>();
    private aliasCounter = 1;

    processTypeString(typeString: string): string {
        const regex = /import\("([^"]+)"\)\.([a-zA-Z0-9_$]+)/g;
        return typeString.replace(regex, (match, filePath, typeName) => {
            const key = `${filePath}|${typeName}`;
            if (this.importMap.has(key)) return this.importMap.get(key)!;

            let finalName = typeName;
            if (this.usedNames.has(finalName)) finalName = `${typeName}_${this.aliasCounter++}`;
            
            this.usedNames.add(finalName);
            this.importMap.set(key, finalName);
            return finalName;
        });
    }

    generateImportStatements(targetFilePath: string): string {
        return Array.from(this.importMap.entries()).map(([key, alias]) => {
            const [absPath, originalName] = key.split('|');
            let relativePath = path.relative(path.dirname(targetFilePath), absPath!);
            if (!relativePath.startsWith('.')) relativePath = './' + relativePath;
            relativePath = relativePath.replace(/(\.d\.ts|\.ts)$/, '').split(path.sep).join('/');
            const importClause = originalName === alias ? originalName : `${originalName} as ${alias}`;
            return `import { ${importClause} } from "${relativePath}";`;
        }).join('\n');
    }
}

// 初始化环境
const mockProxy = new Proxy({}, { get: () => new Proxy({}, { get: () => () => { } }) }) as any;
const { get: getActionInstance } = createActionMap(mockProxy, mockProxy);
const project = new Project({ tsConfigFilePath: CONFIG.tsConfig, skipAddingFilesFromTsConfig: true });
project.addSourceFilesAtPaths(`${CONFIG.sourceRoot}/**/*.ts`);

// --- 提取类型字符串逻辑 ---
function getCleanTypeString(className: string, importManager: ImportManager): string | null {
    const sourceFile = project.getSourceFiles().find(f => f.getClass(className));
    if (!sourceFile) return null;

    const classDec = sourceFile.getClass(className);
    const extendsClause = classDec?.getHeritageClauses()[0];
    if (!extendsClause || extendsClause.getTypeNodes()[0]!.getTypeArguments().length < 2) return null;

    const typeArgs = extendsClause.getTypeNodes()[0]!.getTypeArguments();
    const rawResponseType = typeArgs[1]!.getText();

    const startPos = sourceFile.getEnd();
    sourceFile.insertText(startPos, EXPAND_HELPER);
    
    const tempTypeAlias = sourceFile.addTypeAlias({
        name: "__TempCalc__",
        type: `ExpandRecursively<${rawResponseType}>`,
        isExported: true
    });

    const typeChecker = project.getTypeChecker();
    const expandedTypeString = typeChecker.compilerObject.typeToString(
        tempTypeAlias.getType().compilerType,
        undefined,
        ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.InTypeAlias | ts.TypeFormatFlags.UseFullyQualifiedType | ts.TypeFormatFlags.WriteTypeArgumentsOfSignature
    );

    tempTypeAlias.remove();
    sourceFile.removeText(startPos, sourceFile.getEnd());

    return importManager.processTypeString(expandedTypeString);
}

// --- 主流程 ---
async function main() {
    console.log("🚀 Starting OpenAPI generation (Inline Responses + Shared Components)...");

    const importManager = new ImportManager();
    // 存储 ActionKey -> 生成的类型名称 的映射
    const actionTypeMap: Record<string, string> = {}; 
    const actionRequestSchemas: Record<string, any> = {};
    const processedPaths = new Set<string>();
    let typeExportContent = "";

    // 1. 收集所有 Action 的 Response 类型
    for (const actionKey of Object.values(ActionName)) {
        const actionInstance = getActionInstance(actionKey as any);
        if (!actionInstance) continue;

        const apiPath = `/${actionKey}`;
        if (processedPaths.has(apiPath)) continue;
        processedPaths.add(apiPath);

        const className = actionInstance.constructor.name;
        const typeStr = getCleanTypeString(className, importManager);
        
        if (typeStr) {
            // 给每个 API 的响应体起个独立的名字，例如 Api_get_group_info_Response
            const uniqueTypeName = `Api_${actionKey.replace(/[^a-zA-Z0-9]/g, '_')}_Response`;
            
            typeExportContent += `export type ${uniqueTypeName} = ${typeStr};\n\n`;
            
            actionTypeMap[actionKey] = uniqueTypeName;
            actionRequestSchemas[actionKey] = actionInstance.payloadSchema ? { ...actionInstance.payloadSchema } : {};
            
            console.log(`Collect: ${apiPath} -> ${uniqueTypeName}`);
        }
    }

    // 2. 写入临时文件
    const importStatements = importManager.generateImportStatements(CONFIG.tempFile);
    const finalFileContent = `/* eslint-disable */\n// @ts-nocheck\n${importStatements}\n\n${typeExportContent}`;
    writeFileSync(CONFIG.tempFile, finalFileContent);

    try {
        // 3. 生成完整 Schema
        const config: Config = {
            path: CONFIG.tempFile,
            tsconfig: CONFIG.tsConfig,
            type: "*", 
            expose: "export", // 生成所有 export 的类型
            skipTypeCheck: true,
            topRef: false,
            jsDoc: "none"
        };
        
        // 原始 Schema 生成
        const schema = createGenerator(config).createSchema(config.type);
        
        // 4. Schema 清洗与重组 (关键步骤)
        // 将 "#/definitions/" 替换为 "#/components/schemas/"
        let schemaString = JSON.stringify(schema, null, 2).replace(/#\/definitions\//g, "#/components/schemas/");
        const rootSchema = JSON.parse(schemaString);
        const definitions = rootSchema.definitions || {};

        const openApiDoc: any = {
            openapi: "3.0.0",
            info: { title: "NapCat OneBot 11 API", version: "1.0.0" },
            paths: {},
            components: { schemas: {} }
        };

        // 识别哪些是 API Response，哪些是 Shared Types
        // 我们通过 actionTypeMap 的 values 来判断
        const apiResponseParams = new Set(Object.values(actionTypeMap));

        // 4.1 分离 Definitions
        for (const [defName, defSchema] of Object.entries(definitions)) {
            if (apiResponseParams.has(defName)) {
                // 这是一个 API 的 Response 根节点 -> 之后会放进 paths 里，这里不放 components
                // (暂时忽略，下面组装 path 时直接取用 defSchema)
            } else {
                // 这是一个被引用的 Shared Type (如 OB11User) -> 放进 components
                openApiDoc.components.schemas[defName] = defSchema;
            }
        }

        // 4.2 组装 Paths
        for (const [actionKey, typeName] of Object.entries(actionTypeMap)) {
            const apiPath = `/${actionKey}`;
            const className = getActionInstance(actionKey as any).constructor.name;
            
            // 从生成的 definitions 中把该 API 的具体 Schema 拿出来
            const specificResponseSchema = definitions[typeName];

            if (!specificResponseSchema) {
                console.warn(`⚠️ Warning: Schema for ${typeName} missing.`);
                continue;
            }

            openApiDoc.paths[apiPath] = {
                post: {
                    summary: className,
                    operationId: actionKey,
                    requestBody: {
                        content: { "application/json": { schema: actionRequestSchemas[actionKey] } }
                    },
                    responses: {
                        "200": {
                            description: "Successful response",
                            content: {
                                "application/json": {
                                    // ✨ 核心修改：直接把 Schema 对象放这里 (Inline)
                                    // 里面如果引用了 Shared Type，会自动指向 #/components/schemas/xxx
                                    schema: specificResponseSchema 
                                }
                            }
                        }
                    }
                }
            };
        }

        writeFileSync(CONFIG.outputFile, JSON.stringify(openApiDoc, null, 2));
        console.log(`✅ OpenAPI spec generated at: ${CONFIG.outputFile}`);

    } catch (e) {
        console.error("❌ Generation failed:", e);
    } finally {
        if (existsSync(CONFIG.tempFile)) unlinkSync(CONFIG.tempFile);
    }
}

main().catch(console.error);