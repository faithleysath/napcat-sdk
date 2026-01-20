# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

from collections.abc import Mapping
from typing import Any, Unpack, Protocol
from .types.schemas import (
   CleanStreamTempFilePostResponse,
   TestDownloadStreamPostRequest,
   TestDownloadStreamPostResponse,
   UploadFileStreamPostRequest,
   UploadFileStreamPostResponse,
   DownloadFileStreamPostRequest,
   DownloadFileStreamPostResponse,
   DownloadFileRecordStreamPostRequest,
   DownloadFileRecordStreamPostResponse,
   DownloadFileImageStreamPostRequest,
   DownloadFileImageStreamPostResponse,
   DelGroupAlbumMediaPostRequest,
   DelGroupAlbumMediaPostResponse,
   SetGroupAlbumMediaLikePostRequest,
   SetGroupAlbumMediaLikePostResponse,
   DoGroupAlbumCommentPostRequest,
   DoGroupAlbumCommentPostResponse,
   GetGroupAlbumMediaListPostRequest,
   GetGroupAlbumMediaListPostResponse,
   UploadImageToQunAlbumPostRequest,
   UploadImageToQunAlbumPostResponse,
   GetQunAlbumListPostRequest,
   GetQunAlbumListPostResponse,
   SetGroupTodoPostRequest,
   SetGroupTodoPostResponse,
   SetGroupKickMembersPostRequest,
   SetGroupKickMembersPostResponse,
   SetGroupRobotAddOptionPostRequest,
   SetGroupRobotAddOptionPostResponse,
   SetGroupAddOptionPostRequest,
   SetGroupAddOptionPostResponse,
   SetGroupSearchPostRequest,
   SetGroupSearchPostResponse,
   GetDoubtFriendsAddRequestPostRequest,
   GetDoubtFriendsAddRequestPostResponse,
   SetDoubtFriendsAddRequestPostRequest,
   SetDoubtFriendsAddRequestPostResponse,
   GetRkeyPostResponse,
   GetRkeyServerPostResponse,
   SetGroupRemarkPostRequest,
   SetGroupRemarkPostResponse,
   GetPrivateFileUrlPostRequest,
   GetPrivateFileUrlPostResponse,
   ClickInlineKeyboardButtonPostRequest,
   ClickInlineKeyboardButtonPostResponse,
   GetUnidirectionalFriendListPostResponse,
   SendPrivateMsgPostResponse,
   SendGroupMsgPostResponse,
   SendMsgPostResponse,
   DeleteMsgPostRequest,
   DeleteMsgPostResponse,
   GetMsgPostRequest,
   GetMsgPostResponse,
   GetForwardMsgPostRequest,
   GetForwardMsgPostResponse,
   SendLikePostRequest,
   SendLikePostResponse,
   SetGroupKickPostRequest,
   SetGroupKickPostResponse,
   SetGroupBanPostRequest,
   SetGroupBanPostResponse,
   SetGroupWholeBanPostRequest,
   SetGroupWholeBanPostResponse,
   SetGroupAdminPostRequest,
   SetGroupAdminPostResponse,
   SetGroupCardPostRequest,
   SetGroupCardPostResponse,
   SetGroupNamePostRequest,
   SetGroupNamePostResponse,
   SetGroupLeavePostRequest,
   SetGroupLeavePostResponse,
   SetGroupSpecialTitlePostRequest,
   SetGroupSpecialTitlePostResponse,
   SetFriendAddRequestPostRequest,
   SetFriendAddRequestPostResponse,
   SetFriendRemarkPostRequest,
   SetFriendRemarkPostResponse,
   SetGroupAddRequestPostRequest,
   SetGroupAddRequestPostResponse,
   GetLoginInfoPostResponse,
   GetStrangerInfoPostRequest,
   GetStrangerInfoPostResponse,
   GetFriendListPostRequest,
   GetFriendListPostResponse,
   GetGroupInfoPostRequest,
   GetGroupInfoPostResponse,
   GetGroupListPostRequest,
   GetGroupListPostResponse,
   GetGroupMemberInfoPostRequest,
   GetGroupMemberInfoPostResponse,
   GetGroupMemberListPostRequest,
   GetGroupMemberListPostResponse,
   GetGroupHonorInfoPostRequest,
   GetGroupHonorInfoPostResponse,
   GetCookiesPostRequest,
   GetCookiesPostResponse,
   GetCsrfTokenPostResponse,
   GetCredentialsPostRequest,
   GetCredentialsPostResponse,
   GetRecordPostRequest,
   GetRecordPostResponse,
   GetImagePostRequest,
   GetImagePostResponse,
   CanSendImagePostResponse,
   CanSendRecordPostResponse,
   GetStatusPostResponse,
   GetVersionInfoPostResponse,
   SetRestartPostResponse,
   CleanCachePostResponse,
   BotExitPostResponse,
   SetQqProfilePostRequest,
   SetQqProfilePostResponse,
   FieldGetModelShowPostRequest,
   FieldGetModelShowPostResponse,
   FieldSetModelShowPostResponse,
   GetOnlineClientsPostResponse,
   DeleteFriendPostRequest,
   DeleteFriendPostResponse,
   MarkMsgAsReadPostResponse,
   SendGroupForwardMsgPostResponse,
   SendPrivateForwardMsgPostResponse,
   GetGroupMsgHistoryPostRequest,
   GetGroupMsgHistoryPostResponse,
   OcrImagePostRequest,
   OcrImagePostResponse,
   FieldOcrImagePostRequest,
   FieldOcrImagePostResponse,
   GetGroupSystemMsgPostRequest,
   GetGroupSystemMsgPostResponse,
   GetEssenceMsgListPostRequest,
   GetEssenceMsgListPostResponse,
   GetGroupAtAllRemainPostRequest,
   GetGroupAtAllRemainPostResponse,
   SetGroupPortraitPostRequest,
   SetGroupPortraitPostResponse,
   SetEssenceMsgPostRequest,
   SetEssenceMsgPostResponse,
   DeleteEssenceMsgPostRequest,
   DeleteEssenceMsgPostResponse,
   FieldSendGroupNoticePostRequest,
   FieldSendGroupNoticePostResponse,
   FieldGetGroupNoticePostRequest,
   FieldGetGroupNoticePostResponse,
   UploadGroupFilePostRequest,
   UploadGroupFilePostResponse,
   DeleteGroupFilePostRequest,
   DeleteGroupFilePostResponse,
   CreateGroupFileFolderPostRequest,
   CreateGroupFileFolderPostResponse,
   DeleteGroupFolderPostRequest,
   DeleteGroupFolderPostResponse,
   GetGroupFileSystemInfoPostRequest,
   GetGroupFileSystemInfoPostResponse,
   GetGroupRootFilesPostRequest,
   GetGroupRootFilesPostResponse,
   GetGroupFilesByFolderPostRequest,
   GetGroupFilesByFolderPostResponse,
   GetGroupFileUrlPostRequest,
   GetGroupFileUrlPostResponse,
   UploadPrivateFilePostRequest,
   UploadPrivateFilePostResponse,
   DownloadFilePostRequest,
   DownloadFilePostResponse,
   CheckUrlSafelyPostRequest,
   CheckUrlSafelyPostResponse,
   FieldHandleQuickOperationPostResponse,
   SetDiyOnlineStatusPostRequest,
   SetDiyOnlineStatusPostResponse,
   ArkSharePeerPostRequest,
   ArkSharePeerPostResponse,
   ArkShareGroupPostRequest,
   ArkShareGroupPostResponse,
   SendGroupArkSharePostRequest,
   SendGroupArkSharePostResponse,
   SendArkSharePostRequest,
   SendArkSharePostResponse,
   GetRobotUinRangePostResponse,
   SetOnlineStatusPostRequest,
   SetOnlineStatusPostResponse,
   GetFriendsWithCategoryPostResponse,
   SetQqAvatarPostRequest,
   SetQqAvatarPostResponse,
   GetFilePostRequest,
   GetFilePostResponse,
   ForwardFriendSingleMsgPostRequest,
   ForwardFriendSingleMsgPostResponse,
   ForwardGroupSingleMsgPostRequest,
   ForwardGroupSingleMsgPostResponse,
   TranslateEn2zhPostRequest,
   TranslateEn2zhPostResponse,
   SetMsgEmojiLikePostRequest,
   SetMsgEmojiLikePostResponse,
   SendForwardMsgPostResponse,
   MarkPrivateMsgAsReadPostRequest,
   MarkPrivateMsgAsReadPostResponse,
   MarkGroupMsgAsReadPostRequest,
   MarkGroupMsgAsReadPostResponse,
   GetFriendMsgHistoryPostRequest,
   GetFriendMsgHistoryPostResponse,
   CreateCollectionPostRequest,
   CreateCollectionPostResponse,
   GetCollectionListPostRequest,
   GetCollectionListPostResponse,
   SetSelfLongnickPostRequest,
   SetSelfLongnickPostResponse,
   GetRecentContactPostRequest,
   GetRecentContactPostResponse,
   FieldMarkAllAsReadPostResponse,
   GetProfileLikePostRequest,
   GetProfileLikePostResponse,
   FetchCustomFacePostRequest,
   FetchCustomFacePostResponse,
   FetchEmojiLikePostRequest,
   FetchEmojiLikePostResponse,
   SetInputStatusPostRequest,
   SetInputStatusPostResponse,
   GetGroupInfoExPostRequest,
   GetGroupInfoExPostResponse,
   GetGroupDetailInfoPostRequest,
   GetGroupDetailInfoPostResponse,
   GetGroupIgnoreAddRequestPostResponse,
   FieldDelGroupNoticePostRequest,
   FieldDelGroupNoticePostResponse,
   FriendPokePostRequest,
   FriendPokePostResponse,
   GroupPokePostRequest,
   GroupPokePostResponse,
   NcGetPacketStatusPostResponse,
   NcGetUserStatusPostRequest,
   NcGetUserStatusPostResponse,
   NcGetRkeyPostResponse,
   GetGroupShutListPostRequest,
   GetGroupShutListPostResponse,
   MoveGroupFilePostRequest,
   MoveGroupFilePostResponse,
   TransGroupFilePostRequest,
   TransGroupFilePostResponse,
   RenameGroupFilePostRequest,
   RenameGroupFilePostResponse,
   GetGuildListPostResponse,
   GetGuildServiceProfilePostResponse,
   GetGroupIgnoredNotifiesPostResponse,
   SetGroupSignPostRequest,
   SetGroupSignPostResponse,
   SendGroupSignPostRequest,
   SendGroupSignPostResponse,
   SendPacketPostRequest,
   SendPacketPostResponse,
   GetMiniAppArkPostRequest,
   GetMiniAppArkPostResponse,
   GetAiRecordPostRequest,
   GetAiRecordPostResponse,
   GetAiCharactersPostRequest,
   GetAiCharactersPostResponse,
   SendGroupAiRecordPostRequest,
   SendGroupAiRecordPostResponse,
   GetClientkeyPostResponse,
   SendPokePostRequest,
   SendPokePostResponse,
)
# 定义一个 Protocol，避免循环导入 Client 类，同时保证类型提示
class CallActionProtocol(Protocol):
    async def call_action(self, action: str, params: Mapping[str, Any] | None = None) -> Any: ...

class NapCatAPI:
    """
    NapCat API 命名空间。
    所有自动生成的方法都挂载于此，通过 client.api.xxx 调用。
    """

    def __init__(self, client: CallActionProtocol):
        self._client = client


    async def clean_stream_temp_file(self, **kwargs: Any) -> CleanStreamTempFilePostResponse:
        """
        清理流临时文件

        标签: 流式操作
        """
        return await self._client.call_action("clean_stream_temp_file", kwargs)
    
    async def test_download_stream(self, **kwargs: Unpack[TestDownloadStreamPostRequest]) -> TestDownloadStreamPostResponse:
        """
        流式下载测试

        标签: 流式操作
        """
        return await self._client.call_action("test_download_stream", kwargs)
    
    async def upload_file_stream(self, **kwargs: Unpack[UploadFileStreamPostRequest]) -> UploadFileStreamPostResponse:
        """
        流式上传文件

        标签: 流式操作
        """
        return await self._client.call_action("upload_file_stream", kwargs)
    
    async def download_file_stream(self, **kwargs: Unpack[DownloadFileStreamPostRequest]) -> DownloadFileStreamPostResponse:
        """
        流式下载文件

        标签: 流式操作
        """
        return await self._client.call_action("download_file_stream", kwargs)
    
    async def download_file_record_stream(self, **kwargs: Unpack[DownloadFileRecordStreamPostRequest]) -> DownloadFileRecordStreamPostResponse:
        """
        流式下载语音文件

        标签: 流式操作
        """
        return await self._client.call_action("download_file_record_stream", kwargs)
    
    async def download_file_image_stream(self, **kwargs: Unpack[DownloadFileImageStreamPostRequest]) -> DownloadFileImageStreamPostResponse:
        """
        流式下载图片

        标签: 流式操作
        """
        return await self._client.call_action("download_file_image_stream", kwargs)
    
    async def del_group_album_media(self, **kwargs: Unpack[DelGroupAlbumMediaPostRequest]) -> DelGroupAlbumMediaPostResponse:
        """
        删除群相册文件

        标签: 文件相关
        """
        return await self._client.call_action("del_group_album_media", kwargs)
    
    async def set_group_album_media_like(self, **kwargs: Unpack[SetGroupAlbumMediaLikePostRequest]) -> SetGroupAlbumMediaLikePostResponse:
        """
        点赞群相册

        标签: 文件相关
        """
        return await self._client.call_action("set_group_album_media_like", kwargs)
    
    async def do_group_album_comment(self, **kwargs: Unpack[DoGroupAlbumCommentPostRequest]) -> DoGroupAlbumCommentPostResponse:
        """
        查看群相册评论

        标签: 文件相关
        """
        return await self._client.call_action("do_group_album_comment", kwargs)
    
    async def get_group_album_media_list(self, **kwargs: Unpack[GetGroupAlbumMediaListPostRequest]) -> GetGroupAlbumMediaListPostResponse:
        """
        获取群相册列表

        标签: 文件相关
        """
        return await self._client.call_action("get_group_album_media_list", kwargs)
    
    async def upload_image_to_qun_album(self, **kwargs: Unpack[UploadImageToQunAlbumPostRequest]) -> UploadImageToQunAlbumPostResponse:
        """
        上传图片到群相册

        标签: 文件相关
        """
        return await self._client.call_action("upload_image_to_qun_album", kwargs)
    
    async def get_qun_album_list(self, **kwargs: Unpack[GetQunAlbumListPostRequest]) -> GetQunAlbumListPostResponse:
        """
        获取群相册总列表

        标签: 文件相关
        """
        return await self._client.call_action("get_qun_album_list", kwargs)
    
    async def set_group_todo(self, **kwargs: Unpack[SetGroupTodoPostRequest]) -> SetGroupTodoPostResponse:
        """
        设置群代办

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_todo", kwargs)
    
    async def set_group_kick_members(self, **kwargs: Unpack[SetGroupKickMembersPostRequest]) -> SetGroupKickMembersPostResponse:
        """
        批量踢出群成员

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_kick_members", kwargs)
    
    async def set_group_robot_add_option(self, **kwargs: Unpack[SetGroupRobotAddOptionPostRequest]) -> SetGroupRobotAddOptionPostResponse:
        """
        设置群机器人添加选项

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_robot_add_option", kwargs)
    
    async def set_group_add_option(self, **kwargs: Unpack[SetGroupAddOptionPostRequest]) -> SetGroupAddOptionPostResponse:
        """
        设置群添加选项

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_add_option", kwargs)
    
    async def set_group_search(self, **kwargs: Unpack[SetGroupSearchPostRequest]) -> SetGroupSearchPostResponse:
        """
        设置群搜索

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_search", kwargs)
    
    async def get_doubt_friends_add_request(self, **kwargs: Unpack[GetDoubtFriendsAddRequestPostRequest]) -> GetDoubtFriendsAddRequestPostResponse:
        """
        获取被过滤好友请求

        标签: 账号相关
        """
        return await self._client.call_action("get_doubt_friends_add_request", kwargs)
    
    async def set_doubt_friends_add_request(self, **kwargs: Unpack[SetDoubtFriendsAddRequestPostRequest]) -> SetDoubtFriendsAddRequestPostResponse:
        """
        处理被过滤好友请求

        标签: 账号相关
        """
        return await self._client.call_action("set_doubt_friends_add_request", kwargs)
    
    async def get_rkey(self, **kwargs: Any) -> GetRkeyPostResponse:
        """
        获取rkey

        标签: 密钥相关
        """
        return await self._client.call_action("get_rkey", kwargs)
    
    async def get_rkey_server(self, **kwargs: Any) -> GetRkeyServerPostResponse:
        """
        获取rkey服务

        标签: 密钥相关
        """
        return await self._client.call_action("get_rkey_server", kwargs)
    
    async def set_group_remark(self, **kwargs: Unpack[SetGroupRemarkPostRequest]) -> SetGroupRemarkPostResponse:
        """
        设置群备注

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_remark", kwargs)
    
    async def get_private_file_url(self, **kwargs: Unpack[GetPrivateFileUrlPostRequest]) -> GetPrivateFileUrlPostResponse:
        """
        获取私聊文件链接

        标签: 文件相关
        """
        return await self._client.call_action("get_private_file_url", kwargs)
    
    async def click_inline_keyboard_button(self, **kwargs: Unpack[ClickInlineKeyboardButtonPostRequest]) -> ClickInlineKeyboardButtonPostResponse:
        """
        点击按钮

        标签: 个人操作
        """
        return await self._client.call_action("click_inline_keyboard_button", kwargs)
    
    async def get_unidirectional_friend_list(self, **kwargs: Any) -> GetUnidirectionalFriendListPostResponse:
        """
        获取单向好友列表

        标签: 账号相关
        """
        return await self._client.call_action("get_unidirectional_friend_list", kwargs)
    
    async def send_private_msg(self, **kwargs: Any) -> SendPrivateMsgPostResponse:
        """
        send_private_msg

        标签: 其他/保留
        """
        return await self._client.call_action("send_private_msg", kwargs)
    
    async def send_group_msg(self, **kwargs: Any) -> SendGroupMsgPostResponse:
        """
        send_group_msg

        标签: 其他/保留
        """
        return await self._client.call_action("send_group_msg", kwargs)
    
    async def send_msg(self, **kwargs: Any) -> SendMsgPostResponse:
        """
        send_msg

        标签: 其他/保留
        """
        return await self._client.call_action("send_msg", kwargs)
    
    async def delete_msg(self, **kwargs: Unpack[DeleteMsgPostRequest]) -> DeleteMsgPostResponse:
        """
        撤回消息

        标签: 消息相关
        """
        return await self._client.call_action("delete_msg", kwargs)
    
    async def get_msg(self, **kwargs: Unpack[GetMsgPostRequest]) -> GetMsgPostResponse:
        """
        获取消息详情

        标签: 消息相关
        """
        return await self._client.call_action("get_msg", kwargs)
    
    async def get_forward_msg(self, **kwargs: Unpack[GetForwardMsgPostRequest]) -> GetForwardMsgPostResponse:
        """
        获取合并转发消息

        标签: 消息相关
        """
        return await self._client.call_action("get_forward_msg", kwargs)
    
    async def send_like(self, **kwargs: Unpack[SendLikePostRequest]) -> SendLikePostResponse:
        """
        点赞

        标签: 账号相关
        """
        return await self._client.call_action("send_like", kwargs)
    
    async def set_group_kick(self, **kwargs: Unpack[SetGroupKickPostRequest]) -> SetGroupKickPostResponse:
        """
        群踢人

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_kick", kwargs)
    
    async def set_group_ban(self, **kwargs: Unpack[SetGroupBanPostRequest]) -> SetGroupBanPostResponse:
        """
        群禁言

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_ban", kwargs)
    
    async def set_group_whole_ban(self, **kwargs: Unpack[SetGroupWholeBanPostRequest]) -> SetGroupWholeBanPostResponse:
        """
        全体禁言

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_whole_ban", kwargs)
    
    async def set_group_admin(self, **kwargs: Unpack[SetGroupAdminPostRequest]) -> SetGroupAdminPostResponse:
        """
        设置群管理

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_admin", kwargs)
    
    async def set_group_card(self, **kwargs: Unpack[SetGroupCardPostRequest]) -> SetGroupCardPostResponse:
        """
        设置群成员名片

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_card", kwargs)
    
    async def set_group_name(self, **kwargs: Unpack[SetGroupNamePostRequest]) -> SetGroupNamePostResponse:
        """
        设置群名

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_name", kwargs)
    
    async def set_group_leave(self, **kwargs: Unpack[SetGroupLeavePostRequest]) -> SetGroupLeavePostResponse:
        """
        退群

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_leave", kwargs)
    
    async def set_group_special_title(self, **kwargs: Unpack[SetGroupSpecialTitlePostRequest]) -> SetGroupSpecialTitlePostResponse:
        """
        设置群头衔

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_special_title", kwargs)
    
    async def set_friend_add_request(self, **kwargs: Unpack[SetFriendAddRequestPostRequest]) -> SetFriendAddRequestPostResponse:
        """
        处理好友请求

        标签: 账号相关
        """
        return await self._client.call_action("set_friend_add_request", kwargs)
    
    async def set_friend_remark(self, **kwargs: Unpack[SetFriendRemarkPostRequest]) -> SetFriendRemarkPostResponse:
        """
        设置好友备注

        标签: 账号相关
        """
        return await self._client.call_action("set_friend_remark", kwargs)
    
    async def set_group_add_request(self, **kwargs: Unpack[SetGroupAddRequestPostRequest]) -> SetGroupAddRequestPostResponse:
        """
        处理加群请求

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_add_request", kwargs)
    
    async def get_login_info(self, **kwargs: Any) -> GetLoginInfoPostResponse:
        """
        获取登录号信息

        标签: 账号相关
        """
        return await self._client.call_action("get_login_info", kwargs)
    
    async def get_stranger_info(self, **kwargs: Unpack[GetStrangerInfoPostRequest]) -> GetStrangerInfoPostResponse:
        """
        获取账号信息

        标签: 账号相关
        """
        return await self._client.call_action("get_stranger_info", kwargs)
    
    async def get_friend_list(self, **kwargs: Unpack[GetFriendListPostRequest]) -> GetFriendListPostResponse:
        """
        获取好友列表

        标签: 账号相关
        """
        return await self._client.call_action("get_friend_list", kwargs)
    
    async def get_group_info(self, **kwargs: Unpack[GetGroupInfoPostRequest]) -> GetGroupInfoPostResponse:
        """
        获取群信息

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_info", kwargs)
    
    async def get_group_list(self, **kwargs: Unpack[GetGroupListPostRequest]) -> GetGroupListPostResponse:
        """
        获取群列表

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_list", kwargs)
    
    async def get_group_member_info(self, **kwargs: Unpack[GetGroupMemberInfoPostRequest]) -> GetGroupMemberInfoPostResponse:
        """
        获取群成员信息

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_member_info", kwargs)
    
    async def get_group_member_list(self, **kwargs: Unpack[GetGroupMemberListPostRequest]) -> GetGroupMemberListPostResponse:
        """
        获取群成员列表

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_member_list", kwargs)
    
    async def get_group_honor_info(self, **kwargs: Unpack[GetGroupHonorInfoPostRequest]) -> GetGroupHonorInfoPostResponse:
        """
        获取群荣誉

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_honor_info", kwargs)
    
    async def get_cookies(self, **kwargs: Unpack[GetCookiesPostRequest]) -> GetCookiesPostResponse:
        """
        获取cookies

        标签: 密钥相关
        """
        return await self._client.call_action("get_cookies", kwargs)
    
    async def get_csrf_token(self, **kwargs: Any) -> GetCsrfTokenPostResponse:
        """
        获取 CSRF Token

        标签: 密钥相关
        """
        return await self._client.call_action("get_csrf_token", kwargs)
    
    async def get_credentials(self, **kwargs: Unpack[GetCredentialsPostRequest]) -> GetCredentialsPostResponse:
        """
        获取 QQ 相关接口凭证

        标签: 密钥相关
        """
        return await self._client.call_action("get_credentials", kwargs)
    
    async def get_record(self, **kwargs: Unpack[GetRecordPostRequest]) -> GetRecordPostResponse:
        """
        获取语音消息详情

        标签: 消息相关
        """
        return await self._client.call_action("get_record", kwargs)
    
    async def get_image(self, **kwargs: Unpack[GetImagePostRequest]) -> GetImagePostResponse:
        """
        获取图片消息详情

        标签: 消息相关
        """
        return await self._client.call_action("get_image", kwargs)
    
    async def can_send_image(self, **kwargs: Any) -> CanSendImagePostResponse:
        """
        检查是否可以发送图片

        标签: 个人操作
        """
        return await self._client.call_action("can_send_image", kwargs)
    
    async def can_send_record(self, **kwargs: Any) -> CanSendRecordPostResponse:
        """
        检查是否可以发送语音

        标签: 个人操作
        """
        return await self._client.call_action("can_send_record", kwargs)
    
    async def get_status(self, **kwargs: Any) -> GetStatusPostResponse:
        """
        获取状态

        标签: 账号相关
        """
        return await self._client.call_action("get_status", kwargs)
    
    async def get_version_info(self, **kwargs: Any) -> GetVersionInfoPostResponse:
        """
        获取版本信息

        标签: 系统操作
        """
        return await self._client.call_action("get_version_info", kwargs)
    
    async def set_restart(self, **kwargs: Any) -> SetRestartPostResponse:
        """
        未提供描述
        """
        return await self._client.call_action("set_restart", kwargs)
    
    async def clean_cache(self, **kwargs: Any) -> CleanCachePostResponse:
        """
        清空缓存

        标签: 文件相关
        """
        return await self._client.call_action("clean_cache", kwargs)
    
    async def bot_exit(self, **kwargs: Any) -> BotExitPostResponse:
        """
        账号退出

        标签: 系统操作
        """
        return await self._client.call_action("bot_exit", kwargs)
    
    async def set_qq_profile(self, **kwargs: Unpack[SetQqProfilePostRequest]) -> SetQqProfilePostResponse:
        """
        设置账号信息

        标签: 账号相关
        """
        return await self._client.call_action("set_qq_profile", kwargs)
    
    async def _get_model_show(self, **kwargs: Unpack[FieldGetModelShowPostRequest]) -> FieldGetModelShowPostResponse:
        """
        _获取在线机型

        标签: 账号相关
        """
        return await self._client.call_action("_get_model_show", kwargs)
    
    async def _set_model_show(self, **kwargs: Any) -> FieldSetModelShowPostResponse:
        """
        _设置在线机型

        标签: 账号相关
        """
        return await self._client.call_action("_set_model_show", kwargs)
    
    async def get_online_clients(self, **kwargs: Any) -> GetOnlineClientsPostResponse:
        """
        获取当前账号在线客户端列表

        标签: 账号相关
        """
        return await self._client.call_action("get_online_clients", kwargs)
    
    async def delete_friend(self, **kwargs: Unpack[DeleteFriendPostRequest]) -> DeleteFriendPostResponse:
        """
        删除好友

        标签: 账号相关
        """
        return await self._client.call_action("delete_friend", kwargs)
    
    async def mark_msg_as_read(self, **kwargs: Any) -> MarkMsgAsReadPostResponse:
        """
        设置消息已读

        标签: 账号相关
        """
        return await self._client.call_action("mark_msg_as_read", kwargs)
    
    async def send_group_forward_msg(self, **kwargs: Any) -> SendGroupForwardMsgPostResponse:
        """
        发送群合并转发消息

        标签: 消息相关/发送群聊消息
        """
        return await self._client.call_action("send_group_forward_msg", kwargs)
    
    async def send_private_forward_msg(self, **kwargs: Any) -> SendPrivateForwardMsgPostResponse:
        """
        发送私聊合并转发消息

        标签: 消息相关/发送私聊消息
        """
        return await self._client.call_action("send_private_forward_msg", kwargs)
    
    async def get_group_msg_history(self, **kwargs: Unpack[GetGroupMsgHistoryPostRequest]) -> GetGroupMsgHistoryPostResponse:
        """
        获取群历史消息

        标签: 消息相关
        """
        return await self._client.call_action("get_group_msg_history", kwargs)
    
    async def ocr_image(self, **kwargs: Unpack[OcrImagePostRequest]) -> OcrImagePostResponse:
        """
        OCR 图片识别

        标签: 个人操作
        """
        return await self._client.call_action("ocr_image", kwargs)
    
    async def dot_ocr_image(self, **kwargs: Unpack[FieldOcrImagePostRequest]) -> FieldOcrImagePostResponse:
        """
        .OCR 图片识别

        标签: 个人操作
        """
        return await self._client.call_action(".ocr_image", kwargs)
    
    async def get_group_system_msg(self, **kwargs: Unpack[GetGroupSystemMsgPostRequest]) -> GetGroupSystemMsgPostResponse:
        """
        获取群系统消息

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_system_msg", kwargs)
    
    async def get_essence_msg_list(self, **kwargs: Unpack[GetEssenceMsgListPostRequest]) -> GetEssenceMsgListPostResponse:
        """
        获取群精华消息

        标签: 群聊相关
        """
        return await self._client.call_action("get_essence_msg_list", kwargs)
    
    async def get_group_at_all_remain(self, **kwargs: Unpack[GetGroupAtAllRemainPostRequest]) -> GetGroupAtAllRemainPostResponse:
        """
        获取群 @全体成员 剩余次数

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_at_all_remain", kwargs)
    
    async def set_group_portrait(self, **kwargs: Unpack[SetGroupPortraitPostRequest]) -> SetGroupPortraitPostResponse:
        """
        设置群头像

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_portrait", kwargs)
    
    async def set_essence_msg(self, **kwargs: Unpack[SetEssenceMsgPostRequest]) -> SetEssenceMsgPostResponse:
        """
        设置群精华消息

        标签: 群聊相关
        """
        return await self._client.call_action("set_essence_msg", kwargs)
    
    async def delete_essence_msg(self, **kwargs: Unpack[DeleteEssenceMsgPostRequest]) -> DeleteEssenceMsgPostResponse:
        """
        删除群精华消息

        标签: 群聊相关
        """
        return await self._client.call_action("delete_essence_msg", kwargs)
    
    async def _send_group_notice(self, **kwargs: Unpack[FieldSendGroupNoticePostRequest]) -> FieldSendGroupNoticePostResponse:
        """
        _发送群公告

        标签: 群聊相关
        """
        return await self._client.call_action("_send_group_notice", kwargs)
    
    async def _get_group_notice(self, **kwargs: Unpack[FieldGetGroupNoticePostRequest]) -> FieldGetGroupNoticePostResponse:
        """
        _获取群公告

        标签: 群聊相关
        """
        return await self._client.call_action("_get_group_notice", kwargs)
    
    async def upload_group_file(self, **kwargs: Unpack[UploadGroupFilePostRequest]) -> UploadGroupFilePostResponse:
        """
        上传群文件

        标签: 文件相关
        """
        return await self._client.call_action("upload_group_file", kwargs)
    
    async def delete_group_file(self, **kwargs: Unpack[DeleteGroupFilePostRequest]) -> DeleteGroupFilePostResponse:
        """
        删除群文件

        标签: 文件相关
        """
        return await self._client.call_action("delete_group_file", kwargs)
    
    async def create_group_file_folder(self, **kwargs: Unpack[CreateGroupFileFolderPostRequest]) -> CreateGroupFileFolderPostResponse:
        """
        创建群文件文件夹

        标签: 文件相关
        """
        return await self._client.call_action("create_group_file_folder", kwargs)
    
    async def delete_group_folder(self, **kwargs: Unpack[DeleteGroupFolderPostRequest]) -> DeleteGroupFolderPostResponse:
        """
        删除群文件夹

        标签: 文件相关
        """
        return await self._client.call_action("delete_group_folder", kwargs)
    
    async def get_group_file_system_info(self, **kwargs: Unpack[GetGroupFileSystemInfoPostRequest]) -> GetGroupFileSystemInfoPostResponse:
        """
        获取群文件系统信息

        标签: 文件相关
        """
        return await self._client.call_action("get_group_file_system_info", kwargs)
    
    async def get_group_root_files(self, **kwargs: Unpack[GetGroupRootFilesPostRequest]) -> GetGroupRootFilesPostResponse:
        """
        获取群根目录文件列表

        标签: 文件相关
        """
        return await self._client.call_action("get_group_root_files", kwargs)
    
    async def get_group_files_by_folder(self, **kwargs: Unpack[GetGroupFilesByFolderPostRequest]) -> GetGroupFilesByFolderPostResponse:
        """
        获取群子目录文件列表

        标签: 文件相关
        """
        return await self._client.call_action("get_group_files_by_folder", kwargs)
    
    async def get_group_file_url(self, **kwargs: Unpack[GetGroupFileUrlPostRequest]) -> GetGroupFileUrlPostResponse:
        """
        获取群文件链接

        标签: 文件相关
        """
        return await self._client.call_action("get_group_file_url", kwargs)
    
    async def upload_private_file(self, **kwargs: Unpack[UploadPrivateFilePostRequest]) -> UploadPrivateFilePostResponse:
        """
        上传私聊文件

        标签: 文件相关
        """
        return await self._client.call_action("upload_private_file", kwargs)
    
    async def download_file(self, **kwargs: Unpack[DownloadFilePostRequest]) -> DownloadFilePostResponse:
        """
        下载文件到缓存目录

        标签: 文件相关
        """
        return await self._client.call_action("download_file", kwargs)
    
    async def check_url_safely(self, **kwargs: Unpack[CheckUrlSafelyPostRequest]) -> CheckUrlSafelyPostResponse:
        """
        检查链接安全性

        标签: 其他/接口
        """
        return await self._client.call_action("check_url_safely", kwargs)
    
    async def dot_handle_quick_operation(self, **kwargs: Any) -> FieldHandleQuickOperationPostResponse:
        """
        .对事件执行快速操作

        标签: 个人操作
        """
        return await self._client.call_action(".handle_quick_operation", kwargs)
    
    async def set_diy_online_status(self, **kwargs: Unpack[SetDiyOnlineStatusPostRequest]) -> SetDiyOnlineStatusPostResponse:
        """
        设置自定义在线状态

        标签: 账号相关
        """
        return await self._client.call_action("set_diy_online_status", kwargs)
    
    async def ArkSharePeer(self, **kwargs: Unpack[ArkSharePeerPostRequest]) -> ArkSharePeerPostResponse:
        """
        获取推荐好友/群聊卡片

        标签: 账号相关
        """
        return await self._client.call_action("ArkSharePeer", kwargs)
    
    async def ArkShareGroup(self, **kwargs: Unpack[ArkShareGroupPostRequest]) -> ArkShareGroupPostResponse:
        """
        获取推荐群聊卡片

        标签: 账号相关
        """
        return await self._client.call_action("ArkShareGroup", kwargs)
    
    async def send_group_ark_share(self, **kwargs: Unpack[SendGroupArkSharePostRequest]) -> SendGroupArkSharePostResponse:
        """
        未提供描述
        """
        return await self._client.call_action("send_group_ark_share", kwargs)
    
    async def send_ark_share(self, **kwargs: Unpack[SendArkSharePostRequest]) -> SendArkSharePostResponse:
        """
        未提供描述
        """
        return await self._client.call_action("send_ark_share", kwargs)
    
    async def get_robot_uin_range(self, **kwargs: Any) -> GetRobotUinRangePostResponse:
        """
        获取机器人账号范围

        标签: 系统操作
        """
        return await self._client.call_action("get_robot_uin_range", kwargs)
    
    async def set_online_status(self, **kwargs: Unpack[SetOnlineStatusPostRequest]) -> SetOnlineStatusPostResponse:
        """
        设置在线状态

        标签: 账号相关
        """
        return await self._client.call_action("set_online_status", kwargs)
    
    async def get_friends_with_category(self, **kwargs: Any) -> GetFriendsWithCategoryPostResponse:
        """
        获取好友分组列表

        标签: 账号相关
        """
        return await self._client.call_action("get_friends_with_category", kwargs)
    
    async def set_qq_avatar(self, **kwargs: Unpack[SetQqAvatarPostRequest]) -> SetQqAvatarPostResponse:
        """
        设置头像

        标签: 账号相关
        """
        return await self._client.call_action("set_qq_avatar", kwargs)
    
    async def get_file(self, **kwargs: Unpack[GetFilePostRequest]) -> GetFilePostResponse:
        """
        获取文件信息

        标签: 文件相关
        """
        return await self._client.call_action("get_file", kwargs)
    
    async def forward_friend_single_msg(self, **kwargs: Unpack[ForwardFriendSingleMsgPostRequest]) -> ForwardFriendSingleMsgPostResponse:
        """
        消息转发到私聊

        标签: 消息相关/发送私聊消息
        """
        return await self._client.call_action("forward_friend_single_msg", kwargs)
    
    async def forward_group_single_msg(self, **kwargs: Unpack[ForwardGroupSingleMsgPostRequest]) -> ForwardGroupSingleMsgPostResponse:
        """
        消息转发到群

        标签: 消息相关/发送群聊消息
        """
        return await self._client.call_action("forward_group_single_msg", kwargs)
    
    async def translate_en2zh(self, **kwargs: Unpack[TranslateEn2zhPostRequest]) -> TranslateEn2zhPostResponse:
        """
        英译中

        标签: 个人操作
        """
        return await self._client.call_action("translate_en2zh", kwargs)
    
    async def set_msg_emoji_like(self, **kwargs: Unpack[SetMsgEmojiLikePostRequest]) -> SetMsgEmojiLikePostResponse:
        """
        贴表情

        标签: 消息相关
        """
        return await self._client.call_action("set_msg_emoji_like", kwargs)
    
    async def send_forward_msg(self, **kwargs: Any) -> SendForwardMsgPostResponse:
        """
        发送合并转发消息

        标签: 消息相关
        """
        return await self._client.call_action("send_forward_msg", kwargs)
    
    async def mark_private_msg_as_read(self, **kwargs: Unpack[MarkPrivateMsgAsReadPostRequest]) -> MarkPrivateMsgAsReadPostResponse:
        """
        设置私聊已读

        标签: 账号相关
        """
        return await self._client.call_action("mark_private_msg_as_read", kwargs)
    
    async def mark_group_msg_as_read(self, **kwargs: Unpack[MarkGroupMsgAsReadPostRequest]) -> MarkGroupMsgAsReadPostResponse:
        """
        设置群聊已读

        标签: 账号相关
        """
        return await self._client.call_action("mark_group_msg_as_read", kwargs)
    
    async def get_friend_msg_history(self, **kwargs: Unpack[GetFriendMsgHistoryPostRequest]) -> GetFriendMsgHistoryPostResponse:
        """
        获取好友历史消息

        标签: 消息相关
        """
        return await self._client.call_action("get_friend_msg_history", kwargs)
    
    async def create_collection(self, **kwargs: Unpack[CreateCollectionPostRequest]) -> CreateCollectionPostResponse:
        """
        创建收藏

        标签: 账号相关
        """
        return await self._client.call_action("create_collection", kwargs)
    
    async def get_collection_list(self, **kwargs: Unpack[GetCollectionListPostRequest]) -> GetCollectionListPostResponse:
        """
        获取收藏列表

        标签: 其他/bug
        """
        return await self._client.call_action("get_collection_list", kwargs)
    
    async def set_self_longnick(self, **kwargs: Unpack[SetSelfLongnickPostRequest]) -> SetSelfLongnickPostResponse:
        """
        设置个性签名

        标签: 账号相关
        """
        return await self._client.call_action("set_self_longnick", kwargs)
    
    async def get_recent_contact(self, **kwargs: Unpack[GetRecentContactPostRequest]) -> GetRecentContactPostResponse:
        """
        最近消息列表

        标签: 账号相关
        """
        return await self._client.call_action("get_recent_contact", kwargs)
    
    async def _mark_all_as_read(self, **kwargs: Any) -> FieldMarkAllAsReadPostResponse:
        """
        _设置所有消息已读

        标签: 账号相关
        """
        return await self._client.call_action("_mark_all_as_read", kwargs)
    
    async def get_profile_like(self, **kwargs: Unpack[GetProfileLikePostRequest]) -> GetProfileLikePostResponse:
        """
        获取点赞列表

        标签: 账号相关
        """
        return await self._client.call_action("get_profile_like", kwargs)
    
    async def fetch_custom_face(self, **kwargs: Unpack[FetchCustomFacePostRequest]) -> FetchCustomFacePostResponse:
        """
        获取收藏表情

        标签: 账号相关
        """
        return await self._client.call_action("fetch_custom_face", kwargs)
    
    async def fetch_emoji_like(self, **kwargs: Unpack[FetchEmojiLikePostRequest]) -> FetchEmojiLikePostResponse:
        """
        获取贴表情详情

        标签: 消息相关
        """
        return await self._client.call_action("fetch_emoji_like", kwargs)
    
    async def set_input_status(self, **kwargs: Unpack[SetInputStatusPostRequest]) -> SetInputStatusPostResponse:
        """
        设置输入状态

        标签: 个人操作
        """
        return await self._client.call_action("set_input_status", kwargs)
    
    async def get_group_info_ex(self, **kwargs: Unpack[GetGroupInfoExPostRequest]) -> GetGroupInfoExPostResponse:
        """
        获取群信息ex

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_info_ex", kwargs)
    
    async def get_group_detail_info(self, **kwargs: Unpack[GetGroupDetailInfoPostRequest]) -> GetGroupDetailInfoPostResponse:
        """
        获取群详细信息

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_detail_info", kwargs)
    
    async def get_group_ignore_add_request(self, **kwargs: Any) -> GetGroupIgnoreAddRequestPostResponse:
        """
        获取被过滤的加群请求

        标签: 其他/bug
        """
        return await self._client.call_action("get_group_ignore_add_request", kwargs)
    
    async def _del_group_notice(self, **kwargs: Unpack[FieldDelGroupNoticePostRequest]) -> FieldDelGroupNoticePostResponse:
        """
        _删除群公告

        标签: 群聊相关
        """
        return await self._client.call_action("_del_group_notice", kwargs)
    
    async def friend_poke(self, **kwargs: Unpack[FriendPokePostRequest]) -> FriendPokePostResponse:
        """
        发送私聊戳一戳

        标签: 消息相关/发送私聊消息
        """
        return await self._client.call_action("friend_poke", kwargs)
    
    async def group_poke(self, **kwargs: Unpack[GroupPokePostRequest]) -> GroupPokePostResponse:
        """
        发送群聊戳一戳

        标签: 消息相关/发送群聊消息
        """
        return await self._client.call_action("group_poke", kwargs)
    
    async def nc_get_packet_status(self, **kwargs: Any) -> NcGetPacketStatusPostResponse:
        """
        获取packet状态

        标签: 系统操作
        """
        return await self._client.call_action("nc_get_packet_status", kwargs)
    
    async def nc_get_user_status(self, **kwargs: Unpack[NcGetUserStatusPostRequest]) -> NcGetUserStatusPostResponse:
        """
        获取用户状态

        标签: 账号相关
        """
        return await self._client.call_action("nc_get_user_status", kwargs)
    
    async def nc_get_rkey(self, **kwargs: Any) -> NcGetRkeyPostResponse:
        """
        nc获取rkey

        标签: 密钥相关
        """
        return await self._client.call_action("nc_get_rkey", kwargs)
    
    async def get_group_shut_list(self, **kwargs: Unpack[GetGroupShutListPostRequest]) -> GetGroupShutListPostResponse:
        """
        获取群禁言列表

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_shut_list", kwargs)
    
    async def move_group_file(self, **kwargs: Unpack[MoveGroupFilePostRequest]) -> MoveGroupFilePostResponse:
        """
        移动群文件

        标签: 文件相关
        """
        return await self._client.call_action("move_group_file", kwargs)
    
    async def trans_group_file(self, **kwargs: Unpack[TransGroupFilePostRequest]) -> TransGroupFilePostResponse:
        """
        转存为永久文件

        标签: 文件相关
        """
        return await self._client.call_action("trans_group_file", kwargs)
    
    async def rename_group_file(self, **kwargs: Unpack[RenameGroupFilePostRequest]) -> RenameGroupFilePostResponse:
        """
        重命名群文件

        标签: 文件相关
        """
        return await self._client.call_action("rename_group_file", kwargs)
    
    async def get_guild_list(self, **kwargs: Any) -> GetGuildListPostResponse:
        """
        get_guild_list

        标签: 其他/接口
        """
        return await self._client.call_action("get_guild_list", kwargs)
    
    async def get_guild_service_profile(self, **kwargs: Any) -> GetGuildServiceProfilePostResponse:
        """
        get_guild_service_profile

        标签: 其他/接口
        """
        return await self._client.call_action("get_guild_service_profile", kwargs)
    
    async def get_group_ignored_notifies(self, **kwargs: Any) -> GetGroupIgnoredNotifiesPostResponse:
        """
        获取群过滤系统消息

        标签: 群聊相关
        """
        return await self._client.call_action("get_group_ignored_notifies", kwargs)
    
    async def set_group_sign(self, **kwargs: Unpack[SetGroupSignPostRequest]) -> SetGroupSignPostResponse:
        """
        群打卡

        标签: 群聊相关
        """
        return await self._client.call_action("set_group_sign", kwargs)
    
    async def send_group_sign(self, **kwargs: Unpack[SendGroupSignPostRequest]) -> SendGroupSignPostResponse:
        """
        群打卡

        标签: 群聊相关
        """
        return await self._client.call_action("send_group_sign", kwargs)
    
    async def send_packet(self, **kwargs: Unpack[SendPacketPostRequest]) -> SendPacketPostResponse:
        """
        发送自定义组包

        标签: 系统操作
        """
        return await self._client.call_action("send_packet", kwargs)
    
    async def get_mini_app_ark(self, payload: GetMiniAppArkPostRequest) -> GetMiniAppArkPostResponse:
        """
        获取小程序卡片

        标签: 账号相关
        """
        return await self._client.call_action("get_mini_app_ark", payload)
    
    async def get_ai_record(self, **kwargs: Unpack[GetAiRecordPostRequest]) -> GetAiRecordPostResponse:
        """
        获取AI语音

        标签: 个人操作
        """
        return await self._client.call_action("get_ai_record", kwargs)
    
    async def get_ai_characters(self, **kwargs: Unpack[GetAiCharactersPostRequest]) -> GetAiCharactersPostResponse:
        """
        获取AI语音人物

        标签: 个人操作
        """
        return await self._client.call_action("get_ai_characters", kwargs)
    
    async def send_group_ai_record(self, **kwargs: Unpack[SendGroupAiRecordPostRequest]) -> SendGroupAiRecordPostResponse:
        """
        发送群AI语音

        标签: 消息相关
        """
        return await self._client.call_action("send_group_ai_record", kwargs)
    
    async def get_clientkey(self, **kwargs: Any) -> GetClientkeyPostResponse:
        """
        获取clientkey

        标签: 密钥相关
        """
        return await self._client.call_action("get_clientkey", kwargs)
    
    async def send_poke(self, **kwargs: Unpack[SendPokePostRequest]) -> SendPokePostResponse:
        """
        发送戳一戳

        标签: 消息相关
        """
        return await self._client.call_action("send_poke", kwargs)
    
