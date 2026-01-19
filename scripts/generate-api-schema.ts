import { Project, ts, Node, ClassDeclaration, SourceFile, TypeNode } from "ts-morph";
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

// --- 修改后的：递归查找继承链逻辑 (支持跨文件 Import) ---
/**
 * 递归查找定义了 Response 泛型的父类
 * 返回找到的 TypeNode (Response 类型) 和该类型所在的 SourceFile (用于上下文解析)
 */
function findRootComponentType(classDec: ClassDeclaration): { responseTypeNode: TypeNode, hostSourceFile: SourceFile } | null {
    const extendsClause = classDec.getHeritageClauses()[0];
    if (!extendsClause) return null;

    const typeNodes = extendsClause.getTypeNodes();
    if (typeNodes.length === 0) return null;

    const expression = typeNodes[0];
    const typeArgs = expression!.getTypeArguments();

    // 1. 命中目标：当前类显式继承了带两个泛型参数的父类 (OneBotAction)
    // 我们假设第二个参数总是 Response 类型
    if (typeArgs.length === 2) {
        return {
            responseTypeNode: typeArgs[1]!,
            hostSourceFile: classDec.getSourceFile()
        };
    }

    // 2. 递归查找：获取父类定义
    // 使用 .getBaseClass() 方法，ts-morph 会自动解析 import 路径找到对应的源文件和类定义
    try {
        const baseClass = classDec.getBaseClass();
        if (baseClass) {
            return findRootComponentType(baseClass);
        }
    } catch (e) {
        // 某些极端情况下（如文件未被 Project 包含）可能抛错，忽略即可
        console.warn(`    ⚠️  Could not resolve base class for ${classDec.getName()}: ${(e as Error).message}`);
    }

    return null;
}

// --- 修改后的：提取类型字符串逻辑 ---
function getCleanTypeString(className: string, importManager: ImportManager): string | null {
    // 1. 找到对应的源文件和类
    const sourceFile = project.getSourceFiles().find(f => f.getClass(className));
    if (!sourceFile) return null;

    const classDec = sourceFile.getClass(className);
    if (!classDec) return null;

    // 2. 使用递归函数查找真正的 Response 定义位置
    const rootTypeInfo = findRootComponentType(classDec);
    
    // 如果找不到，或者链条断了，返回 null
    if (!rootTypeInfo) return null;

    const { responseTypeNode, hostSourceFile } = rootTypeInfo;
    
    // 3. 获取 Response 类型的文本 (例如 "ReturnDataType")
    const rawResponseType = responseTypeNode.getText();

    // 4. 重要：我们在找到泛型的那个文件 (hostSourceFile) 里注入 helper
    // 这样才能保证 ReturnDataType 这种非导出类型在作用域内是可见的
    const startPos = hostSourceFile.getEnd();
    hostSourceFile.insertText(startPos, EXPAND_HELPER);
    
    // 5. 在该文件中创建一个临时 TypeAlias 进行计算
    const tempTypeAlias = hostSourceFile.addTypeAlias({
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

    // 6. 清理现场
    tempTypeAlias.remove();
    hostSourceFile.removeText(startPos, hostSourceFile.getEnd());

    return importManager.processTypeString(expandedTypeString);
}

// --- 主流程 ---
async function main() {
    console.log("🚀 Starting OpenAPI generation (Root Interface Pattern)...");

    const importManager = new ImportManager();
    // 1. 新增：用来记录所有处理成功的 Action Key
    const actionKeys: string[] = []; 
    const actionRequestSchemas: Record<string, any> = {};
    const processedPaths = new Set<string>();
    
    let typeExportContent = "";

    // 2. 收集类型
    for (const actionKey of Object.values(ActionName)) {
        const actionInstance = getActionInstance(actionKey as any);
        if (!actionInstance) continue;

        const apiPath = `/${actionKey}`;
        if (processedPaths.has(apiPath)) continue;
        processedPaths.add(apiPath);

        const className = actionInstance.constructor.name;
        const typeStr = getCleanTypeString(className, importManager);
        
        if (typeStr) {
            const uniqueTypeName = `Api_${actionKey.replace(/[^a-zA-Z0-9]/g, '_')}_Response`;
            typeExportContent += `export type ${uniqueTypeName} = ${typeStr};\n`;
            
            // 记录 key，用于稍后组装 Root 接口
            actionKeys.push(actionKey); 
            actionRequestSchemas[actionKey] = actionInstance.payloadSchema ? { ...actionInstance.payloadSchema } : {};
            
            console.log(`Collect: ${apiPath} -> ${uniqueTypeName}`);
        }
    }

    // 3. 核心修改：构建一个超级接口包含所有 API，强制生成器去解析它们
    const rootInterfaceContent = `
export interface OpenApiRoot {
${actionKeys.map(key => {
    const typeName = `Api_${key.replace(/[^a-zA-Z0-9]/g, '_')}_Response`;
    // 注意：这里把每个 API 映射为接口的一个属性
    return `  "${key}": ${typeName};`;
}).join('\n')}
}
`;

    // 4. 写入临时文件（追加了 OpenApiRoot）
    const importStatements = importManager.generateImportStatements(CONFIG.tempFile);
    const finalFileContent = `/* eslint-disable */\n// @ts-nocheck\n${importStatements}\n\n${typeExportContent}\n${rootInterfaceContent}`;
    writeFileSync(CONFIG.tempFile, finalFileContent);

    try {
        // 5. 生成 Schema，指定入口为 OpenApiRoot
        const config: Config = {
            path: CONFIG.tempFile,
            tsconfig: CONFIG.tsConfig,
            type: "OpenApiRoot", // <--- 关键：只生成这个根类型
            expose: "none",
            skipTypeCheck: true,
            topRef: true,        // <--- 关键：保留根定义
            jsDoc: "none"
        };
        
        const schema = createGenerator(config).createSchema(config.type);
        
        // 6. Schema 清洗：将 ref 路径修正
        let schemaString = JSON.stringify(schema, null, 2).replace(/#\/definitions\//g, "#/components/schemas/");
        const rootSchema = JSON.parse(schemaString);
        
        // 获取 definitions (包含 Shared Types 和 OpenApiRoot)
        const definitions = rootSchema.definitions || {};
        
        const openApiDoc: any = {
            openapi: "3.0.0",
            info: { title: "NapCat OneBot 11 API", version: "1.0.0" },
            paths: {},
            components: { schemas: {} }
        };

        // 7. 提取 Components (排除 OpenApiRoot 本身)
        for (const [defName, defSchema] of Object.entries(definitions)) {
            if (defName === "OpenApiRoot") continue;
            openApiDoc.components.schemas[defName] = defSchema;
        }

        // 8. 从 OpenApiRoot 的 properties 中提取每个 API 的具体 Schema
        const rootProps = definitions["OpenApiRoot"]?.properties || {};

        for (const actionKey of actionKeys) {
            const apiPath = `/${actionKey}`;
            const className = getActionInstance(actionKey as any).constructor.name;
            
            // 直接从 Root 的属性里拿 Schema，这样即使是 inline 的也能拿到
            const specificResponseSchema = rootProps[actionKey] || {};

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