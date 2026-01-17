// _temp_extract_Payload.ts

import { FetchEmojiLike } from './FetchEmojiLike';
import { OneBotAction } from 'napcat-onebot/action/OneBotAction';

// 提取第一个泛型 P (Payload)
type ExtractPayload<T> = T extends OneBotAction<infer P, any> ? P : never;

type ActionInstance = InstanceType<typeof FetchEmojiLike>;

// 导出 Payload
export type __Target_Payload_Type__ = ExtractPayload<ActionInstance>;