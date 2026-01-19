// bun-patch.ts
import { plugin } from "bun";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const PROJECT_ROOT = process.cwd();

plugin({
  name: "fix-circular-dependency",
  setup(build) {
    build.onLoad({ filter: /NapCatQQ\/packages\/.*\.ts$/ }, (args) => {
      console.log(`[PATCH] 🛠️ 处理文件: ${args.path}`);
      let source = readFileSync(args.path, "utf8");
      
      // === 核心逻辑 1: 解除 OneBotAction.ts 的循环依赖 ===
      // 如果当前文件是 OneBotAction.ts
      if (args.path.endsWith("OneBotAction.ts")) {
        // 1. 删掉对 StreamBasic 的 import
        if (source.includes("import") && source.includes("StreamBasic")) {
             source = source.replace(
                /import\s+.*from\s+['"]\.\/stream\/StreamBasic['"];?/g, 
                "// [PATCHED] Circular dependency removed"
             );

             // 2. 手动注入 StreamStatus 枚举 (因为 OneBotAction 用到了它)
             // 我们直接把 enum 定义塞到文件最前面
             const injectedEnum = `
             export enum StreamStatus {
               Stream = 'stream',
               Response = 'response',
               Reset = 'reset',
               Error = 'error',
             }
             // Mock 类型，防止 TS 报错 (运行时会被抹除)
             type StreamPacketBasic = any; 
             `;
             
             source = injectedEnum + source;
             console.log(`[PATCH] 🔄 已解除 OneBotAction.ts 的循环依赖`);
        }
      }

      // === 核心逻辑 2: 之前的路径修正 (保持 v3.3 的逻辑) ===
      const modifiedSource = source.replace(
        /(from\s+['"])(napcat-[^'"]+)(['"])/g,
        (match, prefix, importPath, suffix) => {
          
          if (!importPath.includes('/')) return match; // 根引用放行
          if (/\.(ts|js|json|node)$/.test(importPath)) return match; // 有后缀放行

          const parts = importPath.split('/');
          const pkgName = parts[0];
          const subPath = parts.slice(1).join('/');
          const pkgRoot = join(PROJECT_ROOT, 'NapCatQQ', 'packages', pkgName);

          const strategies = [
            { path: subPath + '.ts', result: `${pkgName}/${subPath}.ts` },
            { path: join('src', subPath) + '.ts', result: `${pkgName}/src/${subPath}.ts` },
            { path: join(subPath, 'index.ts'), result: `${pkgName}/${subPath}/index.ts` },
            { path: join('src', subPath, 'index.ts'), result: `${pkgName}/src/${subPath}/index.ts` }
          ];

          for (const strategy of strategies) {
            const absPath = join(pkgRoot, strategy.path);
            if (existsSync(absPath)) {
              return `${prefix}${strategy.result}${suffix}`;
            }
          }
          return `${prefix}${importPath}.ts${suffix}`;
        }
      );

      return {
        contents: modifiedSource,
        loader: "ts",
      };
    });
  },
});