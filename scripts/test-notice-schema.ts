import { createGenerator, type Config } from "ts-json-schema-generator";
import * as fs from "fs";
import * as path from "path";

// --- 配置 ---
const SOURCE_DIR = "NapCatQQ/packages/napcat-onebot/event/notice";
const OUTPUT_DIR = "temp/schemas";
const TS_CONFIG = "tsconfig.json"; // ⚠️ 确保这里指向能解析 @/napcat-onebot 路径的配置

// --- 主逻辑 ---
function main() {
    // 1. 确保输出目录存在
    if (!fs.existsSync(OUTPUT_DIR)) {
        fs.mkdirSync(OUTPUT_DIR, { recursive: true });
    }

    // 2. 读取目录下的 ts 文件
    const files = fs.readdirSync(SOURCE_DIR).filter(f => f.endsWith(".ts"));

    console.log(`🔍 Found ${files.length} files in ${SOURCE_DIR}`);

    for (const file of files) {
        const fullPath = path.join(SOURCE_DIR, file);
        const content = fs.readFileSync(fullPath, "utf-8");

        // 3. 正则提取 export class 类名 (简单粗暴但有效)
        // 匹配模式: export class (类名) ...
        // 或者是 export abstract class (类名) ...
        const match = content.match(/export\s+(?:abstract\s+)?class\s+(\w+)/);

        if (!match) {
            console.warn(`⚠️  Skipping ${file}: No exported class found.`);
            continue;
        }

        const className = match[1];
        console.log(`⚙️  Processing: ${className} (${file})...`);

        try {
            // 4. 配置 Generator
            const config: Config = {
                path: fullPath,      // 指定入口文件
                tsconfig: TS_CONFIG, // 指定 TS 配置
                type: className,     // 指定入口类型
                skipTypeCheck: true, // 跳过完整类型检查以容忍环境缺失
                jsDoc: "extended",   // 保留注释
                expose: "all",       // 导出所有引用到的定义
                topRef: true,        // 顶层引用
            };

            // 5. 生成 Schema
            const generator = createGenerator(config);
            const schema = generator.createSchema(config.type);

            // 6. 写入文件
            const outPath = path.join(OUTPUT_DIR, `${className}.json`);
            fs.writeFileSync(outPath, JSON.stringify(schema, null, 2));
            console.log(`✅ Success: ${outPath}`);

        } catch (error) {
            console.error(`❌ Error processing ${className}:`, error instanceof Error ? error.message : error);
        }
    }
}

main();