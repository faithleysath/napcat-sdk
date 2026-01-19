import { Project, ts } from "ts-morph";
import { createGenerator, type Config } from "ts-json-schema-generator";
import { writeFileSync, unlinkSync, existsSync } from "fs";
import * as path from "path";

// === 🔧 配置修改区 ===
// 你的源文件路径
const sourcePath = "NapCatQQ/packages/napcat-onebot/action/group/GetGroupMemberInfo.ts";
// 目标类名
const className = "GetGroupMemberInfo";
// 输出文件名
const outputPath = "onebot-response-group-member-info.json";
// 临时文件名 (使用绝对路径，放在根目录防止路径混乱)
const tempFilePath = path.resolve(process.cwd(), "temp_calc_schema.ts");
// 临时类型名称
const targetTypeName = "CalculatedResponseType";

console.log(`🚀 启动智能预计算模式: ${className}...`);

try {
    // 1. 初始化 Project (内存模式，不修改文件)
    const project = new Project({
        tsConfigFilePath: "tsconfig.json",
        skipAddingFilesFromTsConfig: true,
    });

    // 2. 加载源文件
    if (!existsSync(sourcePath)) {
        throw new Error(`找不到源文件: ${sourcePath}`);
    }
    const sourceFile = project.addSourceFileAtPath(sourcePath);
    console.log(`📖 已加载源文件: ${sourcePath}`);

    const classDec = sourceFile.getClass(className);
    if (!classDec) throw new Error(`未找到类: ${className}`);

    // === 步骤 1: 提取继承的类型参数 ===
    const extendsClause = classDec.getHeritageClauses()[0];
    if (!extendsClause) throw new Error("该类没有 extends 子句，无法提取类型");
    
    const typeArgs = extendsClause.getTypeNodes()[0]!.getTypeArguments();
    if (typeArgs.length < 2) throw new Error("extends 参数不足，预期至少 2 个参数 (Payload, Response)");
    
    // 获取第二个泛型参数 (Response) 的文本
    const rawTypeFormula = typeArgs[1]!.getText(); 
    console.log(`🧪 捕获原始类型公式: "${rawTypeFormula}"`);

    // === 步骤 2: 注入增强版递归展开工具 ===
    // 针对 JSON Schema 的特殊处理：
    // 1. 剔除函数
    // 2. Date/Buffer -> string
    // 3. 强制展开对象属性
    const expandTypeStr = `
        type ExpandRecursively<T> = T extends (...args: any[]) => any
            ? never // 剔除函数
            : T extends Date
            ? string // Date 转 ISO String
            : T extends Buffer
            ? string // Buffer 转 Base64 String
            : T extends object
            ? T extends infer O ? { [K in keyof O]: ExpandRecursively<O[K]> } : never
            : T;
    `;
    
    // 将工具类型注入到源文件内存快照中 (不会写入磁盘)
    sourceFile.addStatements(expandTypeStr);

    // === 步骤 3: 使用编译器底层 API 计算并序列化类型 ===
    const tempTypeName = "__CalcTempResult__";
    const tempTypeAlias = sourceFile.addTypeAlias({
        name: tempTypeName,
        type: `ExpandRecursively<${rawTypeFormula}>`,
        isExported: true
    });

    // 获取计算后的类型对象
    const calculatedType = tempTypeAlias.getType();
    const typeChecker = project.getTypeChecker();

    console.log("🪄 正在进行深度展开与序列化...");

    // 核心黑魔法：使用 typeToString 配合 Flags
    // 解决 getText() 的截断和相对路径问题
    const expandedTypeString = typeChecker.compilerObject.typeToString(
        calculatedType.compilerType,
        undefined,
        ts.TypeFormatFlags.NoTruncation |               // 🚫 禁止截断 (... 5 more)
        ts.TypeFormatFlags.InTypeAlias |                // ✅ 适配 type alias 格式
        ts.TypeFormatFlags.UseFullyQualifiedType |      // 🗺️ 使用绝对路径 import("/a/b/c").Type
        ts.TypeFormatFlags.WriteTypeArgumentsOfSignature // 🧬 写入泛型参数
    );

    // 简单检查展开结果
    if (expandedTypeString.length < 10) {
        console.warn(`⚠️ 警告: 展开结果过短 (${expandedTypeString})，请检查是否出错`);
    } else {
        console.log(`🦋 类型展开成功 (长度: ${expandedTypeString.length})`);
    }

    // === 步骤 4: 构建临时文件 ===
    console.log("📝 正在构建临时文件...");
    
    // 添加 eslint-disable 和 ts-nocheck 防止临时文件报错阻断流程
    const tempFileContent = `
/* eslint-disable */
// @ts-nocheck
// [Auto Generated Temporary File]
// 此文件包含已展开的类型定义，包含绝对路径引用，用于生成 Schema

export type ${targetTypeName} = ${expandedTypeString};
`;
    writeFileSync(tempFilePath, tempFileContent);

    // === 步骤 5: 生成 Schema ===
    console.log("⚙️ 正在生成 JSON Schema...");

    const config: Config = {
        path: tempFilePath,
        tsconfig: "tsconfig.json",
        type: targetTypeName,
        
        // 关键配置
        skipTypeCheck: true,  // 跳过类型检查 (因为绝对路径 import 有时在隔离环境会报错)
        topRef: false,        // false = 直接输出结构，不套一层 definitions
        expose: "none",       // 不暴露其他类型
        jsDoc: "none",        // 忽略 JSDoc，保持 Schema 纯净
        extraTags: [],        // 清空额外标签
    };

    const generator = createGenerator(config);
    const schema = generator.createSchema(config.type);

    // === 步骤 6: 写入结果 ===
    const schemaString = JSON.stringify(schema, null, 2);
    writeFileSync(outputPath, schemaString);
    console.log(`✅ Schema 已成功生成: ${outputPath}`);

} catch (error) {
    console.error("\n❌ 致命错误:");
    if (error instanceof Error) {
        console.error(error.message);
        // 打印部分堆栈方便调试
        if (error.stack) console.error(error.stack.split('\n')[1]);
    } else {
        console.error(error);
    }
} finally {
    // === 步骤 7: 清理 ===
    if (existsSync(tempFilePath)) {
        // unlinkSync(tempFilePath);
        console.log("🧹 临时文件已清理");
    }
}