from __future__ import annotations
from typing import Any, Literal, NotRequired, TypedDict
from .messages.generated import (
    Message,
    JsonDataConfig,
    NodeDataNew,
)


class BaseResponse(TypedDict):
    status: str
    """
    状态 (ok/failed)
    """
    retcode: float
    """
    返回码
    """
    message: NotRequired[str]
    """
    消息
    """
    wording: NotRequired[str]
    """
    提示
    """
    stream: NotRequired[Literal["stream-action", "normal-action"]]
    """
    流式响应
    """


type EmptyData = None
"""
无数据
"""


class FileBaseData(TypedDict):
    """
    文件消息段基础数据
    """

    file: str
    """
    文件路径/URL/file:///
    """
    path: NotRequired[str]
    """
    文件路径
    """
    url: NotRequired[str]
    """
    文件URL
    """
    name: NotRequired[str]
    """
    文件名
    """
    thumb: NotRequired[str]
    """
    缩略图
    """


class OB11MessageAtData(TypedDict):
    qq: str
    """
    QQ号或all
    """
    name: NotRequired[str]
    """
    显示名称
    """


class OB11MessageContactData(TypedDict):
    type: Literal["qq", "group"]
    """
    联系人类型
    """
    id: str
    """
    联系人ID
    """


class OB11MessageCustomMusicData(TypedDict):
    type: Literal["qq", "163", "kugou", "migu", "kuwo", "custom"]
    """
    音乐平台类型
    """
    id: None
    url: str
    """
    点击后跳转URL
    """
    audio: NotRequired[str]
    """
    音频URL
    """
    title: NotRequired[str]
    """
    音乐标题
    """
    image: str
    """
    封面图片URL
    """
    content: NotRequired[str]
    """
    音乐简介
    """


class OB11MessageDiceData(TypedDict):
    result: float | str
    """
    骰子结果
    """


class OB11MessageFaceData(TypedDict):
    id: str
    """
    表情ID
    """
    resultId: NotRequired[str]
    """
    结果ID
    """
    chainCount: NotRequired[float]
    """
    连击数
    """


class OB11MessageFileBase(TypedDict):
    """
    文件消息基础接口
    """

    data: FileBaseData


class OB11MessageFlashTransferData(TypedDict):
    fileSetId: str
    """
    文件集ID
    """


class OB11MessageForwardData(TypedDict):
    id: str
    """
    合并转发ID
    """
    content: NotRequired[dict[str, Any]]
    """
    消息内容 (OB11Message[])
    """


class OB11MessageIdMusicData(TypedDict):
    type: Literal["qq", "163", "kugou", "migu", "kuwo"]
    """
    音乐平台类型
    """
    id: str | float
    """
    音乐ID
    """


class Data(FileBaseData):
    summary: NotRequired[str]
    """
    图片摘要
    """
    sub_type: NotRequired[float]
    """
    图片子类型
    """


class OB11MessageJsonData(TypedDict):
    data: str | dict[str, Any]
    """
    JSON数据
    """
    config: NotRequired[JsonDataConfig]


class OB11MessageLocationData(TypedDict):
    lat: str | float
    """
    纬度
    """
    lon: str | float
    """
    经度
    """
    title: NotRequired[str]
    """
    标题
    """
    content: NotRequired[str]
    """
    内容
    """


class OB11MessageMFaceData(TypedDict):
    emoji_package_id: float
    """
    表情包ID
    """
    emoji_id: str
    """
    表情ID
    """
    key: str
    """
    表情key
    """
    summary: str
    """
    表情摘要
    """


class OB11MessageMarkdownData(TypedDict):
    content: str
    """
    Markdown内容
    """


class OB11MessageMiniAppData(TypedDict):
    data: str
    """
    小程序数据
    """


class OB11MessageNodeData(TypedDict):
    id: NotRequired[str]
    """
    转发消息ID
    """
    user_id: NotRequired[float | str]
    """
    发送者QQ号
    """
    uin: NotRequired[float | str]
    """
    发送者QQ号(兼容go-cqhttp)
    """
    nickname: str
    """
    发送者昵称
    """
    name: NotRequired[str]
    """
    发送者昵称(兼容go-cqhttp)
    """
    content: dict[str, Any]
    """
    消息内容 (OB11MessageMixType)
    """
    source: NotRequired[str]
    """
    消息来源
    """
    news: NotRequired[list[NodeDataNew]]
    summary: NotRequired[str]
    """
    摘要
    """
    prompt: NotRequired[str]
    """
    提示
    """
    time: NotRequired[str]
    """
    时间
    """


class OB11MessageOnlineFileData(TypedDict):
    msgId: str
    """
    消息ID
    """
    elementId: str
    """
    元素ID
    """
    fileName: str
    """
    文件名
    """
    fileSize: str
    """
    文件大小
    """
    isDir: bool
    """
    是否为目录
    """


class OB11MessagePokeData(TypedDict):
    type: str
    """
    戳一戳类型
    """
    id: str
    """
    戳一戳ID
    """


class OB11MessageRPSData(TypedDict):
    result: float | str
    """
    猜拳结果
    """


class OB11MessageReplyData(TypedDict):
    id: NotRequired[str]
    """
    消息ID的短ID映射
    """
    seq: NotRequired[float]
    """
    消息序列号，优先使用
    """


class OB11MessageEmojiLikesListItem(TypedDict):
    emoji_id: str
    """
    表情ID
    """
    emoji_type: str
    """
    表情类型
    """
    likes_cnt: str
    """
    点赞数
    """


class OB11MessageTextData(TypedDict):
    text: str
    """
    纯文本内容
    """


class OB11MessageXmlData(TypedDict):
    data: str
    """
    XML数据
    """


class OB11PostSendMsgNew(TypedDict):
    text: str
    """
    文本
    """


class OB11Sender(TypedDict):
    """
    OneBot 11 发送者信息
    """

    user_id: float | str
    """
    发送者QQ号
    """
    nickname: str
    """
    发送者昵称
    """
    card: NotRequired[str]
    """
    群名片
    """
    role: NotRequired[str]
    """
    角色
    """
    sex: NotRequired[str]
    """
    性别
    """
    age: NotRequired[float]
    """
    年龄
    """
    area: NotRequired[str]
    """
    地区
    """
    level: NotRequired[str]
    """
    等级
    """
    title: NotRequired[str]
    """
    头衔
    """


class OB11GroupMember(TypedDict):
    """
    OneBot 11 群成员信息
    """

    group_id: float
    """
    群号
    """
    user_id: float
    """
    QQ号
    """
    nickname: str
    """
    昵称
    """
    card: NotRequired[str]
    """
    名片
    """
    sex: NotRequired[str]
    """
    性别
    """
    age: NotRequired[float]
    """
    年龄
    """
    join_time: NotRequired[float]
    """
    入群时间戳
    """
    last_sent_time: NotRequired[float]
    """
    最后发言时间戳
    """
    level: NotRequired[str]
    """
    等级
    """
    qq_level: NotRequired[float]
    """
    QQ等级
    """
    role: NotRequired[str]
    """
    角色 (owner/admin/member)
    """
    title: NotRequired[str]
    """
    头衔
    """
    area: NotRequired[str]
    """
    地区
    """
    unfriendly: NotRequired[bool]
    """
    是否不良记录
    """
    title_expire_time: NotRequired[float]
    """
    头衔过期时间
    """
    card_changeable: NotRequired[bool]
    """
    是否允许修改名片
    """
    shut_up_timestamp: NotRequired[float]
    """
    禁言截止时间戳
    """
    is_robot: NotRequired[bool]
    """
    是否为机器人
    """
    qage: NotRequired[float]
    """
    Q龄
    """


class OB11Group(TypedDict):
    """
    OneBot 11 群信息
    """

    group_all_shut: float
    """
    是否全员禁言
    """
    group_remark: str
    """
    群备注
    """
    group_id: float
    """
    群号
    """
    group_name: str
    """
    群名称
    """
    member_count: NotRequired[float]
    """
    成员人数
    """
    max_member_count: NotRequired[float]
    """
    最大成员人数
    """


class EmojiLikesListItem(TypedDict):
    emoji_id: str
    """
    表情符号ID
    """
    emoji_type: str
    """
    表情符号类型
    """
    likes_cnt: str
    """
    点赞数
    """


class OB11Notify(TypedDict):
    """
    OneBot 11 通知信息
    """

    request_id: float
    """
    请求ID
    """
    invitor_uin: float
    """
    邀请者QQ
    """
    invitor_nick: str
    """
    邀请者昵称
    """
    group_id: float
    """
    群号
    """
    group_name: str
    """
    群名称
    """
    message: str
    """
    附言
    """
    checked: bool
    """
    是否已处理
    """
    actor: float
    """
    操作者QQ
    """
    requester_nick: str
    """
    申请者昵称
    """


class OB11User(TypedDict):
    """
    OneBot 11 用户信息
    """

    birthday_year: NotRequired[float]
    """
    出生年份
    """
    birthday_month: NotRequired[float]
    """
    出生月份
    """
    birthday_day: NotRequired[float]
    """
    出生日期
    """
    phone_num: NotRequired[str]
    """
    手机号
    """
    email: NotRequired[str]
    """
    邮箱
    """
    category_id: NotRequired[float]
    """
    分组ID
    """
    user_id: float
    """
    QQ号
    """
    nickname: str
    """
    昵称
    """
    remark: NotRequired[str]
    """
    备注
    """
    sex: NotRequired[str]
    """
    性别
    """
    level: NotRequired[float]
    """
    等级
    """
    age: NotRequired[float]
    """
    年龄
    """
    qid: NotRequired[str]
    """
    QID
    """
    login_days: NotRequired[float]
    """
    登录天数
    """
    categoryName: NotRequired[str]
    """
    分组名称
    """
    categoryId: NotRequired[float]
    """
    分组ID
    """


class OB11LatestMessageSender(TypedDict):
    user_id: float
    """
    用户QQ号
    """
    nickname: str
    """
    用户昵称
    """
    card: NotRequired[str]
    """
    用户名片
    """
    role: NotRequired[str]
    """
    用户角色
    """


class OB11LatestMessage(TypedDict):
    """
    最后一条消息
    """

    self_id: float
    """
    发送者QQ号
    """
    user_id: float
    """
    接收者QQ号
    """
    time: float
    """
    时间戳
    """
    real_seq: str
    """
    消息序号
    """
    message_type: str
    """
    消息类型
    """
    sender: OB11LatestMessageSender
    raw_message: str
    """
    原始消息
    """
    font: float
    """
    字体大小
    """
    sub_type: str
    """
    子类型
    """
    message: dict[str, Any]
    """
    消息内容
    """
    message_format: str
    """
    消息格式
    """
    post_type: str
    """
    发布类型
    """
    group_id: float
    """
    群号
    """
    group_name: str
    """
    群名称
    """


class CleanStreamTempFilePostRequest(TypedDict):
    pass


type CleanStreamTempFilePostResponse = None


class DownloadFileStreamPostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径或 URL
    """
    file_id: NotRequired[str]
    """
    文件 ID
    """
    chunk_size: NotRequired[float]
    """
    分块大小 (字节)
    """


type DownloadFileStreamPostResponse = dict[str, Any]


class DownloadFileRecordStreamPostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径或 URL
    """
    file_id: NotRequired[str]
    """
    文件 ID
    """
    chunk_size: NotRequired[float]
    """
    分块大小 (字节)
    """
    out_format: NotRequired[str]
    """
    输出格式
    """


type DownloadFileRecordStreamPostResponse = dict[str, Any]


class DownloadFileImageStreamPostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径或 URL
    """
    file_id: NotRequired[str]
    """
    文件 ID
    """
    chunk_size: NotRequired[float]
    """
    分块大小 (字节)
    """


type DownloadFileImageStreamPostResponse = dict[str, Any]


class TestDownloadStreamPostRequest(TypedDict):
    error: NotRequired[bool]
    """
    是否触发测试错误
    """


type TestDownloadStreamPostResponse = dict[str, Any]


class UploadFileStreamPostRequest(TypedDict):
    stream_id: str
    """
    流 ID
    """
    chunk_data: NotRequired[str]
    """
    分块数据 (Base64)
    """
    chunk_index: NotRequired[float]
    """
    分块索引
    """
    total_chunks: NotRequired[float]
    """
    总分块数
    """
    file_size: NotRequired[float]
    """
    文件总大小
    """
    expected_sha256: NotRequired[str]
    """
    期望的 SHA256
    """
    is_complete: NotRequired[bool]
    """
    是否完成
    """
    filename: NotRequired[str]
    """
    文件名
    """
    reset: NotRequired[bool]
    """
    是否重置
    """
    verify_only: NotRequired[bool]
    """
    是否仅验证
    """
    file_retention: float
    """
    文件保留时间 (毫秒)
    """


type UploadFileStreamPostResponse = dict[str, Any]


class DelGroupAlbumMediaPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    album_id: str
    """
    相册ID
    """
    lloc: str
    """
    媒体ID (lloc)
    """


type DelGroupAlbumMediaPostResponse = dict[str, Any]


class SetGroupAlbumMediaLikePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    album_id: str
    """
    相册ID
    """
    lloc: str
    """
    媒体ID (lloc)
    """
    id: str
    """
    点赞ID
    """
    set: bool
    """
    是否点赞
    """


type SetGroupAlbumMediaLikePostResponse = dict[str, Any]


class DoGroupAlbumCommentPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    album_id: str
    """
    相册 ID
    """
    lloc: str
    """
    图片 ID
    """
    content: str
    """
    评论内容
    """


type DoGroupAlbumCommentPostResponse = dict[str, Any]


class GetGroupAlbumMediaListPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    album_id: str
    """
    相册ID
    """
    attach_info: str
    """
    附加信息（用于分页）
    """


type GetGroupAlbumMediaListPostResponse = dict[str, Any]


class GetQunAlbumListPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type GetQunAlbumListPostResponse = list[Any]


class UploadImageToQunAlbumPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    album_id: str
    """
    相册ID
    """
    album_name: str
    """
    相册名称
    """
    file: str
    """
    图片路径、URL或Base64
    """


type UploadImageToQunAlbumPostResponse = dict[str, Any]


class SetGroupTodoPostRequest(TypedDict):
    group_id: str | float
    """
    群号
    """
    message_id: NotRequired[str]
    """
    消息ID
    """
    message_seq: NotRequired[str]
    """
    消息Seq (可选)
    """


type SetGroupTodoPostResponse = None


class GetGroupDetailInfoPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


class GetGroupDetailInfoPostResponse(TypedDict):
    group_id: float
    """
    群号
    """
    group_name: str
    """
    群名称
    """
    member_count: float
    """
    成员数量
    """
    max_member_count: float
    """
    最大成员数量
    """
    group_all_shut: float
    """
    全员禁言状态
    """
    group_remark: str
    """
    群备注
    """


class SetGroupKickMembersPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: list[str]
    """
    QQ号列表
    """
    reject_add_request: NotRequired[bool | str]
    """
    是否拒绝加群请求
    """


type SetGroupKickMembersPostResponse = None


class SetGroupAddOptionPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    add_type: float
    """
    加群方式
    """
    group_question: NotRequired[str]
    """
    加群问题
    """
    group_answer: NotRequired[str]
    """
    加群答案
    """


type SetGroupAddOptionPostResponse = None


class SetGroupRobotAddOptionPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    robot_member_switch: NotRequired[float]
    """
    机器人成员开关
    """
    robot_member_examine: NotRequired[float]
    """
    机器人成员审核
    """


type SetGroupRobotAddOptionPostResponse = None


class SetGroupSearchPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    no_code_finger_open: NotRequired[float]
    """
    未知
    """
    no_finger_open: NotRequired[float]
    """
    未知
    """


type SetGroupSearchPostResponse = None


class SetDoubtFriendsAddRequestPostRequest(TypedDict):
    flag: str
    """
    请求 flag
    """
    approve: bool
    """
    是否同意 (强制为 true)
    """


type SetDoubtFriendsAddRequestPostResponse = Any


class GetDoubtFriendsAddRequestPostRequest(TypedDict):
    count: float
    """
    获取数量
    """


type GetDoubtFriendsAddRequestPostResponse = dict[str, Any]


class SetFriendRemarkPostRequest(TypedDict):
    user_id: str
    """
    对方 QQ 号
    """
    remark: str
    """
    备注内容
    """


type SetFriendRemarkPostResponse = None


class GetRkeyPostRequest(TypedDict):
    pass


class Datum(TypedDict):
    type: str
    """
    类型 (private/group)
    """
    rkey: str
    """
    RKey
    """
    created_at: float
    """
    创建时间
    """
    ttl: float
    """
    有效期
    """


type GetRkeyPostResponse = list[Datum]


class GetRkeyServerPostRequest(TypedDict):
    pass


class GetRkeyServerPostResponse(TypedDict):
    private_rkey: NotRequired[str]
    """
    私聊 RKey
    """
    group_rkey: NotRequired[str]
    """
    群聊 RKey
    """
    expired_time: NotRequired[float]
    """
    过期时间
    """
    name: str
    """
    名称
    """


class SetGroupRemarkPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    remark: str
    """
    备注
    """


type SetGroupRemarkPostResponse = None


class GetGroupInfoExPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type GetGroupInfoExPostResponse = dict[str, Any]


class FetchEmojiLikePostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """
    emojiId: float | str
    """
    表情ID
    """
    emojiType: float | str
    """
    表情类型
    """
    count: float | str
    """
    获取数量
    """
    cookie: str
    """
    分页Cookie
    """


class Data3EmojiLikesListItem(TypedDict):
    tinyId: str
    """
    TinyID
    """
    nickName: str
    """
    昵称
    """
    headUrl: str
    """
    头像URL
    """


class FetchEmojiLikePostResponse(TypedDict):
    emojiLikesList: list[Data3EmojiLikesListItem]
    """
    表情回应列表
    """
    cookie: str
    """
    分页Cookie
    """
    isLastPage: bool
    """
    是否最后一页
    """
    isFirstPage: bool
    """
    是否第一页
    """
    result: float
    """
    结果状态码
    """
    errMsg: str
    """
    错 误信息
    """


class GetEmojiLikesPostRequest(TypedDict):
    group_id: NotRequired[str]
    """
    群号，短ID可不传
    """
    message_id: str
    """
    消息ID，可以传递长ID或短ID
    """
    emoji_id: str
    """
    表情ID
    """
    emoji_type: NotRequired[str]
    """
    表情类型
    """
    count: float
    """
    数量，0代表全部
    """


class Data4EmojiLikeListItem(TypedDict):
    user_id: str
    """
    点击者QQ号
    """
    nick_name: str
    """
    昵称?
    """


class GetEmojiLikesPostResponse(TypedDict):
    emoji_like_list: list[Data4EmojiLikeListItem]
    """
    表情回应列表
    """


class GetFilePostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径、URL或Base64
    """
    file_id: NotRequired[str]
    """
    文件ID
    """


class GetFilePostResponse(TypedDict):
    file: NotRequired[str]
    """
    本地路径
    """
    url: NotRequired[str]
    """
    下载URL
    """
    file_size: NotRequired[str]
    """
    文件大小
    """
    file_name: NotRequired[str]
    """
    文件名
    """
    base64: NotRequired[str]
    """
    Base64编码
    """


class SetQqProfilePostRequest(TypedDict):
    nickname: str
    """
    昵称
    """
    personal_note: NotRequired[str]
    """
    个性签名
    """
    sex: NotRequired[float | str]
    """
    性别 (0: 未知, 1: 男, 2: 女)
    """


type SetQqProfilePostResponse = dict[str, Any]


class ArkShareGroupPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type ArkShareGroupPostResponse = str


class ArkSharePeerPostRequest(TypedDict):
    user_id: NotRequired[str]
    """
    QQ号
    """
    group_id: NotRequired[str]
    """
    群号
    """
    phone_number: str
    """
    手机号
    """


type ArkSharePeerPostResponse = dict[str, Any]


class SendGroupArkSharePostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type SendGroupArkSharePostResponse = str


class SendArkSharePostRequest(TypedDict):
    user_id: NotRequired[str]
    """
    QQ号
    """
    group_id: NotRequired[str]
    """
    群号
    """
    phone_number: str
    """
    手机号
    """


type SendArkSharePostResponse = dict[str, Any]


class CreateCollectionPostRequest(TypedDict):
    rawData: str
    """
    原始数据
    """
    brief: str
    """
    简要描述
    """


type CreateCollectionPostResponse = dict[str, Any]


class SetSelfLongnickPostRequest(TypedDict):
    longNick: str
    """
    签名内容
    """


type SetSelfLongnickPostResponse = dict[str, Any]


class ForwardFriendSingleMsgPostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """
    group_id: NotRequired[str]
    """
    目标群号
    """
    user_id: NotRequired[str]
    """
    目标用户QQ
    """


type ForwardFriendSingleMsgPostResponse = None


class ForwardGroupSingleMsgPostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """
    group_id: NotRequired[str]
    """
    目标群号
    """
    user_id: NotRequired[str]
    """
    目标用户QQ
    """


type ForwardGroupSingleMsgPostResponse = None


class MarkGroupMsgAsReadPostRequest(TypedDict):
    user_id: NotRequired[str | float]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message_id: NotRequired[str]
    """
    消息ID
    """


type MarkGroupMsgAsReadPostResponse = None


class MarkPrivateMsgAsReadPostRequest(TypedDict):
    user_id: NotRequired[str | float]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message_id: NotRequired[str]
    """
    消息ID
    """


type MarkPrivateMsgAsReadPostResponse = None


class SetQqAvatarPostRequest(TypedDict):
    file: str
    """
    图片路径、URL或Base64
    """


type SetQqAvatarPostResponse = None


class TranslateEn2zhPostRequest(TypedDict):
    words: list[str]
    """
    待翻译单词列表
    """


class TranslateEn2zhPostResponse(TypedDict):
    words: list[str]
    """
    翻译结果列表
    """


class GetGroupRootFilesPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_count: float | str
    """
    文件数量
    """


class GetGroupRootFilesPostResponse(TypedDict):
    files: list[Any]
    """
    文件列表
    """
    folders: list[Any]
    """
    文件夹列表
    """


class SetGroupSignPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type SetGroupSignPostResponse = None


class SendGroupSignPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type SendGroupSignPostResponse = None


class GetClientkeyPostRequest(TypedDict):
    pass


class GetClientkeyPostResponse(TypedDict):
    clientkey: NotRequired[str]
    """
    客户端Key
    """


class MoveGroupFilePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_id: str
    """
    文件ID
    """
    current_parent_directory: str
    """
    当前父目录
    """
    target_parent_directory: str
    """
    目标父目录
    """


class MoveGroupFilePostResponse(TypedDict):
    ok: bool
    """
    是否成功
    """


class RenameGroupFilePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_id: str
    """
    文件ID
    """
    current_parent_directory: str
    """
    当前父目录
    """
    new_name: str
    """
    新文件名
    """


class RenameGroupFilePostResponse(TypedDict):
    ok: bool
    """
    是否成功
    """


class TransGroupFilePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_id: str
    """
    文件ID
    """


class TransGroupFilePostResponse(TypedDict):
    ok: bool
    """
    是否成功
    """


class SendLikePostRequest(TypedDict):
    user_id: str
    """
    对方 QQ 号
    """
    times: float | str
    """
    点赞次数
    """


type SendLikePostResponse = None


class GetMsgPostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """


class GetMsgPostResponse(TypedDict):
    time: float
    """
    发送时间
    """
    message_type: str
    """
    消息类型
    """
    message_id: float
    """
    消息ID
    """
    real_id: float
    """
    真实ID
    """
    message_seq: float
    """
    消息序号
    """
    sender: dict[str, Any]
    """
    发送者
    """
    message: dict[str, Any]
    """
    消息内容
    """
    raw_message: str
    """
    原始消息内容
    """
    font: float
    """
    字体
    """
    group_id: NotRequired[float | str]
    """
    群号
    """
    user_id: float | str
    """
    发送者QQ号
    """
    emoji_likes_list: NotRequired[list[Any]]
    """
    表情回应列表
    """


class GetLoginInfoPostRequest(TypedDict):
    pass


type GetLoginInfoPostResponse = OB11User


class GetFriendListPostRequest(TypedDict):
    no_cache: NotRequired[bool | str]
    """
    是否不使用缓存
    """


type GetFriendListPostResponse = list[OB11User]


class GetGroupListPostRequest(TypedDict):
    no_cache: NotRequired[bool | str]
    """
    是否不使用缓存
    """


type GetGroupListPostResponse = list[OB11Group]


class GetGroupInfoPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type GetGroupInfoPostResponse = OB11Group


class GetGroupMemberListPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    no_cache: NotRequired[bool | str]
    """
    是否不使用缓存
    """


type GetGroupMemberListPostResponse = list[Any]


class GetGroupMemberInfoPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    QQ号
    """
    no_cache: NotRequired[bool | str]
    """
    是否不使用缓存
    """


type GetGroupMemberInfoPostResponse = OB11GroupMember


class SendGroupMsgPostRequestNew(TypedDict):
    text: str


class SendGroupMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class SendPrivateMsgPostRequestNew(TypedDict):
    text: str


class SendPrivateMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class SendMsgPostRequestNew(TypedDict):
    text: str


class SendMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class DeleteMsgPostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """


type DeleteMsgPostResponse = None


class SetGroupAddRequestPostRequest(TypedDict):
    flag: str
    """
    请求flag
    """
    approve: NotRequired[bool | str]
    """
    是否同意
    """
    reason: NotRequired[str | None]
    """
    拒绝理由
    """
    count: NotRequired[float]
    """
    搜索通知数量
    """


type SetGroupAddRequestPostResponse = None


class SetFriendAddRequestPostRequest(TypedDict):
    flag: str
    """
    加好友请求的 flag (需从上报中获取)
    """
    approve: NotRequired[str | bool]
    """
    是否同意请求
    """
    remark: NotRequired[str]
    """
    添加后的好友备注
    """


type SetFriendAddRequestPostResponse = None


class SetGroupLeavePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    is_dismiss: NotRequired[bool | str]
    """
    是否解散
    """


type SetGroupLeavePostResponse = None


class GetVersionInfoPostRequest(TypedDict):
    pass


class GetVersionInfoPostResponse(TypedDict):
    app_name: str
    """
    应用名称
    """
    protocol_version: str
    """
    协议版本
    """
    app_version: str
    """
    应用版本
    """


class CanSendRecordPostRequest(TypedDict):
    pass


class CanSendRecordPostResponse(TypedDict):
    yes: bool
    """
    是否可以发送
    """


class CanSendImagePostRequest(TypedDict):
    pass


class CanSendImagePostResponse(TypedDict):
    yes: bool
    """
    是否可以发送
    """


class GetStatusPostRequest(TypedDict):
    pass


class GetStatusPostResponse(TypedDict):
    online: bool
    """
    是否在线
    """
    good: bool
    """
    状态是否良好
    """
    stat: dict[str, Any]
    """
    统计信息
    """


class SetGroupWholeBanPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    enable: NotRequired[bool | str]
    """
    是否开启全员禁言
    """


type SetGroupWholeBanPostResponse = None


class SetGroupBanPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    duration: float | str
    """
    禁言时长(秒)
    """


type SetGroupBanPostResponse = None


class SetGroupKickPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    reject_add_request: NotRequired[bool | str]
    """
    是否拒绝加群请求
    """


type SetGroupKickPostResponse = None


class SetGroupAdminPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    enable: NotRequired[bool | str]
    """
    是否设置为管理员
    """


type SetGroupAdminPostResponse = None


class SetGroupNamePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    group_name: str
    """
    群名称
    """


type SetGroupNamePostResponse = None


class SetGroupCardPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    card: NotRequired[str]
    """
    群名片
    """


type SetGroupCardPostResponse = None


class GetImagePostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径、URL或Base64
    """
    file_id: NotRequired[str]
    """
    文件ID
    """


class GetImagePostResponse(TypedDict):
    file: NotRequired[str]
    """
    本地路径
    """
    url: NotRequired[str]
    """
    下载URL
    """
    file_size: NotRequired[str]
    """
    文件大小
    """
    file_name: NotRequired[str]
    """
    文件名
    """
    base64: NotRequired[str]
    """
    Base64编码
    """


class GetRecordPostRequest(TypedDict):
    file: NotRequired[str]
    """
    文件路径、URL或Base64
    """
    file_id: NotRequired[str]
    """
    文件ID
    """
    out_format: str
    """
    输出格式
    """


class GetRecordPostResponse(TypedDict):
    file: NotRequired[str]
    """
    本地路径
    """
    url: NotRequired[str]
    """
    下载URL
    """
    file_size: NotRequired[str]
    """
    文件大小
    """
    file_name: NotRequired[str]
    """
    文件名
    """
    base64: NotRequired[str]
    """
    Base64编码
    """


class SetMsgEmojiLikePostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """
    emoji_id: float | str
    """
    表情ID
    """
    set: NotRequired[bool | str]
    """
    是否设置
    """


type SetMsgEmojiLikePostResponse = dict[str, Any]


class GetCookiesPostRequest(TypedDict):
    domain: str
    """
    需要获取 cookies 的域名
    """


class GetCookiesPostResponse(TypedDict):
    cookies: str
    """
    Cookies
    """
    bkn: str
    """
    CSRF Token
    """


class SetOnlineStatusPostRequest(TypedDict):
    status: float | str
    """
    在线状态
    """
    ext_status: float | str
    """
    扩展状态
    """
    battery_status: float | str
    """
    电量状态
    """


type SetOnlineStatusPostResponse = None


class GetRobotUinRangePostRequest(TypedDict):
    pass


type GetRobotUinRangePostResponse = list[Any]


class GetFriendsWithCategoryPostRequest(TypedDict):
    pass


class Datum1(TypedDict):
    categoryId: float
    """
    分组ID
    """
    categoryName: str
    """
    分组名称
    """
    categoryMbCount: float
    """
    分组内好友数量
    """
    buddyList: list[OB11User]
    """
    好友列表
    """


type GetFriendsWithCategoryPostResponse = list[Datum1]


class DeleteFriendPostRequest(TypedDict):
    friend_id: NotRequired[str | float]
    """
    好友 QQ 号
    """
    user_id: NotRequired[str | float]
    """
    用户 QQ 号
    """
    temp_block: NotRequired[bool]
    """
    是否加入黑名单
    """
    temp_both_del: NotRequired[bool]
    """
    是否双向删除
    """


type DeleteFriendPostResponse = Any


class CheckUrlSafelyPostRequest(TypedDict):
    url: str
    """
    要检查的 URL
    """


class CheckUrlSafelyPostResponse(TypedDict):
    level: float
    """
    安全等级 (1: 安全, 2: 未知, 3: 危险)
    """


class GetOnlineClientsPostRequest(TypedDict):
    """
    在线客户端负载
    """


type GetOnlineClientsPostResponse = list[Any]


class OcrImagePostRequest(TypedDict):
    image: str
    """
    图片路径、URL或Base64
    """


type OcrImagePostResponse = dict[str, Any]


class FieldOcrImagePostRequest(TypedDict):
    image: str
    """
    图片路径、URL或Base64
    """


type FieldOcrImagePostResponse = dict[str, Any]


class GetGroupHonorInfoPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    type: NotRequired[
        Literal["all", "talkative", "performer", "legend", "strong_newbie", "emotion"]
    ]
    """
    荣誉类型
    """


class GetGroupHonorInfoPostResponse(TypedDict):
    group_id: float
    """
    群号
    """
    current_talkative: dict[str, Any]
    """
    当前龙王
    """
    talkative_list: list[Any]
    """
    龙王列表
    """
    performer_list: list[Any]
    """
    群聊之火列表
    """
    legend_list: list[Any]
    """
    群聊炽热列表
    """
    emotion_list: list[Any]
    """
    快乐源泉列表
    """
    strong_newbie_list: list[Any]
    """
    冒尖小春笋列表
    """


class FieldSendGroupNoticePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    content: str
    """
    公告内容
    """
    image: NotRequired[str]
    """
    公告图片路径或 URL
    """
    pinned: float | str
    """
    是否置顶 (0/1)
    """
    type: float | str
    """
    类型 (默认为 1)
    """
    confirm_required: float | str
    """
    是否需要确认 (0/1)
    """
    is_show_edit_card: float | str
    """
    是否显示修改群名片引导 (0/1)
    """
    tip_window_type: float | str
    """
    弹窗类型 (默认为 0)
    """


type FieldSendGroupNoticePostResponse = None


class FieldGetGroupNoticePostRequest(TypedDict):
    group_id: str
    """
    群号
    """


class Datum2Message(TypedDict):
    """
    公告内容
    """

    text: str
    """
    文本内容
    """
    image: list[Any]
    """
    图片列表
    """
    images: list[Any]
    """
    图片列表
    """


class Datum2(TypedDict):
    sender_id: float
    """
    发送者QQ
    """
    publish_time: float
    """
    发布时间
    """
    notice_id: str
    """
    公告ID
    """
    message: Datum2Message
    """
    公告内容
    """
    settings: NotRequired[dict[str, Any]]
    """
    设置项
    """
    read_num: NotRequired[float]
    """
    阅读数
    """


type FieldGetGroupNoticePostResponse = list[Datum2]


class GetEssenceMsgListPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


class Datum3(TypedDict):
    msg_seq: float
    """
    消息序号
    """
    msg_random: float
    """
    消息随机数
    """
    sender_id: float
    """
    发送者QQ
    """
    sender_nick: str
    """
    发送者昵称
    """
    operator_id: float
    """
    操作者QQ
    """
    operator_nick: str
    """
    操作者昵称
    """
    message_id: float
    """
    消息ID
    """
    operator_time: float
    """
    操作时间
    """
    content: list[Any]
    """
    消息内容
    """


type GetEssenceMsgListPostResponse = list[Datum3]


class GetGroupAtAllRemainPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


class GetGroupAtAllRemainPostResponse(TypedDict):
    can_at_all: bool
    """
    是否可以艾特全体
    """
    remain_at_all_count_for_group: float
    """
    群艾特全体剩余次数
    """
    remain_at_all_count_for_uin: float
    """
    个人艾特全体剩余次数
    """


class SendForwardMsgPostRequestNew(TypedDict):
    text: str


class SendForwardMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class SendGroupForwardMsgPostRequestNew(TypedDict):
    text: str


class SendGroupForwardMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class SendPrivateForwardMsgPostRequestNew(TypedDict):
    text: str


class SendPrivateForwardMsgPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """
    res_id: NotRequired[str]
    """
    转发消息的 res_id
    """
    forward_id: NotRequired[str]
    """
    转发消息的 forward_id
    """


class GetStrangerInfoPostRequest(TypedDict):
    user_id: str
    """
    用户QQ
    """
    no_cache: bool | str
    """
    是否不使用缓存
    """


class GetStrangerInfoPostResponse(TypedDict):
    user_id: float
    """
    用户QQ
    """
    uid: str
    """
    UID
    """
    nickname: str
    """
    昵称
    """
    age: float
    """
    年龄
    """
    qid: str
    """
    QID
    """
    qqLevel: float
    """
    QQ等级
    """
    sex: str
    """
    性别
    """
    long_nick: str
    """
    个性签名
    """
    reg_time: float
    """
    注册时间
    """
    is_vip: bool
    """
    是否VIP
    """
    is_years_vip: bool
    """
    是否年费VIP
    """
    vip_level: float
    """
    VIP等级
    """
    remark: str
    """
    备注
    """
    status: float
    """
    状态
    """
    login_days: float
    """
    登录天数
    """


class DownloadFilePostRequest(TypedDict):
    url: NotRequired[str]
    """
    下载链接
    """
    base64: NotRequired[str]
    """
    base64数据
    """
    name: NotRequired[str]
    """
    文件名
    """
    headers: NotRequired[str | list[str]]
    """
    请求头
    """


class DownloadFilePostResponse(TypedDict):
    file: str
    """
    文件路径
    """


class GetGuildListPostRequest(TypedDict):
    pass


type GetGuildListPostResponse = None


class MarkMsgAsReadPostRequest(TypedDict):
    user_id: NotRequired[str | float]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message_id: NotRequired[str]
    """
    消息ID
    """


type MarkMsgAsReadPostResponse = None


class UploadGroupFilePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file: str
    """
    资源路径或URL
    """
    name: str
    """
    文件名
    """
    folder: NotRequired[str]
    """
    父目录 ID
    """
    folder_id: NotRequired[str]
    """
    父目录 ID (兼容性字段)
    """
    upload_file: bool
    """
    是否执行上传
    """


class UploadGroupFilePostResponse(TypedDict):
    file_id: str | None
    """
    文件 ID
    """


class GetGroupMsgHistoryPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    message_seq: NotRequired[str]
    """
    起始消息序号
    """
    count: float
    """
    获取消息数量
    """
    reverse_order: bool
    """
    是否反向排序
    """
    disable_get_url: bool
    """
    是否禁用获取URL
    """
    parse_mult_msg: bool
    """
    是否解析合并消息
    """
    quick_reply: bool
    """
    是否快速回复
    """
    reverseOrder: bool
    """
    是否反向排序(旧版本兼容)
    """


class GetGroupMsgHistoryPostResponse(TypedDict):
    messages: list[Any]
    """
    消息列表
    """


class GetForwardMsgPostRequest(TypedDict):
    message_id: NotRequired[str]
    """
    消息ID
    """
    id: NotRequired[str]
    """
    消息ID
    """


class GetForwardMsgPostResponse(TypedDict):
    messages: NotRequired[list[Any]]
    """
    消息列表
    """


class GetFriendMsgHistoryPostRequest(TypedDict):
    user_id: str
    """
    用户QQ
    """
    message_seq: NotRequired[str]
    """
    起始消息序号
    """
    count: float
    """
    获取消息数量
    """
    reverse_order: bool
    """
    是否反向排序
    """
    disable_get_url: bool
    """
    是否禁用获取URL
    """
    parse_mult_msg: bool
    """
    是否解析合并消息
    """
    quick_reply: bool
    """
    是否快速回复
    """
    reverseOrder: bool
    """
    是否反向排序(旧版本兼容)
    """


class GetFriendMsgHistoryPostResponse(TypedDict):
    messages: list[Any]
    """
    消息列表
    """


class FieldHandleQuickOperationPostRequestContextSender(TypedDict):
    user_id: str
    """
    用户ID
    """
    nickname: str
    """
    昵称
    """
    sex: NotRequired[str]
    """
    性别
    """
    age: NotRequired[float]
    """
    年龄
    """
    card: NotRequired[str]
    """
    群名片
    """
    level: NotRequired[str]
    """
    群等级
    """
    role: NotRequired[str]
    """
    群角色
    """


class FieldHandleQuickOperationPostRequestContext(TypedDict):
    """
    事件上下文
    """

    time: float
    """
    事件发生时间
    """
    self_id: float
    """
    收到事件的机器人 QQ 号
    """
    post_type: str
    """
    上报类型
    """
    message_type: NotRequired[str]
    """
    消息类型
    """
    sub_type: NotRequired[str]
    """
    消息子类型
    """
    user_id: str
    """
    发送者 QQ 号
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message_id: NotRequired[float]
    """
    消息 ID
    """
    message_seq: NotRequired[float]
    """
    消息序列号
    """
    real_id: NotRequired[float]
    """
    真实消息 ID
    """
    sender: NotRequired[FieldHandleQuickOperationPostRequestContextSender]
    message: NotRequired[dict[str, Any]]
    """
    消息内容
    """
    message_format: NotRequired[str]
    """
    消息格式
    """
    raw_message: NotRequired[str]
    """
    原始消息内容
    """
    font: NotRequired[float]
    """
    字体
    """
    notice_type: NotRequired[str]
    """
    通知类型
    """
    meta_event_type: NotRequired[str]
    """
    元事件类型
    """


class FieldHandleQuickOperationPostRequestOperation(TypedDict):
    """
    快速操作内容
    """

    reply: NotRequired[str]
    """
    回复内容
    """
    auto_escape: NotRequired[bool]
    """
    是否作为纯文本发送
    """
    at_sender: NotRequired[bool]
    """
    是否 @ 发送者
    """
    delete: NotRequired[bool]
    """
    是否撤回该消息
    """
    kick: NotRequired[bool]
    """
    是否踢出发送者
    """
    ban: NotRequired[bool]
    """
    是否禁言发送者
    """
    ban_duration: NotRequired[float]
    """
    禁言时长
    """
    approve: NotRequired[bool]
    """
    是否同意请求/加群
    """
    remark: NotRequired[str]
    """
    好友备注
    """
    reason: NotRequired[str]
    """
    拒绝理由
    """


class FieldHandleQuickOperationPostRequest(TypedDict):
    context: FieldHandleQuickOperationPostRequestContext
    """
    事件上下文
    """
    operation: FieldHandleQuickOperationPostRequestOperation
    """
    快速操作内容
    """


type FieldHandleQuickOperationPostResponse = None


class GetGroupIgnoredNotifiesPostRequest(TypedDict):
    """
    群忽略通知负载
    """


class GetGroupIgnoredNotifiesPostResponse(TypedDict):
    invited_requests: list[Any]
    """
    邀请请求列表
    """
    InvitedRequest: list[Any]
    """
    邀请请求列表
    """
    join_requests: list[Any]
    """
    加入请求列表
    """


class DeleteEssenceMsgPostRequest(TypedDict):
    message_id: NotRequired[float | str]
    """
    消息ID
    """
    msg_seq: NotRequired[str]
    """
    消息序号
    """
    msg_random: NotRequired[str]
    """
    消息随机数
    """
    group_id: NotRequired[str]
    """
    群号
    """


type DeleteEssenceMsgPostResponse = dict[str, Any]


class SetEssenceMsgPostRequest(TypedDict):
    message_id: float | str
    """
    消息ID
    """


type SetEssenceMsgPostResponse = dict[str, Any]


class GetRecentContactPostRequest(TypedDict):
    count: float | str
    """
    获取的数量
    """


class Datum4(TypedDict):
    lastestMsg: dict[str, Any]
    """
    最后一条消息
    """
    peerUin: str
    """
    对象QQ
    """
    remark: str
    """
    备注
    """
    msgTime: str
    """
    消息时间
    """
    chatType: float
    """
    聊天类型
    """
    msgId: str
    """
    消息ID
    """
    sendNickName: str
    """
    发送者昵称
    """
    sendMemberName: str
    """
    发送者群名片
    """
    peerName: str
    """
    对象名称
    """


type GetRecentContactPostResponse = list[Datum4]


class FieldMarkAllAsReadPostRequest(TypedDict):
    pass


type FieldMarkAllAsReadPostResponse = EmptyData | None


class GetProfileLikePostRequest(TypedDict):
    user_id: NotRequired[str]
    """
    QQ号
    """
    start: float | str
    """
    起始位置
    """
    count: float | str
    """
    获取数量
    """


class Data36FavoriteInfo(TypedDict):
    userInfos: list[Any]
    """
    点赞用户信息
    """
    total_count: float
    """
    总点赞数
    """
    last_time: float
    """
    最后点赞时间
    """
    today_count: float
    """
    今日点赞数
    """


class Data36VoteInfo(TypedDict):
    total_count: float
    """
    总点赞数
    """
    new_count: float
    """
    新增点赞数
    """
    new_nearby_count: float
    """
    新增附近点赞数
    """
    last_visit_time: float
    """
    最后访问时间
    """
    userInfos: list[Any]
    """
    点赞用户信息
    """


class GetProfileLikePostResponse(TypedDict):
    uid: str
    """
    用户UID
    """
    time: str
    """
    时间
    """
    favoriteInfo: Data36FavoriteInfo
    voteInfo: Data36VoteInfo


class SetGroupPortraitPostRequest(TypedDict):
    file: str
    """
    头像文件路径或 URL
    """
    group_id: str
    """
    群号
    """


class SetGroupPortraitPostResponse(TypedDict):
    result: float
    errMsg: str


class FetchCustomFacePostRequest(TypedDict):
    count: float | str
    """
    获取数量
    """


type FetchCustomFacePostResponse = list[str]


class UploadPrivateFilePostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    file: str
    """
    资源路径或URL
    """
    name: str
    """
    文件名
    """
    upload_file: bool
    """
    是否执行上传
    """


class UploadPrivateFilePostResponse(TypedDict):
    file_id: str | None
    """
    文件 ID
    """


class GetGuildServiceProfilePostRequest(TypedDict):
    pass


type GetGuildServiceProfilePostResponse = None


class FieldGetModelShowPostRequest(TypedDict):
    model: NotRequired[str]
    """
    模型名称
    """


class Datum5Variants(TypedDict):
    model_show: str
    """
    显示名称
    """
    need_pay: bool
    """
    是否需要付费
    """


class Datum5(TypedDict):
    variants: Datum5Variants


type FieldGetModelShowPostResponse = list[Datum5]


class FieldSetModelShowPostRequest(TypedDict):
    pass


type FieldSetModelShowPostResponse = None


class SetInputStatusPostRequest(TypedDict):
    user_id: str
    """
    QQ号
    """
    event_type: float
    """
    事件类型
    """


type SetInputStatusPostResponse = dict[str, Any]


class GetCsrfTokenPostRequest(TypedDict):
    pass


class GetCsrfTokenPostResponse(TypedDict):
    token: float
    """
    CSRF Token
    """


class GetCredentialsPostRequest(TypedDict):
    domain: str
    """
    需要获取 cookies 的域名
    """


class GetCredentialsPostResponse(TypedDict):
    cookies: str
    """
    Cookies
    """
    token: float
    """
    CSRF Token
    """


class FieldDelGroupNoticePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    notice_id: str
    """
    公告ID
    """


type FieldDelGroupNoticePostResponse = dict[str, Any]


class DeleteGroupFilePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_id: str
    """
    文件ID
    """


type DeleteGroupFilePostResponse = dict[str, Any]


class CreateGroupFileFolderPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    folder_name: NotRequired[str]
    """
    文件夹名称
    """
    name: NotRequired[str]
    """
    文件夹名称
    """


class CreateGroupFileFolderPostResponse(TypedDict):
    result: dict[str, Any]
    """
    操作结果
    """
    groupItem: dict[str, Any]
    """
    群项信息
    """


class DeleteGroupFolderPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    folder_id: NotRequired[str]
    """
    文件夹ID
    """
    folder: NotRequired[str]
    """
    文件夹ID
    """


type DeleteGroupFolderPostResponse = dict[str, Any]


class GetGroupFileSystemInfoPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


class GetGroupFileSystemInfoPostResponse(TypedDict):
    file_count: float
    """
    文件总数
    """
    limit_count: float
    """
    文件上限
    """
    used_space: float
    """
    已使用空间
    """
    total_space: float
    """
    总空间
    """


class GetGroupFilesByFolderPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    folder_id: NotRequired[str]
    """
    文件夹ID
    """
    folder: NotRequired[str]
    """
    文件夹ID
    """
    file_count: float | str
    """
    文件数量
    """


class GetGroupFilesByFolderPostResponse(TypedDict):
    files: list[Any]
    """
    文件列表
    """
    folders: list[Any]
    """
    文件夹列表
    """


class NcGetPacketStatusPostRequest(TypedDict):
    pass


type NcGetPacketStatusPostResponse = None


class SetRestartPostRequest(TypedDict):
    pass


type SetRestartPostResponse = None


class GroupPokePostRequest(TypedDict):
    group_id: NotRequired[str]
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    target_id: NotRequired[str]
    """
    目标QQ
    """


type GroupPokePostResponse = None


class FriendPokePostRequest(TypedDict):
    group_id: NotRequired[str]
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    target_id: NotRequired[str]
    """
    目标QQ
    """


type FriendPokePostResponse = None


class NcGetUserStatusPostRequest(TypedDict):
    user_id: str
    """
    QQ号
    """


class NcGetUserStatusPostResponse(TypedDict):
    status: float
    """
    在线状态
    """
    ext_status: float
    """
    扩展状态
    """


class NcGetRkeyPostRequest(TypedDict):
    pass


type NcGetRkeyPostResponse = list[Any]


class SetGroupSpecialTitlePostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    user_id: str
    """
    QQ号
    """
    special_title: str
    """
    专属头衔
    """


type SetGroupSpecialTitlePostResponse = None


class SetDiyOnlineStatusPostRequest(TypedDict):
    face_id: float | str
    """
    图标ID
    """
    face_type: float | str
    """
    图标类型
    """
    wording: str
    """
    状态文字内容
    """


type SetDiyOnlineStatusPostResponse = str


class GetGroupShutListPostRequest(TypedDict):
    group_id: str
    """
    群号
    """


type GetGroupShutListPostResponse = list[Any]


class GetGroupFileUrlPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    file_id: str
    """
    文件ID
    """


class GetGroupFileUrlPostResponse(TypedDict):
    url: NotRequired[str]
    """
    文件下载链接
    """


class GetMiniAppArkPostRequestGetMiniAppArkPostRequest(TypedDict):
    """
    小程序Ark参数
    """

    type: Literal["bili", "weibo"]
    """
    模板类型
    """
    title: str
    """
    标题
    """
    desc: str
    """
    描述
    """
    picUrl: str
    """
    图片URL
    """
    jumpUrl: str
    """
    跳转URL
    """
    webUrl: NotRequired[str]
    """
    网页URL
    """
    rawArkData: NotRequired[str]
    """
    是否返回原始Ark数据
    """


class GetMiniAppArkPostRequestGetMiniAppArkPostRequest1(TypedDict):
    """
    小程序Ark参数
    """

    title: str
    """
    标题
    """
    desc: str
    """
    描述
    """
    picUrl: str
    """
    图片URL
    """
    jumpUrl: str
    """
    跳转URL
    """
    iconUrl: str
    """
    图标URL
    """
    webUrl: NotRequired[str]
    """
    网页URL
    """
    appId: str
    """
    小程序AppID
    """
    scene: str
    """
    场景ID
    """
    templateType: str
    """
    模板类型
    """
    businessType: str
    """
    业务类型
    """
    verType: str
    """
    版本类型
    """
    shareType: str
    """
    分享类型
    """
    versionId: str
    """
    版本ID
    """
    sdkId: str
    """
    SDK ID
    """
    withShareTicket: str
    """
    是否携带分享票据
    """
    rawArkData: NotRequired[str]
    """
    是否返回原始Ark数据
    """


type GetMiniAppArkPostRequest = (
    GetMiniAppArkPostRequestGetMiniAppArkPostRequest
    | GetMiniAppArkPostRequestGetMiniAppArkPostRequest1
)
"""
小程序Ark参数
"""


class GetMiniAppArkPostResponse(TypedDict):
    data: dict[str, Any]
    """
    Ark数据
    """


class GetAiRecordPostRequest(TypedDict):
    character: str
    """
    角色ID
    """
    group_id: str
    """
    群号
    """
    text: str
    """
    语音文本内容
    """


type GetAiRecordPostResponse = str


class SendGroupAiRecordPostRequest(TypedDict):
    character: str
    """
    角色ID
    """
    group_id: str
    """
    群号
    """
    text: str
    """
    语音文本内容
    """


class SendGroupAiRecordPostResponse(TypedDict):
    message_id: float
    """
    消息ID
    """


class GetAiCharactersPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    chat_type: float | str
    """
    聊天类型
    """


class Datum6Character(TypedDict):
    character_id: str
    """
    角色ID
    """
    character_name: str
    """
    角色名称
    """
    preview_url: str
    """
    预览URL
    """


class Datum6(TypedDict):
    type: str
    """
    角色类型
    """
    characters: list[Datum6Character]
    """
    角色列表
    """


type GetAiCharactersPostResponse = list[Datum6]


class SendPacketPostRequest(TypedDict):
    cmd: str
    """
    命令字
    """
    data: str
    """
    十六进制数据
    """
    rsp: str | bool
    """
    是否等待响应
    """


type SendPacketPostResponse = str | None


class SendPokePostRequest(TypedDict):
    group_id: NotRequired[str]
    """
    群号
    """
    user_id: str
    """
    用户QQ
    """
    target_id: NotRequired[str]
    """
    目标QQ
    """


type SendPokePostResponse = None


class GetGroupSystemMsgPostRequest(TypedDict):
    count: float | str
    """
    获取的消息数量
    """


class GetGroupSystemMsgPostResponse(TypedDict):
    invited_requests: list[OB11Notify]
    """
    进群邀请列表
    """
    InvitedRequest: list[OB11Notify]
    """
    进群邀请列表 (兼容)
    """
    join_requests: list[OB11Notify]
    """
    进群申请列表
    """


class BotExitPostRequest(TypedDict):
    pass


type BotExitPostResponse = dict[str, Any]


class ClickInlineKeyboardButtonPostRequest(TypedDict):
    group_id: str
    """
    群号
    """
    bot_appid: str
    """
    机器人AppID
    """
    button_id: str
    """
    按钮ID
    """
    callback_data: str
    """
    回调数据
    """
    msg_seq: str
    """
    消息序列号
    """


type ClickInlineKeyboardButtonPostResponse = dict[str, Any]


class GetPrivateFileUrlPostRequest(TypedDict):
    file_id: str
    """
    文件ID
    """


class GetPrivateFileUrlPostResponse(TypedDict):
    url: NotRequired[str]
    """
    文件下载链接
    """


class GetUnidirectionalFriendListPostRequest(TypedDict):
    pass


class Datum7(TypedDict):
    uin: float
    """
    QQ号
    """
    uid: str
    """
    用户UID
    """
    nick_name: str
    """
    昵称
    """
    age: float
    """
    年龄
    """
    source: str
    """
    来源
    """


type GetUnidirectionalFriendListPostResponse = list[Datum7]


class CleanCachePostRequest(TypedDict):
    pass


type CleanCachePostResponse = None


class GetGroupIgnoreAddRequestPostRequest(TypedDict):
    pass


class Datum8(TypedDict):
    request_id: float
    """
    请求ID
    """
    invitor_uin: float
    """
    邀请者QQ
    """
    invitor_nick: NotRequired[str]
    """
    邀请者昵称
    """
    group_id: float
    """
    群号
    """
    message: NotRequired[str]
    """
    验证信息
    """
    group_name: NotRequired[str]
    """
    群名称
    """
    checked: bool
    """
    是否已处理
    """
    actor: float
    """
    处理者QQ
    """
    requester_nick: NotRequired[str]
    """
    请求者昵称
    """


type GetGroupIgnoreAddRequestPostResponse = list[Datum8]


class GetCollectionListPostRequest(TypedDict):
    category: str
    """
    分类ID
    """
    count: str
    """
    获取数量
    """


type GetCollectionListPostResponse = dict[str, Any]


class CreateFlashTaskPostRequest(TypedDict):
    files: list[str] | str
    """
    文件列表或单个文件路径
    """
    name: NotRequired[str]
    """
    任务名称
    """
    thumb_path: NotRequired[str]
    """
    缩略图路径
    """


type CreateFlashTaskPostResponse = dict[str, Any]


class GetFlashFileListPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """


type GetFlashFileListPostResponse = dict[str, Any]


class GetFlashFileUrlPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """
    file_name: NotRequired[str]
    """
    文件名
    """
    file_index: NotRequired[float]
    """
    文件索引
    """


type GetFlashFileUrlPostResponse = dict[str, Any]


class SendFlashMsgPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """
    user_id: NotRequired[str]
    """
    用户 QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """


type SendFlashMsgPostResponse = dict[str, Any]


class GetShareLinkPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """


type GetShareLinkPostResponse = dict[str, Any]


class GetFilesetInfoPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """


type GetFilesetInfoPostResponse = dict[str, Any]


class GetOnlineFileMsgPostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """


type GetOnlineFileMsgPostResponse = dict[str, Any]


class SendOnlineFilePostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    file_path: str
    """
    本地文件路径
    """
    file_name: NotRequired[str]
    """
    文件名 (可选)
    """


type SendOnlineFilePostResponse = dict[str, Any]


class SendOnlineFolderPostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    folder_path: str
    """
    本地文件夹路径
    """
    folder_name: NotRequired[str]
    """
    文件夹名称 (可选)
    """


type SendOnlineFolderPostResponse = dict[str, Any]


class ReceiveOnlineFilePostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    msg_id: str
    """
    消息 ID
    """
    element_id: str
    """
    元素 ID
    """


type ReceiveOnlineFilePostResponse = dict[str, Any]


class RefuseOnlineFilePostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    msg_id: str
    """
    消息 ID
    """
    element_id: str
    """
    元素 ID
    """


type RefuseOnlineFilePostResponse = dict[str, Any]


class CancelOnlineFilePostRequest(TypedDict):
    user_id: str
    """
    用户 QQ
    """
    msg_id: str
    """
    消息 ID
    """


type CancelOnlineFilePostResponse = dict[str, Any]


class DownloadFilesetPostRequest(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """


type DownloadFilesetPostResponse = dict[str, Any]


class GetFilesetIdPostRequest(TypedDict):
    share_code: str
    """
    分享码或分享链接
    """


class GetFilesetIdPostResponse(TypedDict):
    fileset_id: str
    """
    文件集 ID
    """


"""
OneBot 11 消息段
"""


type OB11MessageMixType = list[Message] | str | Message
"""
OneBot 11 消息混合类型
"""


class OB11Message(TypedDict):
    """
    OneBot 11 完整消息对象
    """

    real_seq: NotRequired[str]
    """
    真实序列号
    """
    temp_source: NotRequired[float]
    """
    临时会话来源
    """
    message_sent_type: NotRequired[str]
    """
    消息发送类型
    """
    target_id: NotRequired[float]
    """
    目标ID
    """
    self_id: NotRequired[float]
    """
    机器人QQ号
    """
    time: float
    """
    消息时间戳
    """
    message_id: float
    """
    消息ID
    """
    message_seq: float
    """
    消息序列号
    """
    real_id: float
    """
    真实ID
    """
    user_id: float | str
    """
    发送者QQ号
    """
    group_id: NotRequired[float | str]
    """
    群号
    """
    group_name: NotRequired[str]
    """
    群名称
    """
    message_type: Literal["private", "group"]
    """
    消息类型
    """
    sub_type: NotRequired[Literal["friend", "group", "normal"]]
    """
    消息子类型
    """
    sender: OB11Sender
    message: list[Message] | str
    """
    消息内容
    """
    message_format: Literal["array", "string"]
    """
    消息格式
    """
    raw_message: str
    """
    原始消息
    """
    font: float
    """
    字体
    """
    post_type: NotRequired[str]
    """
    上报类型
    """
    raw: NotRequired[dict[str, Any]]
    """
    原始消息对象
    """
    emoji_likes_list: NotRequired[list[OB11MessageEmojiLikesListItem]]
    """
    表情点赞列表
    """


class OB11PostSendMsg(TypedDict):
    """
    OneBot 11 发送消息请求
    """

    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型
    """
    user_id: NotRequired[str]
    """
    用户QQ号
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    messages: NotRequired[OB11MessageMixType]
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    消息来源
    """
    news: NotRequired[list[OB11PostSendMsgNew]]
    summary: NotRequired[str]
    """
    摘要
    """
    prompt: NotRequired[str]
    """
    提示
    """
    time: NotRequired[str]
    """
    时间
    """


class OB11ActionMessage(OB11LatestMessage):
    """
    OneBot 11 消息信息
    """

    message_id: float
    """
    消息ID
    """
    message_seq: float
    """
    消息序列号
    """
    emoji_likes_list: list[EmojiLikesListItem]


class SendGroupMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendGroupMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """


class SendPrivateMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendPrivateMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """


class SendMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """


class SendForwardMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendForwardMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """


class SendGroupForwardMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendGroupForwardMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """


class SendPrivateForwardMsgPostRequest(TypedDict):
    message_type: NotRequired[Literal["private", "group"]]
    """
    消息类型 (private/group)
    """
    user_id: NotRequired[str]
    """
    用户QQ
    """
    group_id: NotRequired[str]
    """
    群号
    """
    message: OB11MessageMixType
    auto_escape: NotRequired[bool | str]
    """
    是否作为纯文本发送
    """
    source: NotRequired[str]
    """
    合并转发来源
    """
    news: NotRequired[list[SendPrivateForwardMsgPostRequestNew]]
    """
    合并转发新闻
    """
    summary: NotRequired[str]
    """
    合并转发摘要
    """
    prompt: NotRequired[str]
    """
    合并转发提示
    """
