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
    outputFile: "openapi.json"
};

// 工具类型定义：用于展开 TypeScript 类型
const EXPAND_HELPER = `
    type ExpandRecursively<T> = T extends (...args: any[]) => any
        ? never 
        : T extends Date | Buffer
        ? string 
        : T extends object
        ? T extends infer O ? { [K in keyof O]: ExpandRecursively<O[K]> } : never
        : T;
`;

// 初始化 Mock 环境以获取运行时 Action 实例
const mockProxy = new Proxy({}, { get: () => new Proxy({}, { get: () => () => { } }) }) as any;
const { get: getActionInstance } = createActionMap(mockProxy, mockProxy);

// 初始化 Project 用于静态分析
const project = new Project({
    tsConfigFilePath: CONFIG.tsConfig,
    skipAddingFilesFromTsConfig: true,
});
project.addSourceFilesAtPaths(`${CONFIG.sourceRoot}/**/*.ts`);

/**
 * 核心函数：通过静态分析生成 Response Schema
 */
function generateResponseSchema(className: string): any {
    const sourceFile = project.getSourceFiles().find(f => f.getClass(className));
    if (!sourceFile) return {};

    const classDec = sourceFile.getClass(className);
    const extendsClause = classDec?.getHeritageClauses()[0];
    
    // 检查是否继承自 OneBotAction 并包含足够的泛型参数
    if (!extendsClause || extendsClause.getTypeNodes()[0]!.getTypeArguments().length < 2) {
        return {};
    }

    const typeArgs = extendsClause.getTypeNodes()[0]!.getTypeArguments();
    const rawResponseType = typeArgs[1]!.getText(); // 获取 Response 泛型参数

    const tempFileName = path.resolve(process.cwd(), `__temp_schema_${Date.now()}_${Math.random().toString(36).slice(2)}.ts`);

    try {
        // 在内存中注入 helper 并计算完整类型
        const lastStatement = sourceFile.getStatements().at(-1);
        sourceFile.insertText(sourceFile.getEnd(), EXPAND_HELPER);
        
        const tempTypeAlias = sourceFile.addTypeAlias({
            name: "__TempCalc__",
            type: `ExpandRecursively<${rawResponseType}>`,
            isExported: true
        });

        const typeChecker = project.getTypeChecker();
        const expandedTypeString = typeChecker.compilerObject.typeToString(
            tempTypeAlias.getType().compilerType,
            undefined,
            ts.TypeFormatFlags.NoTruncation | 
            ts.TypeFormatFlags.InTypeAlias | 
            ts.TypeFormatFlags.UseFullyQualifiedType |
            ts.TypeFormatFlags.WriteTypeArgumentsOfSignature
        );

        // 清理内存修改
        tempTypeAlias.remove();

        // 写入临时文件供生成器使用
        writeFileSync(tempFileName, `/* eslint-disable */\n// @ts-nocheck\nexport type CalculatedResponse = ${expandedTypeString};`);

        // 生成 Schema
        const config: Config = {
            path: tempFileName,
            tsconfig: CONFIG.tsConfig,
            type: "CalculatedResponse",
            skipTypeCheck: true,
            topRef: false,
            expose: "none",
            jsDoc: "none",
            extraTags: [],
        };

        return createGenerator(config).createSchema(config.type);

    } catch (error) {
        console.error(`[Error] Failed to generate schema for ${className}:`, error);
        return {};
    } finally {
        if (existsSync(tempFileName)) unlinkSync(tempFileName);
    }
}

// 主流程
async function main() {
    console.log("🚀 Starting OpenAPI generation...");

    const openApiDoc: any = {
        openapi: "3.0.0",
        info: {
            title: "NapCat OneBot 11 API",
            version: "1.0.0",
        },
        paths: {}
    };

    const processedPaths = new Set<string>();

    for (const actionKey of Object.values(ActionName)) {
        const actionInstance = getActionInstance(actionKey as any);
        if (!actionInstance) continue;

        const apiPath = `/${actionKey}`;
        if (processedPaths.has(apiPath)) continue;
        processedPaths.add(apiPath);

        const className = actionInstance.constructor.name;
        console.log(`Processing: ${apiPath} [${className}]`);

        // 1. 获取 Request Schema (运行时)
        const requestSchema = actionInstance.payloadSchema ? { ...actionInstance.payloadSchema } : {};

        // 2. 获取 Response Schema (静态分析)
        const responseSchema = generateResponseSchema(className);

        // 3. 组装 OpenAPI 路径对象
        openApiDoc.paths[apiPath] = {
            post: {
                summary: className,
                operationId: actionKey,
                requestBody: {
                    content: {
                        "application/json": {
                            schema: requestSchema
                        }
                    }
                },
                responses: {
                    "200": {
                        description: "Successful response",
                        content: {
                            "application/json": {
                                schema: responseSchema
                            }
                        }
                    }
                }
            }
        };
    }

    writeFileSync(CONFIG.outputFile, JSON.stringify(openApiDoc, null, 2));
    console.log(`✅ OpenAPI spec generated at: ${CONFIG.outputFile}`);
}

main().catch(console.error);