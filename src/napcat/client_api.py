# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

from collections.abc import Mapping
from typing import Any, Unpack, Protocol
from .types.schemas import (
    ArkShareGroupPostRequest,
    ArkShareGroupPostResponse,
    ArkSharePeerPostRequest,
    ArkSharePeerPostResponse,
    BotExitPostRequest,
    BotExitPostResponse,
    CanSendImagePostRequest,
    CanSendImagePostResponse,
    CanSendRecordPostRequest,
    CanSendRecordPostResponse,
    CancelOnlineFilePostRequest,
    CancelOnlineFilePostResponse,
    CheckUrlSafelyPostRequest,
    CheckUrlSafelyPostResponse,
    CleanCachePostRequest,
    CleanCachePostResponse,
    CleanStreamTempFilePostRequest,
    CleanStreamTempFilePostResponse,
    ClickInlineKeyboardButtonPostRequest,
    ClickInlineKeyboardButtonPostResponse,
    CreateCollectionPostRequest,
    CreateCollectionPostResponse,
    CreateFlashTaskPostRequest,
    CreateFlashTaskPostResponse,
    CreateGroupFileFolderPostRequest,
    CreateGroupFileFolderPostResponse,
    DelGroupAlbumMediaPostRequest,
    DelGroupAlbumMediaPostResponse,
    DeleteEssenceMsgPostRequest,
    DeleteEssenceMsgPostResponse,
    DeleteFriendPostRequest,
    DeleteFriendPostResponse,
    DeleteGroupFilePostRequest,
    DeleteGroupFilePostResponse,
    DeleteGroupFolderPostRequest,
    DeleteGroupFolderPostResponse,
    DeleteMsgPostRequest,
    DeleteMsgPostResponse,
    DoGroupAlbumCommentPostRequest,
    DoGroupAlbumCommentPostResponse,
    DownloadFileImageStreamPostRequest,
    DownloadFileImageStreamPostResponse,
    DownloadFilePostRequest,
    DownloadFilePostResponse,
    DownloadFileRecordStreamPostRequest,
    DownloadFileRecordStreamPostResponse,
    DownloadFileStreamPostRequest,
    DownloadFileStreamPostResponse,
    DownloadFilesetPostRequest,
    DownloadFilesetPostResponse,
    FetchCustomFacePostRequest,
    FetchCustomFacePostResponse,
    FetchEmojiLikePostRequest,
    FetchEmojiLikePostResponse,
    FieldDelGroupNoticePostRequest,
    FieldDelGroupNoticePostResponse,
    FieldGetGroupNoticePostRequest,
    FieldGetGroupNoticePostResponse,
    FieldGetModelShowPostRequest,
    FieldGetModelShowPostResponse,
    FieldHandleQuickOperationPostRequest,
    FieldHandleQuickOperationPostResponse,
    FieldMarkAllAsReadPostRequest,
    FieldMarkAllAsReadPostResponse,
    FieldOcrImagePostRequest,
    FieldOcrImagePostResponse,
    FieldSendGroupNoticePostRequest,
    FieldSendGroupNoticePostResponse,
    FieldSetModelShowPostRequest,
    FieldSetModelShowPostResponse,
    ForwardFriendSingleMsgPostRequest,
    ForwardFriendSingleMsgPostResponse,
    ForwardGroupSingleMsgPostRequest,
    ForwardGroupSingleMsgPostResponse,
    FriendPokePostRequest,
    FriendPokePostResponse,
    GetAiCharactersPostRequest,
    GetAiCharactersPostResponse,
    GetAiRecordPostRequest,
    GetAiRecordPostResponse,
    GetClientkeyPostRequest,
    GetClientkeyPostResponse,
    GetCollectionListPostRequest,
    GetCollectionListPostResponse,
    GetCookiesPostRequest,
    GetCookiesPostResponse,
    GetCredentialsPostRequest,
    GetCredentialsPostResponse,
    GetCsrfTokenPostRequest,
    GetCsrfTokenPostResponse,
    GetDoubtFriendsAddRequestPostRequest,
    GetDoubtFriendsAddRequestPostResponse,
    GetEmojiLikesPostRequest,
    GetEmojiLikesPostResponse,
    GetEssenceMsgListPostRequest,
    GetEssenceMsgListPostResponse,
    GetFilePostRequest,
    GetFilePostResponse,
    GetFilesetIdPostRequest,
    GetFilesetIdPostResponse,
    GetFilesetInfoPostRequest,
    GetFilesetInfoPostResponse,
    GetFlashFileListPostRequest,
    GetFlashFileListPostResponse,
    GetFlashFileUrlPostRequest,
    GetFlashFileUrlPostResponse,
    GetForwardMsgPostRequest,
    GetForwardMsgPostResponse,
    GetFriendListPostRequest,
    GetFriendListPostResponse,
    GetFriendMsgHistoryPostRequest,
    GetFriendMsgHistoryPostResponse,
    GetFriendsWithCategoryPostRequest,
    GetFriendsWithCategoryPostResponse,
    GetGroupAlbumMediaListPostRequest,
    GetGroupAlbumMediaListPostResponse,
    GetGroupAtAllRemainPostRequest,
    GetGroupAtAllRemainPostResponse,
    GetGroupDetailInfoPostRequest,
    GetGroupDetailInfoPostResponse,
    GetGroupFileSystemInfoPostRequest,
    GetGroupFileSystemInfoPostResponse,
    GetGroupFileUrlPostRequest,
    GetGroupFileUrlPostResponse,
    GetGroupFilesByFolderPostRequest,
    GetGroupFilesByFolderPostResponse,
    GetGroupHonorInfoPostRequest,
    GetGroupHonorInfoPostResponse,
    GetGroupIgnoreAddRequestPostRequest,
    GetGroupIgnoreAddRequestPostResponse,
    GetGroupIgnoredNotifiesPostRequest,
    GetGroupIgnoredNotifiesPostResponse,
    GetGroupInfoExPostRequest,
    GetGroupInfoExPostResponse,
    GetGroupInfoPostRequest,
    GetGroupInfoPostResponse,
    GetGroupListPostRequest,
    GetGroupListPostResponse,
    GetGroupMemberInfoPostRequest,
    GetGroupMemberInfoPostResponse,
    GetGroupMemberListPostRequest,
    GetGroupMemberListPostResponse,
    GetGroupMsgHistoryPostRequest,
    GetGroupMsgHistoryPostResponse,
    GetGroupRootFilesPostRequest,
    GetGroupRootFilesPostResponse,
    GetGroupShutListPostRequest,
    GetGroupShutListPostResponse,
    GetGroupSystemMsgPostRequest,
    GetGroupSystemMsgPostResponse,
    GetGuildListPostRequest,
    GetGuildListPostResponse,
    GetGuildServiceProfilePostRequest,
    GetGuildServiceProfilePostResponse,
    GetImagePostRequest,
    GetImagePostResponse,
    GetLoginInfoPostRequest,
    GetLoginInfoPostResponse,
    GetMiniAppArkPostRequest,
    GetMiniAppArkPostResponse,
    GetMsgPostRequest,
    GetMsgPostResponse,
    GetOnlineClientsPostRequest,
    GetOnlineClientsPostResponse,
    GetOnlineFileMsgPostRequest,
    GetOnlineFileMsgPostResponse,
    GetPrivateFileUrlPostRequest,
    GetPrivateFileUrlPostResponse,
    GetProfileLikePostRequest,
    GetProfileLikePostResponse,
    GetQunAlbumListPostRequest,
    GetQunAlbumListPostResponse,
    GetRecentContactPostRequest,
    GetRecentContactPostResponse,
    GetRecordPostRequest,
    GetRecordPostResponse,
    GetRkeyPostRequest,
    GetRkeyPostResponse,
    GetRkeyServerPostRequest,
    GetRkeyServerPostResponse,
    GetRobotUinRangePostRequest,
    GetRobotUinRangePostResponse,
    GetShareLinkPostRequest,
    GetShareLinkPostResponse,
    GetStatusPostRequest,
    GetStatusPostResponse,
    GetStrangerInfoPostRequest,
    GetStrangerInfoPostResponse,
    GetUnidirectionalFriendListPostRequest,
    GetUnidirectionalFriendListPostResponse,
    GetVersionInfoPostRequest,
    GetVersionInfoPostResponse,
    GroupPokePostRequest,
    GroupPokePostResponse,
    MarkGroupMsgAsReadPostRequest,
    MarkGroupMsgAsReadPostResponse,
    MarkMsgAsReadPostRequest,
    MarkMsgAsReadPostResponse,
    MarkPrivateMsgAsReadPostRequest,
    MarkPrivateMsgAsReadPostResponse,
    MoveGroupFilePostRequest,
    MoveGroupFilePostResponse,
    NcGetPacketStatusPostRequest,
    NcGetPacketStatusPostResponse,
    NcGetRkeyPostRequest,
    NcGetRkeyPostResponse,
    NcGetUserStatusPostRequest,
    NcGetUserStatusPostResponse,
    OcrImagePostRequest,
    OcrImagePostResponse,
    ReceiveOnlineFilePostRequest,
    ReceiveOnlineFilePostResponse,
    RefuseOnlineFilePostRequest,
    RefuseOnlineFilePostResponse,
    RenameGroupFilePostRequest,
    RenameGroupFilePostResponse,
    SendArkSharePostRequest,
    SendArkSharePostResponse,
    SendFlashMsgPostRequest,
    SendFlashMsgPostResponse,
    SendForwardMsgPostRequest,
    SendForwardMsgPostResponse,
    SendGroupAiRecordPostRequest,
    SendGroupAiRecordPostResponse,
    SendGroupArkSharePostRequest,
    SendGroupArkSharePostResponse,
    SendGroupForwardMsgPostRequest,
    SendGroupForwardMsgPostResponse,
    SendGroupMsgPostRequest,
    SendGroupMsgPostResponse,
    SendGroupSignPostRequest,
    SendGroupSignPostResponse,
    SendLikePostRequest,
    SendLikePostResponse,
    SendMsgPostRequest,
    SendMsgPostResponse,
    SendOnlineFilePostRequest,
    SendOnlineFilePostResponse,
    SendOnlineFolderPostRequest,
    SendOnlineFolderPostResponse,
    SendPacketPostRequest,
    SendPacketPostResponse,
    SendPokePostRequest,
    SendPokePostResponse,
    SendPrivateForwardMsgPostRequest,
    SendPrivateForwardMsgPostResponse,
    SendPrivateMsgPostRequest,
    SendPrivateMsgPostResponse,
    SetDiyOnlineStatusPostRequest,
    SetDiyOnlineStatusPostResponse,
    SetDoubtFriendsAddRequestPostRequest,
    SetDoubtFriendsAddRequestPostResponse,
    SetEssenceMsgPostRequest,
    SetEssenceMsgPostResponse,
    SetFriendAddRequestPostRequest,
    SetFriendAddRequestPostResponse,
    SetFriendRemarkPostRequest,
    SetFriendRemarkPostResponse,
    SetGroupAddOptionPostRequest,
    SetGroupAddOptionPostResponse,
    SetGroupAddRequestPostRequest,
    SetGroupAddRequestPostResponse,
    SetGroupAdminPostRequest,
    SetGroupAdminPostResponse,
    SetGroupAlbumMediaLikePostRequest,
    SetGroupAlbumMediaLikePostResponse,
    SetGroupBanPostRequest,
    SetGroupBanPostResponse,
    SetGroupCardPostRequest,
    SetGroupCardPostResponse,
    SetGroupKickMembersPostRequest,
    SetGroupKickMembersPostResponse,
    SetGroupKickPostRequest,
    SetGroupKickPostResponse,
    SetGroupLeavePostRequest,
    SetGroupLeavePostResponse,
    SetGroupNamePostRequest,
    SetGroupNamePostResponse,
    SetGroupPortraitPostRequest,
    SetGroupPortraitPostResponse,
    SetGroupRemarkPostRequest,
    SetGroupRemarkPostResponse,
    SetGroupRobotAddOptionPostRequest,
    SetGroupRobotAddOptionPostResponse,
    SetGroupSearchPostRequest,
    SetGroupSearchPostResponse,
    SetGroupSignPostRequest,
    SetGroupSignPostResponse,
    SetGroupSpecialTitlePostRequest,
    SetGroupSpecialTitlePostResponse,
    SetGroupTodoPostRequest,
    SetGroupTodoPostResponse,
    SetGroupWholeBanPostRequest,
    SetGroupWholeBanPostResponse,
    SetInputStatusPostRequest,
    SetInputStatusPostResponse,
    SetMsgEmojiLikePostRequest,
    SetMsgEmojiLikePostResponse,
    SetOnlineStatusPostRequest,
    SetOnlineStatusPostResponse,
    SetQqAvatarPostRequest,
    SetQqAvatarPostResponse,
    SetQqProfilePostRequest,
    SetQqProfilePostResponse,
    SetRestartPostRequest,
    SetRestartPostResponse,
    SetSelfLongnickPostRequest,
    SetSelfLongnickPostResponse,
    TestDownloadStreamPostRequest,
    TestDownloadStreamPostResponse,
    TransGroupFilePostRequest,
    TransGroupFilePostResponse,
    TranslateEn2zhPostRequest,
    TranslateEn2zhPostResponse,
    UploadFileStreamPostRequest,
    UploadFileStreamPostResponse,
    UploadGroupFilePostRequest,
    UploadGroupFilePostResponse,
    UploadImageToQunAlbumPostRequest,
    UploadImageToQunAlbumPostResponse,
    UploadPrivateFilePostRequest,
    UploadPrivateFilePostResponse,
)


# 定义一个 Protocol，避免循环导入 Client 类，同时保证类型提示
class CallActionProtocol(Protocol):
    async def call_action(
        self, action: str, params: Mapping[str, Any] | None = None
    ) -> Any: ...


class NapCatAPI:
    """
    NapCat API 命名空间。
    所有自动生成的方法都挂载于此，通过 client.api.xxx 调用。
    """

    def __init__(self, client: CallActionProtocol):
        self._client = client

    async def clean_stream_temp_file(
        self, **kwargs: Unpack[CleanStreamTempFilePostRequest]
    ) -> CleanStreamTempFilePostResponse:
        """
        清理流式传输临时文件

        标签: 流式传输扩展
        """
        return await self._client.call_action("clean_stream_temp_file", kwargs)

    async def download_file_stream(
        self, **kwargs: Unpack[DownloadFileStreamPostRequest]
    ) -> DownloadFileStreamPostResponse:
        """
        下载文件流

        标签: 流式接口
        """
        return await self._client.call_action("download_file_stream", kwargs)

    async def download_file_record_stream(
        self, **kwargs: Unpack[DownloadFileRecordStreamPostRequest]
    ) -> DownloadFileRecordStreamPostResponse:
        """
        下载语音文件流

        标签: 流式传输扩展
        """
        return await self._client.call_action("download_file_record_stream", kwargs)

    async def download_file_image_stream(
        self, **kwargs: Unpack[DownloadFileImageStreamPostRequest]
    ) -> DownloadFileImageStreamPostResponse:
        """
        下载图片文件流

        标签: 流式传输扩展
        """
        return await self._client.call_action("download_file_image_stream", kwargs)

    async def test_download_stream(
        self, **kwargs: Unpack[TestDownloadStreamPostRequest]
    ) -> TestDownloadStreamPostResponse:
        """
        测试下载流

        标签: 流式传输扩展
        """
        return await self._client.call_action("test_download_stream", kwargs)

    async def upload_file_stream(
        self, **kwargs: Unpack[UploadFileStreamPostRequest]
    ) -> UploadFileStreamPostResponse:
        """
        上传文件流

        标签: 流式接口
        """
        return await self._client.call_action("upload_file_stream", kwargs)

    async def del_group_album_media(
        self, **kwargs: Unpack[DelGroupAlbumMediaPostRequest]
    ) -> DelGroupAlbumMediaPostResponse:
        """
        删除群相册媒体

        标签: 群组扩展
        """
        return await self._client.call_action("del_group_album_media", kwargs)

    async def set_group_album_media_like(
        self, **kwargs: Unpack[SetGroupAlbumMediaLikePostRequest]
    ) -> SetGroupAlbumMediaLikePostResponse:
        """
        点赞群相册媒体

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_album_media_like", kwargs)

    async def do_group_album_comment(
        self, **kwargs: Unpack[DoGroupAlbumCommentPostRequest]
    ) -> DoGroupAlbumCommentPostResponse:
        """
        发表群相册评论

        标签: 群组扩展
        """
        return await self._client.call_action("do_group_album_comment", kwargs)

    async def get_group_album_media_list(
        self, **kwargs: Unpack[GetGroupAlbumMediaListPostRequest]
    ) -> GetGroupAlbumMediaListPostResponse:
        """
        获取群相册媒体列表

        标签: 群组扩展
        """
        return await self._client.call_action("get_group_album_media_list", kwargs)

    async def get_qun_album_list(
        self, **kwargs: Unpack[GetQunAlbumListPostRequest]
    ) -> GetQunAlbumListPostResponse:
        """
        获取群相册列表

        标签: 群组扩展
        """
        return await self._client.call_action("get_qun_album_list", kwargs)

    async def upload_image_to_qun_album(
        self, **kwargs: Unpack[UploadImageToQunAlbumPostRequest]
    ) -> UploadImageToQunAlbumPostResponse:
        """
        上传图片到群相册

        标签: 群组扩展
        """
        return await self._client.call_action("upload_image_to_qun_album", kwargs)

    async def set_group_todo(
        self, **kwargs: Unpack[SetGroupTodoPostRequest]
    ) -> SetGroupTodoPostResponse:
        """
        设置群待办

        标签: 核心接口
        """
        return await self._client.call_action("set_group_todo", kwargs)

    async def get_group_detail_info(
        self, **kwargs: Unpack[GetGroupDetailInfoPostRequest]
    ) -> GetGroupDetailInfoPostResponse:
        """
        获取群详细信息

        标签: 群组接口
        """
        return await self._client.call_action("get_group_detail_info", kwargs)

    async def set_group_kick_members(
        self, **kwargs: Unpack[SetGroupKickMembersPostRequest]
    ) -> SetGroupKickMembersPostResponse:
        """
        批量踢出群成员

        标签: 扩展接口
        """
        return await self._client.call_action("set_group_kick_members", kwargs)

    async def set_group_add_option(
        self, **kwargs: Unpack[SetGroupAddOptionPostRequest]
    ) -> SetGroupAddOptionPostResponse:
        """
        设置群加群选项

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_add_option", kwargs)

    async def set_group_robot_add_option(
        self, **kwargs: Unpack[SetGroupRobotAddOptionPostRequest]
    ) -> SetGroupRobotAddOptionPostResponse:
        """
        设置群机器人加群选项

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_robot_add_option", kwargs)

    async def set_group_search(
        self, **kwargs: Unpack[SetGroupSearchPostRequest]
    ) -> SetGroupSearchPostResponse:
        """
        设置群搜索选项

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_search", kwargs)

    async def set_doubt_friends_add_request(
        self, **kwargs: Unpack[SetDoubtFriendsAddRequestPostRequest]
    ) -> SetDoubtFriendsAddRequestPostResponse:
        """
        处理可疑好友申请

        标签: 系统接口
        """
        return await self._client.call_action("set_doubt_friends_add_request", kwargs)

    async def get_doubt_friends_add_request(
        self, **kwargs: Unpack[GetDoubtFriendsAddRequestPostRequest]
    ) -> GetDoubtFriendsAddRequestPostResponse:
        """
        获取可疑好友申请

        标签: 系统接口
        """
        return await self._client.call_action("get_doubt_friends_add_request", kwargs)

    async def set_friend_remark(
        self, **kwargs: Unpack[SetFriendRemarkPostRequest]
    ) -> SetFriendRemarkPostResponse:
        """
        设置好友备注

        标签: 用户接口
        """
        return await self._client.call_action("set_friend_remark", kwargs)

    async def get_rkey(
        self, **kwargs: Unpack[GetRkeyPostRequest]
    ) -> GetRkeyPostResponse:
        """
        获取扩展 RKey

        标签: 系统扩展
        """
        return await self._client.call_action("get_rkey", kwargs)

    async def get_rkey_server(
        self, **kwargs: Unpack[GetRkeyServerPostRequest]
    ) -> GetRkeyServerPostResponse:
        """
        获取 RKey 服务器

        标签: 系统扩展
        """
        return await self._client.call_action("get_rkey_server", kwargs)

    async def set_group_remark(
        self, **kwargs: Unpack[SetGroupRemarkPostRequest]
    ) -> SetGroupRemarkPostResponse:
        """
        设置群备注

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_remark", kwargs)

    async def get_group_info_ex(
        self, **kwargs: Unpack[GetGroupInfoExPostRequest]
    ) -> GetGroupInfoExPostResponse:
        """
        获取群详细信息 (扩展)

        标签: 群组扩展
        """
        return await self._client.call_action("get_group_info_ex", kwargs)

    async def fetch_emoji_like(
        self, **kwargs: Unpack[FetchEmojiLikePostRequest]
    ) -> FetchEmojiLikePostResponse:
        """
        获取表情点赞详情

        标签: 消息扩展
        """
        return await self._client.call_action("fetch_emoji_like", kwargs)

    async def get_emoji_likes(
        self, **kwargs: Unpack[GetEmojiLikesPostRequest]
    ) -> GetEmojiLikesPostResponse:
        """
        获取消息表情点赞列表

        标签: 消息扩展
        """
        return await self._client.call_action("get_emoji_likes", kwargs)

    async def get_file(
        self, **kwargs: Unpack[GetFilePostRequest]
    ) -> GetFilePostResponse:
        """
        获取文件

        标签: 文件接口
        """
        return await self._client.call_action("get_file", kwargs)

    async def set_qq_profile(
        self, **kwargs: Unpack[SetQqProfilePostRequest]
    ) -> SetQqProfilePostResponse:
        """
        设置QQ资料

        标签: Go-CQHTTP
        """
        return await self._client.call_action("set_qq_profile", kwargs)

    async def ArkShareGroup(
        self, **kwargs: Unpack[ArkShareGroupPostRequest]
    ) -> ArkShareGroupPostResponse:
        """
        分享群 (Ark)

        标签: 消息扩展
        """
        return await self._client.call_action("ArkShareGroup", kwargs)

    async def ArkSharePeer(
        self, **kwargs: Unpack[ArkSharePeerPostRequest]
    ) -> ArkSharePeerPostResponse:
        """
        分享用户 (Ark)

        标签: 消息扩展
        """
        return await self._client.call_action("ArkSharePeer", kwargs)

    async def send_group_ark_share(
        self, **kwargs: Unpack[SendGroupArkSharePostRequest]
    ) -> SendGroupArkSharePostResponse:
        """
        分享群 (Ark)

        标签: 消息扩展
        """
        return await self._client.call_action("send_group_ark_share", kwargs)

    async def send_ark_share(
        self, **kwargs: Unpack[SendArkSharePostRequest]
    ) -> SendArkSharePostResponse:
        """
        分享用户 (Ark)

        标签: 消息扩展
        """
        return await self._client.call_action("send_ark_share", kwargs)

    async def create_collection(
        self, **kwargs: Unpack[CreateCollectionPostRequest]
    ) -> CreateCollectionPostResponse:
        """
        创建收藏

        标签: 扩展接口
        """
        return await self._client.call_action("create_collection", kwargs)

    async def set_self_longnick(
        self, **kwargs: Unpack[SetSelfLongnickPostRequest]
    ) -> SetSelfLongnickPostResponse:
        """
        设置个性签名

        标签: 扩展接口
        """
        return await self._client.call_action("set_self_longnick", kwargs)

    async def forward_friend_single_msg(
        self, **kwargs: Unpack[ForwardFriendSingleMsgPostRequest]
    ) -> ForwardFriendSingleMsgPostResponse:
        """
        转发单条消息

        标签: 消息接口
        """
        return await self._client.call_action("forward_friend_single_msg", kwargs)

    async def forward_group_single_msg(
        self, **kwargs: Unpack[ForwardGroupSingleMsgPostRequest]
    ) -> ForwardGroupSingleMsgPostResponse:
        """
        转发单条消息

        标签: 消息接口
        """
        return await self._client.call_action("forward_group_single_msg", kwargs)

    async def mark_group_msg_as_read(
        self, **kwargs: Unpack[MarkGroupMsgAsReadPostRequest]
    ) -> MarkGroupMsgAsReadPostResponse:
        """
        标记群聊已读

        标签: 消息接口
        """
        return await self._client.call_action("mark_group_msg_as_read", kwargs)

    async def mark_private_msg_as_read(
        self, **kwargs: Unpack[MarkPrivateMsgAsReadPostRequest]
    ) -> MarkPrivateMsgAsReadPostResponse:
        """
        标记私聊已读

        标签: 消息接口
        """
        return await self._client.call_action("mark_private_msg_as_read", kwargs)

    async def set_qq_avatar(
        self, **kwargs: Unpack[SetQqAvatarPostRequest]
    ) -> SetQqAvatarPostResponse:
        """
        设置QQ头像

        标签: 扩展接口
        """
        return await self._client.call_action("set_qq_avatar", kwargs)

    async def translate_en2zh(
        self, **kwargs: Unpack[TranslateEn2zhPostRequest]
    ) -> TranslateEn2zhPostResponse:
        """
        英文单词翻译

        标签: 扩展接口
        """
        return await self._client.call_action("translate_en2zh", kwargs)

    async def get_group_root_files(
        self, **kwargs: Unpack[GetGroupRootFilesPostRequest]
    ) -> GetGroupRootFilesPostResponse:
        """
        获取群根目录文件列表

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_root_files", kwargs)

    async def set_group_sign(
        self, **kwargs: Unpack[SetGroupSignPostRequest]
    ) -> SetGroupSignPostResponse:
        """
        群打卡

        标签: 群组扩展
        """
        return await self._client.call_action("set_group_sign", kwargs)

    async def send_group_sign(
        self, **kwargs: Unpack[SendGroupSignPostRequest]
    ) -> SendGroupSignPostResponse:
        """
        群打卡

        标签: 群组扩展
        """
        return await self._client.call_action("send_group_sign", kwargs)

    async def get_clientkey(
        self, **kwargs: Unpack[GetClientkeyPostRequest]
    ) -> GetClientkeyPostResponse:
        """
        获取ClientKey

        标签: 扩展接口
        """
        return await self._client.call_action("get_clientkey", kwargs)

    async def move_group_file(
        self, **kwargs: Unpack[MoveGroupFilePostRequest]
    ) -> MoveGroupFilePostResponse:
        """
        移动群文件

        标签: 文件扩展
        """
        return await self._client.call_action("move_group_file", kwargs)

    async def rename_group_file(
        self, **kwargs: Unpack[RenameGroupFilePostRequest]
    ) -> RenameGroupFilePostResponse:
        """
        重命名群文件

        标签: 文件扩展
        """
        return await self._client.call_action("rename_group_file", kwargs)

    async def trans_group_file(
        self, **kwargs: Unpack[TransGroupFilePostRequest]
    ) -> TransGroupFilePostResponse:
        """
        传输群文件

        标签: 文件扩展
        """
        return await self._client.call_action("trans_group_file", kwargs)

    async def send_like(
        self, **kwargs: Unpack[SendLikePostRequest]
    ) -> SendLikePostResponse:
        """
        点赞

        标签: 用户接口
        """
        return await self._client.call_action("send_like", kwargs)

    async def get_msg(self, **kwargs: Unpack[GetMsgPostRequest]) -> GetMsgPostResponse:
        """
        获取消息

        标签: 消息接口
        """
        return await self._client.call_action("get_msg", kwargs)

    async def get_login_info(
        self, **kwargs: Unpack[GetLoginInfoPostRequest]
    ) -> GetLoginInfoPostResponse:
        """
        获取登录号信息

        标签: 系统接口
        """
        return await self._client.call_action("get_login_info", kwargs)

    async def get_friend_list(
        self, **kwargs: Unpack[GetFriendListPostRequest]
    ) -> GetFriendListPostResponse:
        """
        获取好友列表

        标签: 用户接口
        """
        return await self._client.call_action("get_friend_list", kwargs)

    async def get_group_list(
        self, **kwargs: Unpack[GetGroupListPostRequest]
    ) -> GetGroupListPostResponse:
        """
        获取群列表

        标签: 群组接口
        """
        return await self._client.call_action("get_group_list", kwargs)

    async def get_group_info(
        self, **kwargs: Unpack[GetGroupInfoPostRequest]
    ) -> GetGroupInfoPostResponse:
        """
        获取群信息

        标签: 群组接口
        """
        return await self._client.call_action("get_group_info", kwargs)

    async def get_group_member_list(
        self, **kwargs: Unpack[GetGroupMemberListPostRequest]
    ) -> GetGroupMemberListPostResponse:
        """
        获取群成员列表

        标签: 群组接口
        """
        return await self._client.call_action("get_group_member_list", kwargs)

    async def get_group_member_info(
        self, **kwargs: Unpack[GetGroupMemberInfoPostRequest]
    ) -> GetGroupMemberInfoPostResponse:
        """
        获取群成员信息

        标签: 群组接口
        """
        return await self._client.call_action("get_group_member_info", kwargs)

    async def send_group_msg(
        self, **kwargs: Unpack[SendGroupMsgPostRequest]
    ) -> SendGroupMsgPostResponse:
        """
        发送群消息

        标签: 群组接口
        """
        return await self._client.call_action("send_group_msg", kwargs)

    async def send_private_msg(
        self, **kwargs: Unpack[SendPrivateMsgPostRequest]
    ) -> SendPrivateMsgPostResponse:
        """
        发送私聊消息

        标签: 消息接口
        """
        return await self._client.call_action("send_private_msg", kwargs)

    async def send_msg(
        self, **kwargs: Unpack[SendMsgPostRequest]
    ) -> SendMsgPostResponse:
        """
        发送消息

        标签: 消息接口
        """
        return await self._client.call_action("send_msg", kwargs)

    async def delete_msg(
        self, **kwargs: Unpack[DeleteMsgPostRequest]
    ) -> DeleteMsgPostResponse:
        """
        撤回消息

        标签: 消息接口
        """
        return await self._client.call_action("delete_msg", kwargs)

    async def set_group_add_request(
        self, **kwargs: Unpack[SetGroupAddRequestPostRequest]
    ) -> SetGroupAddRequestPostResponse:
        """
        处理加群请求

        标签: 群组接口
        """
        return await self._client.call_action("set_group_add_request", kwargs)

    async def set_friend_add_request(
        self, **kwargs: Unpack[SetFriendAddRequestPostRequest]
    ) -> SetFriendAddRequestPostResponse:
        """
        处理加好友请求

        标签: 用户接口
        """
        return await self._client.call_action("set_friend_add_request", kwargs)

    async def set_group_leave(
        self, **kwargs: Unpack[SetGroupLeavePostRequest]
    ) -> SetGroupLeavePostResponse:
        """
        退出群组

        标签: 群组接口
        """
        return await self._client.call_action("set_group_leave", kwargs)

    async def get_version_info(
        self, **kwargs: Unpack[GetVersionInfoPostRequest]
    ) -> GetVersionInfoPostResponse:
        """
        获取版本信息

        标签: 系统接口
        """
        return await self._client.call_action("get_version_info", kwargs)

    async def can_send_record(
        self, **kwargs: Unpack[CanSendRecordPostRequest]
    ) -> CanSendRecordPostResponse:
        """
        是否可以发送语音

        标签: 系统接口
        """
        return await self._client.call_action("can_send_record", kwargs)

    async def can_send_image(
        self, **kwargs: Unpack[CanSendImagePostRequest]
    ) -> CanSendImagePostResponse:
        """
        是否可以发送图片

        标签: 系统接口
        """
        return await self._client.call_action("can_send_image", kwargs)

    async def get_status(
        self, **kwargs: Unpack[GetStatusPostRequest]
    ) -> GetStatusPostResponse:
        """
        获取运行状态

        标签: 系统接口
        """
        return await self._client.call_action("get_status", kwargs)

    async def set_group_whole_ban(
        self, **kwargs: Unpack[SetGroupWholeBanPostRequest]
    ) -> SetGroupWholeBanPostResponse:
        """
        全员禁言

        标签: 群组接口
        """
        return await self._client.call_action("set_group_whole_ban", kwargs)

    async def set_group_ban(
        self, **kwargs: Unpack[SetGroupBanPostRequest]
    ) -> SetGroupBanPostResponse:
        """
        群组禁言

        标签: 群组接口
        """
        return await self._client.call_action("set_group_ban", kwargs)

    async def set_group_kick(
        self, **kwargs: Unpack[SetGroupKickPostRequest]
    ) -> SetGroupKickPostResponse:
        """
        群组踢人

        标签: 群组接口
        """
        return await self._client.call_action("set_group_kick", kwargs)

    async def set_group_admin(
        self, **kwargs: Unpack[SetGroupAdminPostRequest]
    ) -> SetGroupAdminPostResponse:
        """
        设置群管理员

        标签: 群组接口
        """
        return await self._client.call_action("set_group_admin", kwargs)

    async def set_group_name(
        self, **kwargs: Unpack[SetGroupNamePostRequest]
    ) -> SetGroupNamePostResponse:
        """
        设置群名称

        标签: 群组接口
        """
        return await self._client.call_action("set_group_name", kwargs)

    async def set_group_card(
        self, **kwargs: Unpack[SetGroupCardPostRequest]
    ) -> SetGroupCardPostResponse:
        """
        设置群名片

        标签: 群组接口
        """
        return await self._client.call_action("set_group_card", kwargs)

    async def get_image(
        self, **kwargs: Unpack[GetImagePostRequest]
    ) -> GetImagePostResponse:
        """
        获取图片

        标签: 文件接口
        """
        return await self._client.call_action("get_image", kwargs)

    async def get_record(
        self, **kwargs: Unpack[GetRecordPostRequest]
    ) -> GetRecordPostResponse:
        """
        获取语音

        标签: 文件接口
        """
        return await self._client.call_action("get_record", kwargs)

    async def set_msg_emoji_like(
        self, **kwargs: Unpack[SetMsgEmojiLikePostRequest]
    ) -> SetMsgEmojiLikePostResponse:
        """
        设置消息表情点赞

        标签: 消息扩展
        """
        return await self._client.call_action("set_msg_emoji_like", kwargs)

    async def get_cookies(
        self, **kwargs: Unpack[GetCookiesPostRequest]
    ) -> GetCookiesPostResponse:
        """
        获取 Cookies

        标签: 用户接口
        """
        return await self._client.call_action("get_cookies", kwargs)

    async def set_online_status(
        self, **kwargs: Unpack[SetOnlineStatusPostRequest]
    ) -> SetOnlineStatusPostResponse:
        """
        设置在线状态

        标签: 系统扩展
        """
        return await self._client.call_action("set_online_status", kwargs)

    async def get_robot_uin_range(
        self, **kwargs: Unpack[GetRobotUinRangePostRequest]
    ) -> GetRobotUinRangePostResponse:
        """
        获取机器人 UIN 范围

        标签: 系统扩展
        """
        return await self._client.call_action("get_robot_uin_range", kwargs)

    async def get_friends_with_category(
        self, **kwargs: Unpack[GetFriendsWithCategoryPostRequest]
    ) -> GetFriendsWithCategoryPostResponse:
        """
        获取带分组的好友列表

        标签: 用户扩展
        """
        return await self._client.call_action("get_friends_with_category", kwargs)

    async def delete_friend(
        self, **kwargs: Unpack[DeleteFriendPostRequest]
    ) -> DeleteFriendPostResponse:
        """
        删除好友

        标签: Go-CQHTTP
        """
        return await self._client.call_action("delete_friend", kwargs)

    async def check_url_safely(
        self, **kwargs: Unpack[CheckUrlSafelyPostRequest]
    ) -> CheckUrlSafelyPostResponse:
        """
        检查URL安全性

        标签: Go-CQHTTP
        """
        return await self._client.call_action("check_url_safely", kwargs)

    async def get_online_clients(
        self, **kwargs: Unpack[GetOnlineClientsPostRequest]
    ) -> GetOnlineClientsPostResponse:
        """
        获取在线客户端

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_online_clients", kwargs)

    async def ocr_image(
        self, **kwargs: Unpack[OcrImagePostRequest]
    ) -> OcrImagePostResponse:
        """
        图片 OCR 识别

        标签: 扩展接口
        """
        return await self._client.call_action("ocr_image", kwargs)

    async def dot_ocr_image(
        self, **kwargs: Unpack[FieldOcrImagePostRequest]
    ) -> FieldOcrImagePostResponse:
        """
        图片 OCR 识别 (内部)

        标签: 扩展接口
        """
        return await self._client.call_action(".ocr_image", kwargs)

    async def get_group_honor_info(
        self, **kwargs: Unpack[GetGroupHonorInfoPostRequest]
    ) -> GetGroupHonorInfoPostResponse:
        """
        获取群荣誉信息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_honor_info", kwargs)

    async def _send_group_notice(
        self, **kwargs: Unpack[FieldSendGroupNoticePostRequest]
    ) -> FieldSendGroupNoticePostResponse:
        """
        发送群公告

        标签: Go-CQHTTP
        """
        return await self._client.call_action("_send_group_notice", kwargs)

    async def _get_group_notice(
        self, **kwargs: Unpack[FieldGetGroupNoticePostRequest]
    ) -> FieldGetGroupNoticePostResponse:
        """
        获取群公告

        标签: 群组接口
        """
        return await self._client.call_action("_get_group_notice", kwargs)

    async def get_essence_msg_list(
        self, **kwargs: Unpack[GetEssenceMsgListPostRequest]
    ) -> GetEssenceMsgListPostResponse:
        """
        获取群精华消息

        标签: 群组接口
        """
        return await self._client.call_action("get_essence_msg_list", kwargs)

    async def get_group_at_all_remain(
        self, **kwargs: Unpack[GetGroupAtAllRemainPostRequest]
    ) -> GetGroupAtAllRemainPostResponse:
        """
        获取群艾特全体剩余次数

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_at_all_remain", kwargs)

    async def send_forward_msg(
        self, **kwargs: Unpack[SendForwardMsgPostRequest]
    ) -> SendForwardMsgPostResponse:
        """
        发送合并转发消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("send_forward_msg", kwargs)

    async def send_group_forward_msg(
        self, **kwargs: Unpack[SendGroupForwardMsgPostRequest]
    ) -> SendGroupForwardMsgPostResponse:
        """
        发送群合并转发消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("send_group_forward_msg", kwargs)

    async def send_private_forward_msg(
        self, **kwargs: Unpack[SendPrivateForwardMsgPostRequest]
    ) -> SendPrivateForwardMsgPostResponse:
        """
        发送私聊合并转发消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("send_private_forward_msg", kwargs)

    async def get_stranger_info(
        self, **kwargs: Unpack[GetStrangerInfoPostRequest]
    ) -> GetStrangerInfoPostResponse:
        """
        获取陌生人信息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_stranger_info", kwargs)

    async def download_file(
        self, **kwargs: Unpack[DownloadFilePostRequest]
    ) -> DownloadFilePostResponse:
        """
        下载文件

        标签: Go-CQHTTP
        """
        return await self._client.call_action("download_file", kwargs)

    async def get_guild_list(
        self, **kwargs: Unpack[GetGuildListPostRequest]
    ) -> GetGuildListPostResponse:
        """
        获取频道列表

        标签: 频道接口
        """
        return await self._client.call_action("get_guild_list", kwargs)

    async def mark_msg_as_read(
        self, **kwargs: Unpack[MarkMsgAsReadPostRequest]
    ) -> MarkMsgAsReadPostResponse:
        """
        标记消息已读 (Go-CQHTTP)

        标签: 消息接口
        """
        return await self._client.call_action("mark_msg_as_read", kwargs)

    async def upload_group_file(
        self, **kwargs: Unpack[UploadGroupFilePostRequest]
    ) -> UploadGroupFilePostResponse:
        """
        上传群文件

        标签: Go-CQHTTP
        """
        return await self._client.call_action("upload_group_file", kwargs)

    async def get_group_msg_history(
        self, **kwargs: Unpack[GetGroupMsgHistoryPostRequest]
    ) -> GetGroupMsgHistoryPostResponse:
        """
        获取群历史消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_msg_history", kwargs)

    async def get_forward_msg(
        self, **kwargs: Unpack[GetForwardMsgPostRequest]
    ) -> GetForwardMsgPostResponse:
        """
        获取合并转发消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_forward_msg", kwargs)

    async def get_friend_msg_history(
        self, **kwargs: Unpack[GetFriendMsgHistoryPostRequest]
    ) -> GetFriendMsgHistoryPostResponse:
        """
        获取好友历史消息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_friend_msg_history", kwargs)

    async def dot_handle_quick_operation(
        self, **kwargs: Unpack[FieldHandleQuickOperationPostRequest]
    ) -> FieldHandleQuickOperationPostResponse:
        """
        处理快速操作

        标签: Go-CQHTTP
        """
        return await self._client.call_action(".handle_quick_operation", kwargs)

    async def get_group_ignored_notifies(
        self, **kwargs: Unpack[GetGroupIgnoredNotifiesPostRequest]
    ) -> GetGroupIgnoredNotifiesPostResponse:
        """
        获取群忽略通知

        标签: 群组接口
        """
        return await self._client.call_action("get_group_ignored_notifies", kwargs)

    async def delete_essence_msg(
        self, **kwargs: Unpack[DeleteEssenceMsgPostRequest]
    ) -> DeleteEssenceMsgPostResponse:
        """
        移出精华消息

        标签: 群组接口
        """
        return await self._client.call_action("delete_essence_msg", kwargs)

    async def set_essence_msg(
        self, **kwargs: Unpack[SetEssenceMsgPostRequest]
    ) -> SetEssenceMsgPostResponse:
        """
        设置精华消息

        标签: 群组接口
        """
        return await self._client.call_action("set_essence_msg", kwargs)

    async def get_recent_contact(
        self, **kwargs: Unpack[GetRecentContactPostRequest]
    ) -> GetRecentContactPostResponse:
        """
        获取最近会话

        标签: 用户接口
        """
        return await self._client.call_action("get_recent_contact", kwargs)

    async def _mark_all_as_read(
        self, **kwargs: Unpack[FieldMarkAllAsReadPostRequest]
    ) -> FieldMarkAllAsReadPostResponse:
        """
        标记所有消息已读

        标签: 消息接口
        """
        return await self._client.call_action("_mark_all_as_read", kwargs)

    async def get_profile_like(
        self, **kwargs: Unpack[GetProfileLikePostRequest]
    ) -> GetProfileLikePostResponse:
        """
        获取资料点赞

        标签: 用户扩展
        """
        return await self._client.call_action("get_profile_like", kwargs)

    async def set_group_portrait(
        self, **kwargs: Unpack[SetGroupPortraitPostRequest]
    ) -> SetGroupPortraitPostResponse:
        """
        设置群头像

        标签: Go-CQHTTP
        """
        return await self._client.call_action("set_group_portrait", kwargs)

    async def fetch_custom_face(
        self, **kwargs: Unpack[FetchCustomFacePostRequest]
    ) -> FetchCustomFacePostResponse:
        """
        获取自定义表情

        标签: 系统扩展
        """
        return await self._client.call_action("fetch_custom_face", kwargs)

    async def upload_private_file(
        self, **kwargs: Unpack[UploadPrivateFilePostRequest]
    ) -> UploadPrivateFilePostResponse:
        """
        上传私聊文件

        标签: Go-CQHTTP
        """
        return await self._client.call_action("upload_private_file", kwargs)

    async def get_guild_service_profile(
        self, **kwargs: Unpack[GetGuildServiceProfilePostRequest]
    ) -> GetGuildServiceProfilePostResponse:
        """
        获取频道个人信息

        标签: 频道接口
        """
        return await self._client.call_action("get_guild_service_profile", kwargs)

    async def _get_model_show(
        self, **kwargs: Unpack[FieldGetModelShowPostRequest]
    ) -> FieldGetModelShowPostResponse:
        """
        获取机型显示

        标签: Go-CQHTTP
        """
        return await self._client.call_action("_get_model_show", kwargs)

    async def _set_model_show(
        self, **kwargs: Unpack[FieldSetModelShowPostRequest]
    ) -> FieldSetModelShowPostResponse:
        """
        设置机型

        标签: Go-CQHTTP
        """
        return await self._client.call_action("_set_model_show", kwargs)

    async def set_input_status(
        self, **kwargs: Unpack[SetInputStatusPostRequest]
    ) -> SetInputStatusPostResponse:
        """
        设置输入状态

        标签: 系统扩展
        """
        return await self._client.call_action("set_input_status", kwargs)

    async def get_csrf_token(
        self, **kwargs: Unpack[GetCsrfTokenPostRequest]
    ) -> GetCsrfTokenPostResponse:
        """
        获取 CSRF Token

        标签: 系统接口
        """
        return await self._client.call_action("get_csrf_token", kwargs)

    async def get_credentials(
        self, **kwargs: Unpack[GetCredentialsPostRequest]
    ) -> GetCredentialsPostResponse:
        """
        获取登录凭证

        标签: 系统接口
        """
        return await self._client.call_action("get_credentials", kwargs)

    async def _del_group_notice(
        self, **kwargs: Unpack[FieldDelGroupNoticePostRequest]
    ) -> FieldDelGroupNoticePostResponse:
        """
        删除群公告

        标签: 群组接口
        """
        return await self._client.call_action("_del_group_notice", kwargs)

    async def delete_group_file(
        self, **kwargs: Unpack[DeleteGroupFilePostRequest]
    ) -> DeleteGroupFilePostResponse:
        """
        删除群文件

        标签: Go-CQHTTP
        """
        return await self._client.call_action("delete_group_file", kwargs)

    async def create_group_file_folder(
        self, **kwargs: Unpack[CreateGroupFileFolderPostRequest]
    ) -> CreateGroupFileFolderPostResponse:
        """
        创建群文件目录

        标签: Go-CQHTTP
        """
        return await self._client.call_action("create_group_file_folder", kwargs)

    async def delete_group_folder(
        self, **kwargs: Unpack[DeleteGroupFolderPostRequest]
    ) -> DeleteGroupFolderPostResponse:
        """
        删除群文件目录

        标签: Go-CQHTTP
        """
        return await self._client.call_action("delete_group_folder", kwargs)

    async def get_group_file_system_info(
        self, **kwargs: Unpack[GetGroupFileSystemInfoPostRequest]
    ) -> GetGroupFileSystemInfoPostResponse:
        """
        获取群文件系统信息

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_file_system_info", kwargs)

    async def get_group_files_by_folder(
        self, **kwargs: Unpack[GetGroupFilesByFolderPostRequest]
    ) -> GetGroupFilesByFolderPostResponse:
        """
        获取群文件夹文件列表

        标签: Go-CQHTTP
        """
        return await self._client.call_action("get_group_files_by_folder", kwargs)

    async def nc_get_packet_status(
        self, **kwargs: Unpack[NcGetPacketStatusPostRequest]
    ) -> NcGetPacketStatusPostResponse:
        """
        获取Packet状态

        标签: 系统接口
        """
        return await self._client.call_action("nc_get_packet_status", kwargs)

    async def set_restart(
        self, **kwargs: Unpack[SetRestartPostRequest]
    ) -> SetRestartPostResponse:
        """
        重启服务

        标签: 系统接口
        """
        return await self._client.call_action("set_restart", kwargs)

    async def group_poke(
        self, **kwargs: Unpack[GroupPokePostRequest]
    ) -> GroupPokePostResponse:
        """
        发送戳一戳

        标签: 核心接口
        """
        return await self._client.call_action("group_poke", kwargs)

    async def friend_poke(
        self, **kwargs: Unpack[FriendPokePostRequest]
    ) -> FriendPokePostResponse:
        """
        发送戳一戳

        标签: 核心接口
        """
        return await self._client.call_action("friend_poke", kwargs)

    async def nc_get_user_status(
        self, **kwargs: Unpack[NcGetUserStatusPostRequest]
    ) -> NcGetUserStatusPostResponse:
        """
        获取用户在线状态

        标签: 系统扩展
        """
        return await self._client.call_action("nc_get_user_status", kwargs)

    async def nc_get_rkey(
        self, **kwargs: Unpack[NcGetRkeyPostRequest]
    ) -> NcGetRkeyPostResponse:
        """
        获取 RKey

        标签: 系统扩展
        """
        return await self._client.call_action("nc_get_rkey", kwargs)

    async def set_group_special_title(
        self, **kwargs: Unpack[SetGroupSpecialTitlePostRequest]
    ) -> SetGroupSpecialTitlePostResponse:
        """
        设置专属头衔

        标签: 扩展接口
        """
        return await self._client.call_action("set_group_special_title", kwargs)

    async def set_diy_online_status(
        self, **kwargs: Unpack[SetDiyOnlineStatusPostRequest]
    ) -> SetDiyOnlineStatusPostResponse:
        """
        设置自定义在线状态

        标签: 用户扩展
        """
        return await self._client.call_action("set_diy_online_status", kwargs)

    async def get_group_shut_list(
        self, **kwargs: Unpack[GetGroupShutListPostRequest]
    ) -> GetGroupShutListPostResponse:
        """
        获取群禁言列表

        标签: 群组接口
        """
        return await self._client.call_action("get_group_shut_list", kwargs)

    async def get_group_file_url(
        self, **kwargs: Unpack[GetGroupFileUrlPostRequest]
    ) -> GetGroupFileUrlPostResponse:
        """
        获取群文件URL

        标签: 文件接口
        """
        return await self._client.call_action("get_group_file_url", kwargs)

    async def get_mini_app_ark(
        self, payload: GetMiniAppArkPostRequest
    ) -> GetMiniAppArkPostResponse:
        """
        获取小程序 Ark

        标签: 系统扩展
        """
        return await self._client.call_action("get_mini_app_ark", payload)

    async def get_ai_record(
        self, **kwargs: Unpack[GetAiRecordPostRequest]
    ) -> GetAiRecordPostResponse:
        """
        获取 AI 语音

        标签: AI 扩展
        """
        return await self._client.call_action("get_ai_record", kwargs)

    async def send_group_ai_record(
        self, **kwargs: Unpack[SendGroupAiRecordPostRequest]
    ) -> SendGroupAiRecordPostResponse:
        """
        发送群 AI 语音

        标签: AI 扩展
        """
        return await self._client.call_action("send_group_ai_record", kwargs)

    async def get_ai_characters(
        self, **kwargs: Unpack[GetAiCharactersPostRequest]
    ) -> GetAiCharactersPostResponse:
        """
        获取AI角色列表

        标签: 扩展接口
        """
        return await self._client.call_action("get_ai_characters", kwargs)

    async def send_packet(
        self, **kwargs: Unpack[SendPacketPostRequest]
    ) -> SendPacketPostResponse:
        """
        发送原始数据包

        标签: 系统扩展
        """
        return await self._client.call_action("send_packet", kwargs)

    async def send_poke(
        self, **kwargs: Unpack[SendPokePostRequest]
    ) -> SendPokePostResponse:
        """
        发送戳一戳

        标签: 核心接口
        """
        return await self._client.call_action("send_poke", kwargs)

    async def get_group_system_msg(
        self, **kwargs: Unpack[GetGroupSystemMsgPostRequest]
    ) -> GetGroupSystemMsgPostResponse:
        """
        获取群系统消息

        标签: 系统接口
        """
        return await self._client.call_action("get_group_system_msg", kwargs)

    async def bot_exit(
        self, **kwargs: Unpack[BotExitPostRequest]
    ) -> BotExitPostResponse:
        """
        退出登录

        标签: 系统扩展
        """
        return await self._client.call_action("bot_exit", kwargs)

    async def click_inline_keyboard_button(
        self, **kwargs: Unpack[ClickInlineKeyboardButtonPostRequest]
    ) -> ClickInlineKeyboardButtonPostResponse:
        """
        点击内联键盘按钮

        标签: 消息扩展
        """
        return await self._client.call_action("click_inline_keyboard_button", kwargs)

    async def get_private_file_url(
        self, **kwargs: Unpack[GetPrivateFileUrlPostRequest]
    ) -> GetPrivateFileUrlPostResponse:
        """
        获取私聊文件URL

        标签: 文件接口
        """
        return await self._client.call_action("get_private_file_url", kwargs)

    async def get_unidirectional_friend_list(
        self, **kwargs: Unpack[GetUnidirectionalFriendListPostRequest]
    ) -> GetUnidirectionalFriendListPostResponse:
        """
        获取单向好友列表

        标签: 用户扩展
        """
        return await self._client.call_action("get_unidirectional_friend_list", kwargs)

    async def clean_cache(
        self, **kwargs: Unpack[CleanCachePostRequest]
    ) -> CleanCachePostResponse:
        """
        清理缓存

        标签: 系统接口
        """
        return await self._client.call_action("clean_cache", kwargs)

    async def get_group_ignore_add_request(
        self, **kwargs: Unpack[GetGroupIgnoreAddRequestPostRequest]
    ) -> GetGroupIgnoreAddRequestPostResponse:
        """
        获取群被忽略的加群请求

        标签: 群组接口
        """
        return await self._client.call_action("get_group_ignore_add_request", kwargs)

    async def get_collection_list(
        self, **kwargs: Unpack[GetCollectionListPostRequest]
    ) -> GetCollectionListPostResponse:
        """
        获取收藏列表

        标签: 系统扩展
        """
        return await self._client.call_action("get_collection_list", kwargs)

    async def create_flash_task(
        self, **kwargs: Unpack[CreateFlashTaskPostRequest]
    ) -> CreateFlashTaskPostResponse:
        """
        创建闪传任务

        标签: 文件扩展
        """
        return await self._client.call_action("create_flash_task", kwargs)

    async def get_flash_file_list(
        self, **kwargs: Unpack[GetFlashFileListPostRequest]
    ) -> GetFlashFileListPostResponse:
        """
        获取闪传文件列表

        标签: 文件扩展
        """
        return await self._client.call_action("get_flash_file_list", kwargs)

    async def get_flash_file_url(
        self, **kwargs: Unpack[GetFlashFileUrlPostRequest]
    ) -> GetFlashFileUrlPostResponse:
        """
        获取闪传文件链接

        标签: 文件扩展
        """
        return await self._client.call_action("get_flash_file_url", kwargs)

    async def send_flash_msg(
        self, **kwargs: Unpack[SendFlashMsgPostRequest]
    ) -> SendFlashMsgPostResponse:
        """
        发送闪传消息

        标签: 文件扩展
        """
        return await self._client.call_action("send_flash_msg", kwargs)

    async def get_share_link(
        self, **kwargs: Unpack[GetShareLinkPostRequest]
    ) -> GetShareLinkPostResponse:
        """
        获取文件分享链接

        标签: 文件扩展
        """
        return await self._client.call_action("get_share_link", kwargs)

    async def get_fileset_info(
        self, **kwargs: Unpack[GetFilesetInfoPostRequest]
    ) -> GetFilesetInfoPostResponse:
        """
        获取文件集信息

        标签: 文件扩展
        """
        return await self._client.call_action("get_fileset_info", kwargs)

    async def get_online_file_msg(
        self, **kwargs: Unpack[GetOnlineFileMsgPostRequest]
    ) -> GetOnlineFileMsgPostResponse:
        """
        获取在线文件消息

        标签: 文件扩展
        """
        return await self._client.call_action("get_online_file_msg", kwargs)

    async def send_online_file(
        self, **kwargs: Unpack[SendOnlineFilePostRequest]
    ) -> SendOnlineFilePostResponse:
        """
        发送在线文件

        标签: 文件扩展
        """
        return await self._client.call_action("send_online_file", kwargs)

    async def send_online_folder(
        self, **kwargs: Unpack[SendOnlineFolderPostRequest]
    ) -> SendOnlineFolderPostResponse:
        """
        发送在线文件夹

        标签: 文件扩展
        """
        return await self._client.call_action("send_online_folder", kwargs)

    async def receive_online_file(
        self, **kwargs: Unpack[ReceiveOnlineFilePostRequest]
    ) -> ReceiveOnlineFilePostResponse:
        """
        接收在线文件

        标签: 文件扩展
        """
        return await self._client.call_action("receive_online_file", kwargs)

    async def refuse_online_file(
        self, **kwargs: Unpack[RefuseOnlineFilePostRequest]
    ) -> RefuseOnlineFilePostResponse:
        """
        拒绝在线文件

        标签: 文件扩展
        """
        return await self._client.call_action("refuse_online_file", kwargs)

    async def cancel_online_file(
        self, **kwargs: Unpack[CancelOnlineFilePostRequest]
    ) -> CancelOnlineFilePostResponse:
        """
        取消在线文件

        标签: 文件扩展
        """
        return await self._client.call_action("cancel_online_file", kwargs)

    async def download_fileset(
        self, **kwargs: Unpack[DownloadFilesetPostRequest]
    ) -> DownloadFilesetPostResponse:
        """
        下载文件集

        标签: 文件扩展
        """
        return await self._client.call_action("download_fileset", kwargs)

    async def get_fileset_id(
        self, **kwargs: Unpack[GetFilesetIdPostRequest]
    ) -> GetFilesetIdPostResponse:
        """
        获取文件集 ID

        标签: 文件扩展
        """
        return await self._client.call_action("get_fileset_id", kwargs)
