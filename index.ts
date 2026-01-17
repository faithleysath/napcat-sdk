import { writeFileSync } from 'node:fs';
import { createActionMap } from 'napcat-onebot/action/index';
import { ActionName } from 'napcat-onebot/action/router';

// 1. 制造 Mock 对象 (防止实例化报错)
// 使用 Proxy 拦截所有属性读取，返回空函数或空对象
const mockCore = new Proxy({}, {
    get: () => new Proxy({}, { get: () => () => { } })
}) as any;

const mockAdapter = new Proxy({}, {
    get: () => new Proxy({}, { get: () => () => { } })
}) as any;

console.log('🚀 正在初始化 ActionMap...');

// 2. 调用核心函数，获取 getter
// 这里会自动实例化所有 Action 类 (GetMsg, SendMsg 等等)
const { get } = createActionMap(mockAdapter, mockCore);

const schemas: Record<string, any> = {};

console.log('🔍 开始扫描 API...');

// 3. 遍历 ActionName 枚举里的所有 Key
Object.values(ActionName).forEach((actionKey) => {
    // 尝试获取该 Action 的实例
    const actionInstance = get(actionKey);

    if (actionInstance && actionInstance.payloadSchema) {
        // 拿到 TypeBox Schema
        schemas[actionKey] = actionInstance.payloadSchema;
    }
});

// 4. 保存文件
writeFileSync('./onebot-request-schema.json', JSON.stringify(schemas, null, 2));
console.log(`✅ 成功提取 ${Object.keys(schemas).length} 个 API 的 Schema！`);