import { createGenerator, type Config } from "ts-json-schema-generator";
import { writeFileSync, readFileSync, unlinkSync } from "fs";
import { join, dirname } from "path";

// 定义原文件路径
const originalPath = "NapCatQQ/packages/napcat-onebot/types/message.ts";
// 定义同目录下的临时文件路径
const tempPath = join(dirname(originalPath), "message_temp.ts");

// 1. 读取源码
const sourceCode = readFileSync(originalPath, "utf-8");

// 2. 删除 content?: OB11Message[];
// 使用正则替换，\s* 匹配可能存在的空格
const modifiedCode = sourceCode.replace(/content\?:\s*OB11Message\[\];/g, "");

// 3. 写入临时文件
writeFileSync(tempPath, modifiedCode);

try {
    // 4. 配置 Config 指向临时文件
    const config: Config = {
        path: tempPath, // 这里改为临时文件路径
        tsconfig: "tsconfig.json",
        type: "OB11MessageData",
        skipTypeCheck: true,
    };

    // 5. 生成 Schema
    const schema = createGenerator(config).createSchema(config.type!);
    writeFileSync("schemas/OB11MessageData.schema.json", JSON.stringify(schema, null, 2));
    console.log("Schema generated successfully!");

} catch (error) {
    console.error("Error generating schema:", error);
} finally {
    // 6. 清理临时文件 (无论成功失败都执行)
    try {
        unlinkSync(tempPath);
    } catch (e) {
        console.warn("Failed to delete temp file:", e);
    }
}