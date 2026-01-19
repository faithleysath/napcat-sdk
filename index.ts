import { Project, ts } from "ts-morph"; // 👈 注意这里引入了 ts
import { createGenerator, type Config } from "ts-json-schema-generator";
import { writeFileSync, unlinkSync, existsSync } from "fs";

// === 🔧 配置修改区 ===
const sourcePath = "NapCatQQ/packages/napcat-onebot/action/extends/FetchEmojiLike.ts";
const tempFilePath = "NapCatQQ/packages/napcat-onebot/action/extends/FetchEmojiLike.temp.ts"; 
const className = "FetchEmojiLike";
const outputPath = "onebot-response-emoji-like.json";

console.log(`🚀 启动智能预计算模式: ${className}...`);

try {
    // 1. 初始化项目
    const project = new Project({
        tsConfigFilePath: "tsconfig.json",
        skipAddingFilesFromTsConfig: true,
    });

    // 2. 加载源文件
    const sourceFile = project.addSourceFileAtPath(sourcePath);
    console.log(`📖 已加载源文件: ${sourcePath}`);

    const classDec = sourceFile.getClass(className);
    if (!classDec) throw new Error(`未找到类: ${className}`);

    // === 步骤 1: 偷取原始类型公式 ===
    const extendsClause = classDec.getHeritageClauses()[0];
    if (!extendsClause) throw new Error("没有 extends 子句");
    
    const typeArgs = extendsClause.getTypeNodes()[0].getTypeArguments();
    if (typeArgs.length < 2) throw new Error("extends 参数不足");
    
    const rawTypeFormula = typeArgs[1].getText(); 
    console.log(`🧪 捕获原始公式: "${rawTypeFormula}"`);

    // === 步骤 2: 【关键】原地计算类型结果 ===
    // 我们在当前文件里临时创建一个 TypeAlias，让 TS 编译器帮我们展开它
    // 这样能保留当前文件的所有 import 上下文
    const tempTypeName = "__CalcTempResult__";
    const tempTypeAlias = sourceFile.addTypeAlias({
        name: tempTypeName,
        type: rawTypeFormula
    });

    // 调用 TS 编译器计算最终类型
    const calculatedType = tempTypeAlias.getType();
    
    // 将计算结果转换为字符串 (例如 "{ emojiId: string; ... }" 或 "SomeInterface")
    // 使用 TypeFormatFlags.NoTruncation 防止大对象被截断
    // 使用 InTypeAlias 确保生成的格式是合法的类型定义
    const expandedTypeString = calculatedType.getText(
        undefined, 
        ts.TypeFormatFlags.NoTruncation | ts.TypeFormatFlags.InTypeAlias | ts.TypeFormatFlags.UseFullyQualifiedType
    );

    console.log(`🦋 类型已展开 (预览前50字符): ${expandedTypeString.slice(0, 50)}...`);

    // === 步骤 3: 毁灭与重建 ===
    
    // 移除原来的类、变量、Payload等，只保留 import
    classDec.remove();
    sourceFile.getVariableStatements().forEach(stmt => stmt.remove());
    sourceFile.getTypeAlias("Payload")?.remove();
    tempTypeAlias.remove(); // 移除刚才临时的 helper

    // 移除不必要的 import (OneBotAction, TypeBox)
    sourceFile.getImportDeclarations().forEach(imp => {
        const moduleName = imp.getModuleSpecifierValue();
        if (moduleName.includes("OneBotAction") || moduleName.includes("@sinclair/typebox") || moduleName.includes("action/router")) {
            imp.remove();
        }
    });

    // 将计算好的“展开类型”写入文件
    sourceFile.addTypeAlias({
        name: "TargetResponse",
        type: expandedTypeString, 
        isExported: true
    });

    writeFileSync(tempFilePath, sourceFile.getFullText());
    console.log(`📝 生成预计算临时文件: ${tempFilePath}`);

    // === 步骤 4: 生成 Schema ===
    const config: Config = {
        path: tempFilePath,
        tsconfig: "tsconfig.json",
        type: "TargetResponse",
        jsDoc: "none",
        skipTypeCheck: true, 
        expose: "none",
    };

    console.log("⚙️ 正在生成 Schema...");
    const generator = createGenerator(config);
    const schema = generator.createSchema(config.type);

    writeFileSync(outputPath, JSON.stringify(schema, null, 2));
    console.log(`✅ 成功！Schema 已生成: ${outputPath}`);

} catch (e) {
    console.error("❌ 发生错误:", e);
    // 打印更详细的错误栈
    if (e instanceof Error) {
        console.error(e.stack);
    }
} finally {
    if (existsSync(tempFilePath)) unlinkSync(tempFilePath);
    console.log("🧹 清理完成");
}