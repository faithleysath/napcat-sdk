# Auto-generated file. Do not modify directly.
# 自动生成的文件。请勿直接修改。

"""
NapCat 客户端 API Mixin

自动生成的 API 方法，实现了 OneBot 11 (以及扩展) 的所有 API 调用接口。
混入到 NapCatClient 类中使用。
"""

from collections.abc import Mapping
from typing import Any, Unpack

from .types.schemas import (
    ArkShareGroupPostRequest,
    ArkShareGroupPostResponse,
    ArkSharePeerPostRequest,
    ArkSharePeerPostResponse,
    BotExitPostRequest,
    BotExitPostResponse,
    CancelOnlineFilePostRequest,
    CancelOnlineFilePostResponse,
    CanSendImagePostRequest,
    CanSendImagePostResponse,
    CanSendRecordPostRequest,
    CanSendRecordPostResponse,
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
    DelGroupAlbumMediaPostRequest,
    DelGroupAlbumMediaPostResponse,
    DoGroupAlbumCommentPostRequest,
    DoGroupAlbumCommentPostResponse,
    DownloadFileImageStreamPostRequest,
    DownloadFileImageStreamPostResponse,
    DownloadFilePostRequest,
    DownloadFilePostResponse,
    DownloadFileRecordStreamPostRequest,
    DownloadFileRecordStreamPostResponse,
    DownloadFilesetPostRequest,
    DownloadFilesetPostResponse,
    DownloadFileStreamPostRequest,
    DownloadFileStreamPostResponse,
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
    GetGroupFilesByFolderPostRequest,
    GetGroupFilesByFolderPostResponse,
    GetGroupFileSystemInfoPostRequest,
    GetGroupFileSystemInfoPostResponse,
    GetGroupFileUrlPostRequest,
    GetGroupFileUrlPostResponse,
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


class NapCatAPIMixin:
    """
    NapCat API mixin。
    所有自动生成的方法都混入 NapCatClient，通过 client.xxx 调用。
    """

    async def call_action(
        self, action: str, params: Mapping[str, Any] | None = None
    ) -> Any:
        raise NotImplementedError

    async def clean_stream_temp_file(
        self, **kwargs: Unpack[CleanStreamTempFilePostRequest]
    ) -> CleanStreamTempFilePostResponse:
        """
        清理流式传输临时文件

        标签: 流式传输扩展

        请求示例:
        {}

        成功响应 data 示例:
        {
          "message": "success"
        }
        """
        return await self.call_action("clean_stream_temp_file", kwargs)

    async def download_file_stream(
        self, **kwargs: Unpack[DownloadFileStreamPostRequest]
    ) -> DownloadFileStreamPostResponse:
        """
        下载文件流

        描述:
        以流式方式从网络或本地下载文件

        标签: 流式接口

        请求示例:
        {
          "file": "http://example.com/file.png"
        }

        成功响应 data 示例:
        {
          "type": "stream",
          "data_type": "file_info",
          "file_name": "file.png",
          "file_size": 1024
        }
        """
        return await self.call_action("download_file_stream", kwargs)

    async def download_file_record_stream(
        self, **kwargs: Unpack[DownloadFileRecordStreamPostRequest]
    ) -> DownloadFileRecordStreamPostResponse:
        """
        下载语音文件流

        标签: 流式传输扩展

        请求示例:
        {
          "file": "record_file_id"
        }

        成功响应 data 示例:
        {
          "file": "temp_record_path"
        }
        """
        return await self.call_action("download_file_record_stream", kwargs)

    async def download_file_image_stream(
        self, **kwargs: Unpack[DownloadFileImageStreamPostRequest]
    ) -> DownloadFileImageStreamPostResponse:
        """
        下载图片文件流

        标签: 流式传输扩展

        请求示例:
        {
          "file": "image_file_id"
        }

        成功响应 data 示例:
        {
          "file": "temp_image_path"
        }
        """
        return await self.call_action("download_file_image_stream", kwargs)

    async def test_download_stream(
        self, **kwargs: Unpack[TestDownloadStreamPostRequest]
    ) -> TestDownloadStreamPostResponse:
        """
        测试下载流

        标签: 流式传输扩展

        请求示例:
        {
          "error": false
        }

        成功响应 data 示例:
        {
          "success": true
        }
        """
        return await self.call_action("test_download_stream", kwargs)

    async def upload_file_stream(
        self, **kwargs: Unpack[UploadFileStreamPostRequest]
    ) -> UploadFileStreamPostResponse:
        """
        上传文件流

        描述:
        以流式方式上传文件数据到机器人

        标签: 流式接口

        请求示例:
        {
          "stream_id": "uuid-1234-5678",
          "chunk_data": "SGVsbG8gV29ybGQ=",
          "chunk_index": 0,
          "total_chunks": 1,
          "file_size": 11
        }

        成功响应 data 示例:
        {
          "type": "stream",
          "stream_id": "uuid-1234-5678",
          "status": "chunk_received",
          "received_chunks": 1,
          "total_chunks": 1
        }
        """
        return await self.call_action("upload_file_stream", kwargs)

    async def del_group_album_media(
        self, **kwargs: Unpack[DelGroupAlbumMediaPostRequest]
    ) -> DelGroupAlbumMediaPostResponse:
        """
        删除群相册媒体

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "album_id": "album_id_1",
          "lloc": "media_id_1"
        }

        成功响应 data 示例:
        {
          "result": {}
        }
        """
        return await self.call_action("del_group_album_media", kwargs)

    async def set_group_album_media_like(
        self, **kwargs: Unpack[SetGroupAlbumMediaLikePostRequest]
    ) -> SetGroupAlbumMediaLikePostResponse:
        """
        点赞群相册媒体

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "album_id": "album_id_1",
          "lloc": "media_id_1",
          "id": "123456"
        }

        成功响应 data 示例:
        {
          "result": {}
        }
        """
        return await self.call_action("set_group_album_media_like", kwargs)

    async def do_group_album_comment(
        self, **kwargs: Unpack[DoGroupAlbumCommentPostRequest]
    ) -> DoGroupAlbumCommentPostResponse:
        """
        发表群相册评论

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "album_id": "album_id_1",
          "lloc": "media_id_1",
          "content": "很有意思"
        }

        成功响应 data 示例:
        {
          "result": {}
        }
        """
        return await self.call_action("do_group_album_comment", kwargs)

    async def get_group_album_media_list(
        self, **kwargs: Unpack[GetGroupAlbumMediaListPostRequest]
    ) -> GetGroupAlbumMediaListPostResponse:
        """
        获取群相册媒体列表

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "album_id": "album_id_1"
        }

        成功响应 data 示例:
        {
          "media_list": [
            {
              "media_id": "media_id_1",
              "url": "http://example.com/1.jpg"
            }
          ]
        }
        """
        return await self.call_action("get_group_album_media_list", kwargs)

    async def get_qun_album_list(
        self, **kwargs: Unpack[GetQunAlbumListPostRequest]
    ) -> GetQunAlbumListPostResponse:
        """
        获取群相册列表

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "attach_info": ""
        }

        成功响应 data 示例:
        {
          "album_list": [
            {
              "album_id": "album_1",
              "album_name": "测试相册",
              "cover_url": "http://example.com/cover.jpg",
              "create_time": 1734567890
            }
          ],
          "attach_info": "",
          "has_more": false
        }
        """
        return await self.call_action("get_qun_album_list", kwargs)

    async def upload_image_to_qun_album(
        self, **kwargs: Unpack[UploadImageToQunAlbumPostRequest]
    ) -> UploadImageToQunAlbumPostResponse:
        """
        上传图片到群相册

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "album_id": "album_id_1",
          "album_name": "相册1",
          "file": "/path/to/image.jpg"
        }

        成功响应 data 示例:
        {
          "result": null
        }
        """
        return await self.call_action("upload_image_to_qun_album", kwargs)

    async def set_group_todo(
        self, **kwargs: Unpack[SetGroupTodoPostRequest]
    ) -> SetGroupTodoPostResponse:
        """
        设置群待办

        描述:
        将指定消息设置为群待办

        标签: 核心接口

        请求示例:
        {
          "group_id": "123456",
          "message_id": "123456789"
        }
        """
        return await self.call_action("set_group_todo", kwargs)

    async def get_group_detail_info(
        self, **kwargs: Unpack[GetGroupDetailInfoPostRequest]
    ) -> GetGroupDetailInfoPostResponse:
        """
        获取群详细信息

        描述:
        获取群聊的详细信息，包括成员数、最大成员数等

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        {
          "group_id": 123456,
          "group_name": "测试群",
          "member_count": 100,
          "max_member_count": 500
        }
        """
        return await self.call_action("get_group_detail_info", kwargs)

    async def set_group_kick_members(
        self, **kwargs: Unpack[SetGroupKickMembersPostRequest]
    ) -> SetGroupKickMembersPostResponse:
        """
        批量踢出群成员

        描述:
        从指定群聊中批量踢出多个成员

        标签: 扩展接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": [
            "123456789"
          ],
          "reject_add_request": false
        }
        """
        return await self.call_action("set_group_kick_members", kwargs)

    async def set_group_add_option(
        self, **kwargs: Unpack[SetGroupAddOptionPostRequest]
    ) -> SetGroupAddOptionPostResponse:
        """
        设置群加群选项

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "add_type": 1
        }
        """
        return await self.call_action("set_group_add_option", kwargs)

    async def set_group_robot_add_option(
        self, **kwargs: Unpack[SetGroupRobotAddOptionPostRequest]
    ) -> SetGroupRobotAddOptionPostResponse:
        """
        设置群机器人加群选项

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456"
        }
        """
        return await self.call_action("set_group_robot_add_option", kwargs)

    async def set_group_search(
        self, **kwargs: Unpack[SetGroupSearchPostRequest]
    ) -> SetGroupSearchPostResponse:
        """
        设置群搜索选项

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456"
        }
        """
        return await self.call_action("set_group_search", kwargs)

    async def set_doubt_friends_add_request(
        self, **kwargs: Unpack[SetDoubtFriendsAddRequestPostRequest]
    ) -> SetDoubtFriendsAddRequestPostResponse:
        """
        处理可疑好友申请

        描述:
        同意并处理系统的可疑好友申请

        标签: 系统接口

        请求示例:
        {
          "flag": "12345"
        }
        """
        return await self.call_action("set_doubt_friends_add_request", kwargs)

    async def get_doubt_friends_add_request(
        self, **kwargs: Unpack[GetDoubtFriendsAddRequestPostRequest]
    ) -> GetDoubtFriendsAddRequestPostResponse:
        """
        获取可疑好友申请

        描述:
        获取系统的可疑好友申请列表

        标签: 系统接口

        请求示例:
        {
          "count": 10
        }

        成功响应 data 示例:
        [
          {
            "user_id": 123456789,
            "nickname": "昵称",
            "age": 20,
            "sex": "male",
            "reason": "申请理由",
            "flag": "flag_123"
          }
        ]
        """
        return await self.call_action("get_doubt_friends_add_request", kwargs)

    async def set_friend_remark(
        self, **kwargs: Unpack[SetFriendRemarkPostRequest]
    ) -> SetFriendRemarkPostResponse:
        """
        设置好友备注

        描述:
        设置好友备注

        标签: 用户接口

        请求示例:
        {
          "user_id": "123456",
          "remark": "测试备注"
        }
        """
        return await self.call_action("set_friend_remark", kwargs)

    async def get_rkey(
        self, **kwargs: Unpack[GetRkeyPostRequest]
    ) -> GetRkeyPostResponse:
        """
        获取扩展 RKey

        标签: 系统扩展

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "type": "private",
            "rkey": "rkey_123",
            "created_at": 1734567890,
            "ttl": 3600
          }
        ]
        """
        return await self.call_action("get_rkey", kwargs)

    async def get_rkey_server(
        self, **kwargs: Unpack[GetRkeyServerPostRequest]
    ) -> GetRkeyServerPostResponse:
        """
        获取 RKey 服务器

        标签: 系统扩展

        请求示例:
        {}

        成功响应 data 示例:
        {
          "private_rkey": "&rkey=123456789",
          "group_rkey": "&rkey=123456789",
          "expired_time": 1694560000,
          "name": "NapCat 4"
        }
        """
        return await self.call_action("get_rkey_server", kwargs)

    async def set_group_remark(
        self, **kwargs: Unpack[SetGroupRemarkPostRequest]
    ) -> SetGroupRemarkPostResponse:
        """
        设置群备注

        描述:
        设置群备注

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456",
          "remark": "测试群备注"
        }
        """
        return await self.call_action("set_group_remark", kwargs)

    async def get_group_info_ex(
        self, **kwargs: Unpack[GetGroupInfoExPostRequest]
    ) -> GetGroupInfoExPostResponse:
        """
        获取群详细信息 (扩展)

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456"
        }
        """
        return await self.call_action("get_group_info_ex", kwargs)

    async def fetch_emoji_like(
        self, **kwargs: Unpack[FetchEmojiLikePostRequest]
    ) -> FetchEmojiLikePostResponse:
        """
        获取表情点赞详情

        标签: 消息扩展

        请求示例:
        {
          "message_id": 12345,
          "emojiId": "123",
          "emojiType": 1,
          "count": 10,
          "cookie": ""
        }

        成功响应 data 示例:
        {
          "emojiLikesList": [
            {
              "tinyId": "123456",
              "nickName": "测试用户",
              "headUrl": "http://example.com/avatar.png"
            }
          ],
          "cookie": "",
          "isLastPage": true,
          "isFirstPage": true,
          "result": 0,
          "errMsg": ""
        }
        """
        return await self.call_action("fetch_emoji_like", kwargs)

    async def get_emoji_likes(
        self, **kwargs: Unpack[GetEmojiLikesPostRequest]
    ) -> GetEmojiLikesPostResponse:
        """
        获取消息表情点赞列表

        标签: 消息扩展

        请求示例:
        {
          "message_id": "12345",
          "emoji_id": "123"
        }

        成功响应 data 示例:
        {
          "emoji_like_list": [
            {
              "user_id": "654321",
              "nick_name": "测试用户"
            }
          ]
        }
        """
        return await self.call_action("get_emoji_likes", kwargs)

    async def get_file(
        self, **kwargs: Unpack[GetFilePostRequest]
    ) -> GetFilePostResponse:
        """
        获取文件

        描述:
        获取指定文件的详细信息及下载路径

        标签: 文件接口

        请求示例:
        {
          "file": "file_id_123"
        }

        成功响应 data 示例:
        {
          "file": "/path/to/file",
          "url": "http://...",
          "file_size": 1024,
          "file_name": "test.jpg"
        }
        """
        return await self.call_action("get_file", kwargs)

    async def set_qq_profile(
        self, **kwargs: Unpack[SetQqProfilePostRequest]
    ) -> SetQqProfilePostResponse:
        """
        设置QQ资料

        描述:
        修改当前账号的昵称、个性签名等资料

        标签: Go-CQHTTP

        请求示例:
        {
          "nickname": "新昵称",
          "personal_note": "个性签名"
        }
        """
        return await self.call_action("set_qq_profile", kwargs)

    async def ArkShareGroup(
        self, **kwargs: Unpack[ArkShareGroupPostRequest]
    ) -> ArkShareGroupPostResponse:
        """
        分享群 (Ark)

        描述:
        获取群分享的 Ark 内容

        标签: 消息扩展

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        "{\"app\": \"com.tencent.structmsg\", ...}"
        """
        return await self.call_action("ArkShareGroup", kwargs)

    async def ArkSharePeer(
        self, **kwargs: Unpack[ArkSharePeerPostRequest]
    ) -> ArkSharePeerPostResponse:
        """
        分享用户 (Ark)

        描述:
        获取用户推荐的 Ark 内容

        标签: 消息扩展

        请求示例:
        {
          "user_id": "123456",
          "phone_number": ""
        }

        成功响应 data 示例:
        {
          "ark": "..."
        }
        """
        return await self.call_action("ArkSharePeer", kwargs)

    async def send_group_ark_share(
        self, **kwargs: Unpack[SendGroupArkSharePostRequest]
    ) -> SendGroupArkSharePostResponse:
        """
        分享群 (Ark)

        描述:
        获取群分享的 Ark 内容

        标签: 消息扩展

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        "{\"app\": \"com.tencent.structmsg\", ...}"
        """
        return await self.call_action("send_group_ark_share", kwargs)

    async def send_ark_share(
        self, **kwargs: Unpack[SendArkSharePostRequest]
    ) -> SendArkSharePostResponse:
        """
        分享用户 (Ark)

        描述:
        获取用户推荐的 Ark 内容

        标签: 消息扩展

        请求示例:
        {
          "user_id": "123456",
          "phone_number": ""
        }

        成功响应 data 示例:
        {
          "ark": "..."
        }
        """
        return await self.call_action("send_ark_share", kwargs)

    async def create_collection(
        self, **kwargs: Unpack[CreateCollectionPostRequest]
    ) -> CreateCollectionPostResponse:
        """
        创建收藏

        标签: 扩展接口

        请求示例:
        {
          "rawData": "收藏内容",
          "brief": "收藏标题"
        }

        成功响应 data 示例:
        {
          "result": 0,
          "errMsg": ""
        }
        """
        return await self.call_action("create_collection", kwargs)

    async def set_self_longnick(
        self, **kwargs: Unpack[SetSelfLongnickPostRequest]
    ) -> SetSelfLongnickPostResponse:
        """
        设置个性签名

        描述:
        修改当前登录帐号的个性签名

        标签: 扩展接口

        请求示例:
        {
          "longNick": "个性签名"
        }
        """
        return await self.call_action("set_self_longnick", kwargs)

    async def forward_friend_single_msg(
        self, **kwargs: Unpack[ForwardFriendSingleMsgPostRequest]
    ) -> ForwardFriendSingleMsgPostResponse:
        """
        转发单条消息

        描述:
        转发单条消息

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345,
          "group_id": "123456"
        }
        """
        return await self.call_action("forward_friend_single_msg", kwargs)

    async def forward_group_single_msg(
        self, **kwargs: Unpack[ForwardGroupSingleMsgPostRequest]
    ) -> ForwardGroupSingleMsgPostResponse:
        """
        转发单条消息

        描述:
        转发单条消息

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345,
          "group_id": "123456"
        }
        """
        return await self.call_action("forward_group_single_msg", kwargs)

    async def mark_group_msg_as_read(
        self, **kwargs: Unpack[MarkGroupMsgAsReadPostRequest]
    ) -> MarkGroupMsgAsReadPostResponse:
        """
        标记群聊已读

        描述:
        标记指定渠道的消息为已读

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345
        }
        """
        return await self.call_action("mark_group_msg_as_read", kwargs)

    async def mark_private_msg_as_read(
        self, **kwargs: Unpack[MarkPrivateMsgAsReadPostRequest]
    ) -> MarkPrivateMsgAsReadPostResponse:
        """
        标记私聊已读

        描述:
        标记指定渠道的消息为已读

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345
        }
        """
        return await self.call_action("mark_private_msg_as_read", kwargs)

    async def set_qq_avatar(
        self, **kwargs: Unpack[SetQqAvatarPostRequest]
    ) -> SetQqAvatarPostResponse:
        """
        设置QQ头像

        描述:
        修改当前账号的QQ头像

        标签: 扩展接口

        请求示例:
        {
          "file": "base64://..."
        }
        """
        return await self.call_action("set_qq_avatar", kwargs)

    async def translate_en2zh(
        self, **kwargs: Unpack[TranslateEn2zhPostRequest]
    ) -> TranslateEn2zhPostResponse:
        """
        英文单词翻译

        描述:
        将英文单词列表翻译为中文

        标签: 扩展接口

        请求示例:
        {
          "words": [
            "hello"
          ]
        }

        成功响应 data 示例:
        {
          "words": [
            "你好"
          ]
        }
        """
        return await self.call_action("translate_en2zh", kwargs)

    async def get_group_root_files(
        self, **kwargs: Unpack[GetGroupRootFilesPostRequest]
    ) -> GetGroupRootFilesPostResponse:
        """
        获取群根目录文件列表

        描述:
        获取群文件根目录下的所有文件和文件夹

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        {
          "files": [],
          "folders": []
        }
        """
        return await self.call_action("get_group_root_files", kwargs)

    async def set_group_sign(
        self, **kwargs: Unpack[SetGroupSignPostRequest]
    ) -> SetGroupSignPostResponse:
        """
        群打卡

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456789"
        }
        """
        return await self.call_action("set_group_sign", kwargs)

    async def send_group_sign(
        self, **kwargs: Unpack[SendGroupSignPostRequest]
    ) -> SendGroupSignPostResponse:
        """
        群打卡

        标签: 群组扩展

        请求示例:
        {
          "group_id": "123456789"
        }
        """
        return await self.call_action("send_group_sign", kwargs)

    async def get_clientkey(
        self, **kwargs: Unpack[GetClientkeyPostRequest]
    ) -> GetClientkeyPostResponse:
        """
        获取ClientKey

        描述:
        获取当前登录帐号的ClientKey

        标签: 扩展接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "clientkey": "abcdef123456"
        }
        """
        return await self.call_action("get_clientkey", kwargs)

    async def move_group_file(
        self, **kwargs: Unpack[MoveGroupFilePostRequest]
    ) -> MoveGroupFilePostResponse:
        """
        移动群文件

        标签: 文件扩展

        请求示例:
        {
          "group_id": "123456",
          "file_id": "/file_id",
          "current_parent_directory": "/current_folder_id",
          "target_parent_directory": "/target_folder_id"
        }

        成功响应 data 示例:
        {
          "ok": true
        }
        """
        return await self.call_action("move_group_file", kwargs)

    async def rename_group_file(
        self, **kwargs: Unpack[RenameGroupFilePostRequest]
    ) -> RenameGroupFilePostResponse:
        """
        重命名群文件

        标签: 文件扩展

        请求示例:
        {
          "group_id": "123456",
          "file_id": "/file_id",
          "current_parent_directory": "/",
          "new_name": "new_name.jpg"
        }

        成功响应 data 示例:
        {
          "ok": true
        }
        """
        return await self.call_action("rename_group_file", kwargs)

    async def trans_group_file(
        self, **kwargs: Unpack[TransGroupFilePostRequest]
    ) -> TransGroupFilePostResponse:
        """
        传输群文件

        标签: 文件扩展

        请求示例:
        {
          "group_id": "123456",
          "file_id": "/file_id"
        }

        成功响应 data 示例:
        {
          "ok": true
        }
        """
        return await self.call_action("trans_group_file", kwargs)

    async def send_like(
        self, **kwargs: Unpack[SendLikePostRequest]
    ) -> SendLikePostResponse:
        """
        点赞

        描述:
        给指定用户点赞

        标签: 用户接口

        请求示例:
        {
          "user_id": "123456",
          "times": 10
        }
        """
        return await self.call_action("send_like", kwargs)

    async def get_msg(self, **kwargs: Unpack[GetMsgPostRequest]) -> GetMsgPostResponse:
        """
        获取消息

        描述:
        根据消息 ID 获取消息详细信息

        标签: 消息接口

        请求示例:
        {
          "message_id": 123456
        }

        成功响应 data 示例:
        {
          "time": 1710000000,
          "message_type": "group",
          "message_id": 123456,
          "real_id": 123456,
          "sender": {
            "user_id": 123456789,
            "nickname": "昵称"
          },
          "message": "hello"
        }
        """
        return await self.call_action("get_msg", kwargs)

    async def get_login_info(
        self, **kwargs: Unpack[GetLoginInfoPostRequest]
    ) -> GetLoginInfoPostResponse:
        """
        获取登录号信息

        描述:
        获取当前登录帐号的信息

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "user_id": 123456789,
          "nickname": "机器人"
        }
        """
        return await self.call_action("get_login_info", kwargs)

    async def get_friend_list(
        self, **kwargs: Unpack[GetFriendListPostRequest]
    ) -> GetFriendListPostResponse:
        """
        获取好友列表

        描述:
        获取当前帐号的好友列表

        标签: 用户接口

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "user_id": 123456789,
            "nickname": "昵称",
            "remark": "备注"
          }
        ]
        """
        return await self.call_action("get_friend_list", kwargs)

    async def get_group_list(
        self, **kwargs: Unpack[GetGroupListPostRequest]
    ) -> GetGroupListPostResponse:
        """
        获取群列表

        描述:
        获取当前帐号的群聊列表

        标签: 群组接口

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "group_id": 123456,
            "group_name": "测试群",
            "member_count": 100,
            "max_member_count": 500
          }
        ]
        """
        return await self.call_action("get_group_list", kwargs)

    async def get_group_info(
        self, **kwargs: Unpack[GetGroupInfoPostRequest]
    ) -> GetGroupInfoPostResponse:
        """
        获取群信息

        描述:
        获取群聊的基本信息

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        {
          "group_id": 123456,
          "group_name": "测试群",
          "member_count": 100,
          "max_member_count": 500
        }
        """
        return await self.call_action("get_group_info", kwargs)

    async def get_group_member_list(
        self, **kwargs: Unpack[GetGroupMemberListPostRequest]
    ) -> GetGroupMemberListPostResponse:
        """
        获取群成员列表

        描述:
        获取群聊中的所有成员列表

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        [
          {
            "group_id": 123456,
            "user_id": 123456789,
            "nickname": "昵称",
            "card": "名片",
            "role": "member"
          }
        ]
        """
        return await self.call_action("get_group_member_list", kwargs)

    async def get_group_member_info(
        self, **kwargs: Unpack[GetGroupMemberInfoPostRequest]
    ) -> GetGroupMemberInfoPostResponse:
        """
        获取群成员信息

        描述:
        获取群聊中指定成员的信息

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789"
        }

        成功响应 data 示例:
        {
          "group_id": 123456,
          "user_id": 123456789,
          "nickname": "昵称",
          "card": "名片",
          "role": "member"
        }
        """
        return await self.call_action("get_group_member_info", kwargs)

    async def send_group_msg(
        self, **kwargs: Unpack[SendGroupMsgPostRequest]
    ) -> SendGroupMsgPostResponse:
        """
        发送群消息

        描述:
        发送群消息

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "message": "hello"
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_group_msg", kwargs)

    async def send_private_msg(
        self, **kwargs: Unpack[SendPrivateMsgPostRequest]
    ) -> SendPrivateMsgPostResponse:
        """
        发送私聊消息

        描述:
        发送私聊消息

        标签: 消息接口

        请求示例:
        {
          "user_id": "123456789",
          "message": "hello"
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_private_msg", kwargs)

    async def send_msg(
        self, **kwargs: Unpack[SendMsgPostRequest]
    ) -> SendMsgPostResponse:
        """
        发送消息

        描述:
        发送私聊或群聊消息

        标签: 消息接口

        请求示例:
        {
          "message_type": "group",
          "group_id": "123456",
          "message": "hello"
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_msg", kwargs)

    async def delete_msg(
        self, **kwargs: Unpack[DeleteMsgPostRequest]
    ) -> DeleteMsgPostResponse:
        """
        撤回消息

        描述:
        撤回已发送的消息

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345
        }
        """
        return await self.call_action("delete_msg", kwargs)

    async def set_group_add_request(
        self, **kwargs: Unpack[SetGroupAddRequestPostRequest]
    ) -> SetGroupAddRequestPostResponse:
        """
        处理加群请求

        描述:
        同意或拒绝加群请求或邀请

        标签: 群组接口

        请求示例:
        {
          "flag": "flag_123",
          "sub_type": "add",
          "approve": true
        }
        """
        return await self.call_action("set_group_add_request", kwargs)

    async def set_friend_add_request(
        self, **kwargs: Unpack[SetFriendAddRequestPostRequest]
    ) -> SetFriendAddRequestPostResponse:
        """
        处理加好友请求

        描述:
        同意或拒绝加好友请求

        标签: 用户接口

        请求示例:
        {
          "flag": "flag_12345",
          "approve": true,
          "remark": "新朋友"
        }
        """
        return await self.call_action("set_friend_add_request", kwargs)

    async def set_group_leave(
        self, **kwargs: Unpack[SetGroupLeavePostRequest]
    ) -> SetGroupLeavePostResponse:
        """
        退出群组

        描述:
        退出指定群聊；群主可通过 is_dismiss=true 解散群聊

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "is_dismiss": false
        }
        """
        return await self.call_action("set_group_leave", kwargs)

    async def get_version_info(
        self, **kwargs: Unpack[GetVersionInfoPostRequest]
    ) -> GetVersionInfoPostResponse:
        """
        获取版本信息

        描述:
        获取版本信息

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "app_name": "NapCat.Onebot",
          "protocol_version": "v11",
          "app_version": "1.0.0"
        }
        """
        return await self.call_action("get_version_info", kwargs)

    async def can_send_record(
        self, **kwargs: Unpack[CanSendRecordPostRequest]
    ) -> CanSendRecordPostResponse:
        """
        是否可以发送语音

        描述:
        检查是否可以发送语音

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "yes": true
        }
        """
        return await self.call_action("can_send_record", kwargs)

    async def can_send_image(
        self, **kwargs: Unpack[CanSendImagePostRequest]
    ) -> CanSendImagePostResponse:
        """
        是否可以发送图片

        描述:
        检查是否可以发送图片

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "yes": true
        }
        """
        return await self.call_action("can_send_image", kwargs)

    async def get_status(
        self, **kwargs: Unpack[GetStatusPostRequest]
    ) -> GetStatusPostResponse:
        """
        获取运行状态

        描述:
        获取运行状态

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "online": true,
          "good": true,
          "stat": {}
        }
        """
        return await self.call_action("get_status", kwargs)

    async def set_group_whole_ban(
        self, **kwargs: Unpack[SetGroupWholeBanPostRequest]
    ) -> SetGroupWholeBanPostResponse:
        """
        全员禁言

        描述:
        开启或关闭指定群聊的全员禁言

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "enable": true
        }
        """
        return await self.call_action("set_group_whole_ban", kwargs)

    async def set_group_ban(
        self, **kwargs: Unpack[SetGroupBanPostRequest]
    ) -> SetGroupBanPostResponse:
        """
        群组禁言

        描述:
        禁言群聊中的指定成员

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789",
          "duration": 1800
        }
        """
        return await self.call_action("set_group_ban", kwargs)

    async def set_group_kick(
        self, **kwargs: Unpack[SetGroupKickPostRequest]
    ) -> SetGroupKickPostResponse:
        """
        群组踢人

        描述:
        将指定成员踢出群聊

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789",
          "reject_add_request": false
        }
        """
        return await self.call_action("set_group_kick", kwargs)

    async def set_group_admin(
        self, **kwargs: Unpack[SetGroupAdminPostRequest]
    ) -> SetGroupAdminPostResponse:
        """
        设置群管理员

        描述:
        设置或取消群聊中的管理员

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789",
          "enable": true
        }
        """
        return await self.call_action("set_group_admin", kwargs)

    async def set_group_name(
        self, **kwargs: Unpack[SetGroupNamePostRequest]
    ) -> SetGroupNamePostResponse:
        """
        设置群名称

        描述:
        修改指定群聊的名称

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "group_name": "新群名"
        }
        """
        return await self.call_action("set_group_name", kwargs)

    async def set_group_card(
        self, **kwargs: Unpack[SetGroupCardPostRequest]
    ) -> SetGroupCardPostResponse:
        """
        设置群名片

        描述:
        设置群聊中指定成员的群名片

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789",
          "card": "新名片"
        }
        """
        return await self.call_action("set_group_card", kwargs)

    async def get_image(
        self, **kwargs: Unpack[GetImagePostRequest]
    ) -> GetImagePostResponse:
        """
        获取图片

        描述:
        获取指定图片的信息及路径

        标签: 文件接口

        请求示例:
        {
          "file": "image_id_123"
        }

        成功响应 data 示例:
        {
          "file": "/path/to/image",
          "url": "http://..."
        }
        """
        return await self.call_action("get_image", kwargs)

    async def get_record(
        self, **kwargs: Unpack[GetRecordPostRequest]
    ) -> GetRecordPostResponse:
        """
        获取语音

        描述:
        获取指定语音文件的信息，并支持格式转换

        标签: 文件接口

        请求示例:
        {
          "file": "record_id_123",
          "out_format": "mp3"
        }

        成功响应 data 示例:
        {
          "file": "/path/to/record",
          "url": "http://..."
        }
        """
        return await self.call_action("get_record", kwargs)

    async def set_msg_emoji_like(
        self, **kwargs: Unpack[SetMsgEmojiLikePostRequest]
    ) -> SetMsgEmojiLikePostResponse:
        """
        设置消息表情点赞

        标签: 消息扩展

        请求示例:
        {
          "message_id": 12345,
          "emoji_id": "123",
          "set": true
        }

        成功响应 data 示例:
        {
          "result": true
        }
        """
        return await self.call_action("set_msg_emoji_like", kwargs)

    async def get_cookies(
        self, **kwargs: Unpack[GetCookiesPostRequest]
    ) -> GetCookiesPostResponse:
        """
        获取 Cookies

        描述:
        获取指定域名的 Cookies

        标签: 用户接口

        请求示例:
        {
          "domain": "qun.qq.com"
        }

        成功响应 data 示例:
        {
          "cookies": "uin=o123456789; skey=@abc12345;",
          "bkn": "123456789"
        }
        """
        return await self.call_action("get_cookies", kwargs)

    async def set_online_status(
        self, **kwargs: Unpack[SetOnlineStatusPostRequest]
    ) -> SetOnlineStatusPostResponse:
        """
        设置在线状态

        描述:
        ## 状态列表

        ### 在线
        ```json5;
        { "status": 10, "ext_status": 0, "battery_status": 0; }
        ```

        ### Q我吧
        ```json5;
        { "status": 60, "ext_status": 0, "battery_status": 0; }
        ```

        ### 离开
        ```json5;
        { "status": 30, "ext_status": 0, "battery_status": 0; }
        ```

        ### 忙碌
        ```json5;
        { "status": 50, "ext_status": 0, "battery_status": 0; }
        ```

        ### 请勿打扰
        ```json5;
        { "status": 70, "ext_status": 0, "battery_status": 0; }
        ```

        ### 隐身
        ```json5;
        { "status": 40, "ext_status": 0, "battery_status": 0; }
        ```

        ### 听歌中
        ```json5;
        { "status": 10, "ext_status": 1028, "battery_status": 0; }
        ```

        ### 春日限定
        ```json5;
        { "status": 10, "ext_status": 2037, "battery_status": 0; }
        ```

        ### 一起元梦
        ```json5;
        { "status": 10, "ext_status": 2025, "battery_status": 0; }
        ```

        ### 求星搭子
        ```json5;
        { "status": 10, "ext_status": 2026, "battery_status": 0; }
        ```

        ### 被掏空
        ```json5;
        { "status": 10, "ext_status": 2014, "battery_status": 0; }
        ```

        ### 今日天气
        ```json5;
        { "status": 10, "ext_status": 1030, "battery_status": 0; }
        ```

        ### 我crash了
        ```json5;
        { "status": 10, "ext_status": 2019, "battery_status": 0; }
        ```

        ### 爱你
        ```json5;
        { "status": 10, "ext_status": 2006, "battery_status": 0; }
        ```

        ### 恋爱中
        ```json5;
        { "status": 10, "ext_status": 1051, "battery_status": 0; }
        ```

        ### 好运锦鲤
        ```json5;
        { "status": 10, "ext_status": 1071, "battery_status": 0; }
        ```

        ### 水逆退散
        ```json5;
        { "status": 10, "ext_status": 1201, "battery_status": 0; }
        ```

        ### 嗨到飞起
        ```json5;
        { "status": 10, "ext_status": 1056, "battery_status": 0; }
        ```

        ### 元气满满
        ```json5;
        { "status": 10, "ext_status": 1058, "battery_status": 0; }
        ```

        ### 宝宝认证
        ```json5;
        { "status": 10, "ext_status": 1070, "battery_status": 0; }
        ```

        ### 一言难尽
        ```json5;
        { "status": 10, "ext_status": 1063, "battery_status": 0; }
        ```

        ### 难得糊涂
        ```json5;
        { "status": 10, "ext_status": 2001, "battery_status": 0; }
        ```

        ### emo中
        ```json5;
        { "status": 10, "ext_status": 1401, "battery_status": 0; }
        ```

        ### 我太难了
        ```json5;
        { "status": 10, "ext_status": 1062, "battery_status": 0; }
        ```

        ### 我想开了
        ```json5;
        { "status": 10, "ext_status": 2013, "battery_status": 0; }
        ```

        ### 我没事
        ```json5;
        { "status": 10, "ext_status": 1052, "battery_status": 0; }
        ```

        ### 想静静
        ```json5;
        { "status": 10, "ext_status": 1061, "battery_status": 0; }
        ```

        ### 悠哉哉
        ```json5;
        { "status": 10, "ext_status": 1059, "battery_status": 0; }
        ```

        ### 去旅行
        ```json5;
        { "status": 10, "ext_status": 2015, "battery_status": 0; }
        ```

        ### 信号弱
        ```json5;
        { "status": 10, "ext_status": 1011, "battery_status": 0; }
        ```

        ### 出去浪
        ```json5;
        { "status": 10, "ext_status": 2003, "battery_status": 0; }
        ```

        ### 肝作业
        ```json5;
        { "status": 10, "ext_status": 2012, "battery_status": 0; }
        ```

        ### 学习中
        ```json5;
        { "status": 10, "ext_status": 1018, "battery_status": 0; }
        ```

        ### 搬砖中
        ```json5;
        { "status": 10, "ext_status": 2023, "battery_status": 0; }
        ```

        ### 摸鱼中
        ```json5;
        { "status": 10, "ext_status": 1300, "battery_status": 0; }
        ```

        ### 无聊中
        ```json5;
        { "status": 10, "ext_status": 1060, "battery_status": 0; }
        ```

        ### timi中
        ```json5;
        { "status": 10, "ext_status": 1027, "battery_status": 0; }
        ```

        ### 睡觉中
        ```json5;
        { "status": 10, "ext_status": 1016, "battery_status": 0; }
        ```

        ### 熬夜中
        ```json5;
        { "status": 10, "ext_status": 1032, "battery_status": 0; }
        ```

        ### 追剧中
        ```json5;
        { "status": 10, "ext_status": 1021, "battery_status": 0; }
        ```

        ### 我的电量
        ```json5;
        {
          "status": 10,
            "ext_status": 1000,
              "battery_status": 0;
        }
        ```

        标签: 系统扩展

        请求示例:
        {
          "status": 11,
          "ext_status": 0,
          "battery_status": 100
        }
        """
        return await self.call_action("set_online_status", kwargs)

    async def get_robot_uin_range(
        self, **kwargs: Unpack[GetRobotUinRangePostRequest]
    ) -> GetRobotUinRangePostResponse:
        """
        获取机器人 UIN 范围

        标签: 系统扩展

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "minUin": "12345678",
            "maxUin": "87654321"
          }
        ]
        """
        return await self.call_action("get_robot_uin_range", kwargs)

    async def get_friends_with_category(
        self, **kwargs: Unpack[GetFriendsWithCategoryPostRequest]
    ) -> GetFriendsWithCategoryPostResponse:
        """
        获取带分组的好友列表

        标签: 用户扩展

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "categoryId": 1,
            "categoryName": "我的好友",
            "categoryMbCount": 1,
            "buddyList": []
          }
        ]
        """
        return await self.call_action("get_friends_with_category", kwargs)

    async def delete_friend(
        self, **kwargs: Unpack[DeleteFriendPostRequest]
    ) -> DeleteFriendPostResponse:
        """
        删除好友

        描述:
        从好友列表中删除指定用户

        标签: Go-CQHTTP

        请求示例:
        {
          "user_id": "123456789"
        }
        """
        return await self.call_action("delete_friend", kwargs)

    async def check_url_safely(
        self, **kwargs: Unpack[CheckUrlSafelyPostRequest]
    ) -> CheckUrlSafelyPostResponse:
        """
        检查URL安全性 (未实现)

        描述:
        兼容接口，当前版本未实现 check_url_safely

        当前导出状态：未实现兼容接口，调用将返回业务错误。
        原因：当前版本未实现 check_url_safely

        标签: Go-CQHTTP

        请求示例:
        {
          "url": "https://example.com"
        }
        """
        return await self.call_action("check_url_safely", kwargs)

    async def get_online_clients(
        self, **kwargs: Unpack[GetOnlineClientsPostRequest]
    ) -> GetOnlineClientsPostResponse:
        """
        获取在线客户端 (未实现)

        描述:
        兼容接口，当前版本未实现 get_online_clients

        当前导出状态：未实现兼容接口，调用将返回业务错误。
        原因：当前版本未实现 get_online_clients

        标签: Go-CQHTTP

        请求示例:
        {}
        """
        return await self.call_action("get_online_clients", kwargs)

    async def ocr_image(
        self, **kwargs: Unpack[OcrImagePostRequest]
    ) -> OcrImagePostResponse:
        """
        图片 OCR 识别

        描述:
        识别图片中的文字内容(仅Windows端支持)

        标签: 扩展接口

        请求示例:
        {
          "image": "image_id_123"
        }

        成功响应 data 示例:
        {
          "texts": [
            {
              "text": "识别内容",
              "coordinates": []
            }
          ]
        }
        """
        return await self.call_action("ocr_image", kwargs)

    async def dot_ocr_image(
        self, **kwargs: Unpack[FieldOcrImagePostRequest]
    ) -> FieldOcrImagePostResponse:
        """
        图片 OCR 识别 (内部)

        描述:
        识别图片中的文字内容(仅Windows端支持)

        标签: 扩展接口

        请求示例:
        {
          "image": "image_id_123"
        }

        成功响应 data 示例:
        {
          "texts": [
            {
              "text": "识别内容",
              "coordinates": []
            }
          ]
        }
        """
        return await self.call_action(".ocr_image", kwargs)

    async def get_group_honor_info(
        self, **kwargs: Unpack[GetGroupHonorInfoPostRequest]
    ) -> GetGroupHonorInfoPostResponse:
        """
        获取群荣誉信息

        描述:
        获取指定群聊的荣誉信息，如龙王等

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "type": "all"
        }

        成功响应 data 示例:
        {
          "group_id": 123456,
          "current_talkative": {},
          "talkative_list": []
        }
        """
        return await self.call_action("get_group_honor_info", kwargs)

    async def _send_group_notice(
        self, **kwargs: Unpack[FieldSendGroupNoticePostRequest]
    ) -> FieldSendGroupNoticePostResponse:
        """
        发送群公告

        描述:
        在指定群聊中发布新的公告

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "content": "公告内容",
          "image": "base64://..."
        }
        """
        return await self.call_action("_send_group_notice", kwargs)

    async def _get_group_notice(
        self, **kwargs: Unpack[FieldGetGroupNoticePostRequest]
    ) -> FieldGetGroupNoticePostResponse:
        """
        获取群公告

        描述:
        获取指定群聊中的公告列表

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        [
          {
            "notice_id": "notice_123",
            "sender_id": 123456,
            "publish_time": 1710000000,
            "message": {
              "text": "公告内容",
              "image": []
            }
          }
        ]
        """
        return await self.call_action("_get_group_notice", kwargs)

    async def get_essence_msg_list(
        self, **kwargs: Unpack[GetEssenceMsgListPostRequest]
    ) -> GetEssenceMsgListPostResponse:
        """
        获取群精华消息

        描述:
        获取指定群聊中的精华消息列表

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        [
          {
            "message_id": 123456,
            "sender_id": 123456,
            "sender_nick": "昵称",
            "operator_id": 123456,
            "operator_nick": "昵称",
            "operator_time": 1710000000,
            "content": "精华内容"
          }
        ]
        """
        return await self.call_action("get_essence_msg_list", kwargs)

    async def get_group_at_all_remain(
        self, **kwargs: Unpack[GetGroupAtAllRemainPostRequest]
    ) -> GetGroupAtAllRemainPostResponse:
        """
        获取群艾特全体剩余次数

        描述:
        获取指定群聊中艾特全体成员的剩余次数

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        {
          "can_at_all": true,
          "remain_at_all_count_for_group": 10,
          "remain_at_all_count_for_self": 10
        }
        """
        return await self.call_action("get_group_at_all_remain", kwargs)

    async def send_forward_msg(
        self, **kwargs: Unpack[SendForwardMsgPostRequest]
    ) -> SendForwardMsgPostResponse:
        """
        发送合并转发消息

        描述:
        发送合并转发消息

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456789",
          "messages": []
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_forward_msg", kwargs)

    async def send_group_forward_msg(
        self, **kwargs: Unpack[SendGroupForwardMsgPostRequest]
    ) -> SendGroupForwardMsgPostResponse:
        """
        发送群合并转发消息

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456789",
          "messages": []
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_group_forward_msg", kwargs)

    async def send_private_forward_msg(
        self, **kwargs: Unpack[SendPrivateForwardMsgPostRequest]
    ) -> SendPrivateForwardMsgPostResponse:
        """
        发送私聊合并转发消息

        标签: Go-CQHTTP

        请求示例:
        {
          "user_id": "123456789",
          "messages": []
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_private_forward_msg", kwargs)

    async def get_stranger_info(
        self, **kwargs: Unpack[GetStrangerInfoPostRequest]
    ) -> GetStrangerInfoPostResponse:
        """
        获取陌生人信息

        描述:
        获取指定非好友用户的信息

        标签: Go-CQHTTP

        请求示例:
        {
          "user_id": "123456789"
        }

        成功响应 data 示例:
        {
          "user_id": 123456789,
          "nickname": "昵称",
          "sex": "unknown"
        }
        """
        return await self.call_action("get_stranger_info", kwargs)

    async def download_file(
        self, **kwargs: Unpack[DownloadFilePostRequest]
    ) -> DownloadFilePostResponse:
        """
        下载文件

        描述:
        下载网络文件到本地临时目录

        标签: Go-CQHTTP

        请求示例:
        {
          "url": "https://example.com/file.png",
          "thread_count": 1,
          "headers": "User-Agent: NapCat"
        }

        成功响应 data 示例:
        {
          "file": "/path/to/downloaded/file"
        }
        """
        return await self.call_action("download_file", kwargs)

    async def get_guild_list(
        self, **kwargs: Unpack[GetGuildListPostRequest]
    ) -> GetGuildListPostResponse:
        """
        获取频道列表 (未实现)

        描述:
        兼容接口，当前版本未实现 get_guild_list

        当前导出状态：未实现兼容接口，调用将返回业务错误。
        原因：当前版本未实现 get_guild_list

        标签: 频道接口

        请求示例:
        {}
        """
        return await self.call_action("get_guild_list", kwargs)

    async def mark_msg_as_read(
        self, **kwargs: Unpack[MarkMsgAsReadPostRequest]
    ) -> MarkMsgAsReadPostResponse:
        """
        标记消息已读 (Go-CQHTTP)

        描述:
        标记指定渠道的消息为已读

        标签: 消息接口

        请求示例:
        {
          "message_id": 12345
        }
        """
        return await self.call_action("mark_msg_as_read", kwargs)

    async def upload_group_file(
        self, **kwargs: Unpack[UploadGroupFilePostRequest]
    ) -> UploadGroupFilePostResponse:
        """
        上传群文件

        描述:
        上传资源路径或URL指定的文件到指定群聊的文件系统中

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "file": "/path/to/file",
          "name": "test.txt"
        }

        成功响应 data 示例:
        {
          "file_id": "file_uuid_123"
        }
        """
        return await self.call_action("upload_group_file", kwargs)

    async def get_group_msg_history(
        self, **kwargs: Unpack[GetGroupMsgHistoryPostRequest]
    ) -> GetGroupMsgHistoryPostResponse:
        """
        获取群历史消息

        描述:
        获取指定群聊的历史聊天记录

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "message_seq": 0,
          "count": 20
        }

        成功响应 data 示例:
        {
          "messages": []
        }
        """
        return await self.call_action("get_group_msg_history", kwargs)

    async def get_forward_msg(
        self, **kwargs: Unpack[GetForwardMsgPostRequest]
    ) -> GetForwardMsgPostResponse:
        """
        获取合并转发消息

        描述:
        获取合并转发消息的具体内容

        标签: Go-CQHTTP

        请求示例:
        {
          "message_id": "123456"
        }

        成功响应 data 示例:
        {
          "messages": []
        }
        """
        return await self.call_action("get_forward_msg", kwargs)

    async def get_friend_msg_history(
        self, **kwargs: Unpack[GetFriendMsgHistoryPostRequest]
    ) -> GetFriendMsgHistoryPostResponse:
        """
        获取好友历史消息

        描述:
        获取指定好友的历史聊天记录

        标签: Go-CQHTTP

        请求示例:
        {
          "user_id": "123456789",
          "message_seq": 0,
          "count": 20
        }

        成功响应 data 示例:
        {
          "messages": []
        }
        """
        return await self.call_action("get_friend_msg_history", kwargs)

    async def dot_handle_quick_operation(
        self, **kwargs: Unpack[FieldHandleQuickOperationPostRequest]
    ) -> FieldHandleQuickOperationPostResponse:
        """
        处理快速操作

        描述:
        处理来自事件上报的快速操作请求

        标签: Go-CQHTTP

        请求示例:
        {
          "context": {},
          "operation": {}
        }
        """
        return await self.call_action(".handle_quick_operation", kwargs)

    async def get_group_ignored_notifies(
        self, **kwargs: Unpack[GetGroupIgnoredNotifiesPostRequest]
    ) -> GetGroupIgnoredNotifiesPostResponse:
        """
        获取群忽略通知

        描述:
        获取被忽略的入群申请和邀请通知

        标签: 群组接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "invited_requests": [],
          "InvitedRequest": [],
          "join_requests": []
        }
        """
        return await self.call_action("get_group_ignored_notifies", kwargs)

    async def delete_essence_msg(
        self, **kwargs: Unpack[DeleteEssenceMsgPostRequest]
    ) -> DeleteEssenceMsgPostResponse:
        """
        移出精华消息

        描述:
        将一条消息从群精华消息列表中移出

        标签: 群组接口

        请求示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("delete_essence_msg", kwargs)

    async def set_essence_msg(
        self, **kwargs: Unpack[SetEssenceMsgPostRequest]
    ) -> SetEssenceMsgPostResponse:
        """
        设置精华消息

        描述:
        将一条消息设置为群精华消息

        标签: 群组接口

        请求示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("set_essence_msg", kwargs)

    async def get_recent_contact(
        self, **kwargs: Unpack[GetRecentContactPostRequest]
    ) -> GetRecentContactPostResponse:
        """
        获取最近会话

        描述:
        获取最近会话

        标签: 用户接口

        请求示例:
        {
          "count": 10
        }

        成功响应 data 示例:
        [
          {
            "peerUin": "123456",
            "peerName": "测试",
            "msgTime": "1734567890",
            "msgId": "12345",
            "lastestMsg": {}
          }
        ]
        """
        return await self.call_action("get_recent_contact", kwargs)

    async def _mark_all_as_read(
        self, **kwargs: Unpack[FieldMarkAllAsReadPostRequest]
    ) -> FieldMarkAllAsReadPostResponse:
        """
        标记所有消息已读

        标签: 消息接口

        请求示例:
        {}
        """
        return await self.call_action("_mark_all_as_read", kwargs)

    async def get_profile_like(
        self, **kwargs: Unpack[GetProfileLikePostRequest]
    ) -> GetProfileLikePostResponse:
        """
        获取资料点赞

        标签: 用户扩展

        请求示例:
        {
          "user_id": "123456789",
          "start": 0,
          "count": 10
        }

        成功响应 data 示例:
        {
          "uid": "u_123",
          "time": "1734567890",
          "favoriteInfo": {
            "userInfos": [],
            "total_count": 10,
            "last_time": 1734567890,
            "today_count": 5
          },
          "voteInfo": {
            "total_count": 100,
            "new_count": 2,
            "new_nearby_count": 0,
            "last_visit_time": 1734567890,
            "userInfos": []
          }
        }
        """
        return await self.call_action("get_profile_like", kwargs)

    async def set_group_portrait(
        self, **kwargs: Unpack[SetGroupPortraitPostRequest]
    ) -> SetGroupPortraitPostResponse:
        """
        设置群头像

        描述:
        修改指定群聊的头像

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "file": "base64://..."
        }

        成功响应 data 示例:
        {
          "result": 0,
          "errMsg": ""
        }
        """
        return await self.call_action("set_group_portrait", kwargs)

    async def fetch_custom_face(
        self, **kwargs: Unpack[FetchCustomFacePostRequest]
    ) -> FetchCustomFacePostResponse:
        """
        获取自定义表情

        标签: 系统扩展

        请求示例:
        {
          "count": 10
        }

        成功响应 data 示例:
        [
          "http://example.com/face1.png"
        ]
        """
        return await self.call_action("fetch_custom_face", kwargs)

    async def upload_private_file(
        self, **kwargs: Unpack[UploadPrivateFilePostRequest]
    ) -> UploadPrivateFilePostResponse:
        """
        上传私聊文件

        描述:
        上传本地文件到指定私聊会话中

        标签: Go-CQHTTP

        请求示例:
        {
          "user_id": "123456789",
          "file": "/path/to/file",
          "name": "test.txt"
        }

        成功响应 data 示例:
        {
          "file_id": "file_uuid_123"
        }
        """
        return await self.call_action("upload_private_file", kwargs)

    async def get_guild_service_profile(
        self, **kwargs: Unpack[GetGuildServiceProfilePostRequest]
    ) -> GetGuildServiceProfilePostResponse:
        """
        获取频道个人信息 (未实现)

        描述:
        兼容接口，当前版本未实现 get_guild_service_profile

        当前导出状态：未实现兼容接口，调用将返回业务错误。
        原因：当前版本未实现 get_guild_service_profile

        标签: 频道接口

        请求示例:
        {}
        """
        return await self.call_action("get_guild_service_profile", kwargs)

    async def _get_model_show(
        self, **kwargs: Unpack[FieldGetModelShowPostRequest]
    ) -> FieldGetModelShowPostResponse:
        """
        获取机型显示

        描述:
        获取当前账号可用的设备机型显示名称列表

        标签: Go-CQHTTP

        请求示例:
        {
          "model": "iPhone 13"
        }

        成功响应 data 示例:
        [
          {
            "variants": {
              "model_show": "napcat",
              "need_pay": false
            }
          }
        ]
        """
        return await self.call_action("_get_model_show", kwargs)

    async def _set_model_show(
        self, **kwargs: Unpack[FieldSetModelShowPostRequest]
    ) -> FieldSetModelShowPostResponse:
        """
        设置机型 (未实现)

        描述:
        兼容接口，当前版本未实现 _set_model_show

        当前导出状态：未实现兼容接口，调用将返回业务错误。
        原因：当前版本未实现 _set_model_show

        标签: Go-CQHTTP

        请求示例:
        {}
        """
        return await self.call_action("_set_model_show", kwargs)

    async def set_input_status(
        self, **kwargs: Unpack[SetInputStatusPostRequest]
    ) -> SetInputStatusPostResponse:
        """
        设置输入状态

        标签: 系统扩展

        请求示例:
        {
          "user_id": "123456789",
          "event_type": 1
        }
        """
        return await self.call_action("set_input_status", kwargs)

    async def get_csrf_token(
        self, **kwargs: Unpack[GetCsrfTokenPostRequest]
    ) -> GetCsrfTokenPostResponse:
        """
        获取 CSRF Token

        描述:
        获取 CSRF Token

        标签: 系统接口

        请求示例:
        {}

        成功响应 data 示例:
        {
          "token": 123456789
        }
        """
        return await self.call_action("get_csrf_token", kwargs)

    async def get_credentials(
        self, **kwargs: Unpack[GetCredentialsPostRequest]
    ) -> GetCredentialsPostResponse:
        """
        获取登录凭证

        描述:
        获取登录凭证

        标签: 系统接口

        请求示例:
        {
          "domain": "qun.qq.com"
        }

        成功响应 data 示例:
        {
          "cookies": "uin=o123456789; skey=@abc12345;",
          "token": 123456789
        }
        """
        return await self.call_action("get_credentials", kwargs)

    async def _del_group_notice(
        self, **kwargs: Unpack[FieldDelGroupNoticePostRequest]
    ) -> FieldDelGroupNoticePostResponse:
        """
        删除群公告

        描述:
        删除群聊中的公告

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456",
          "notice_id": "notice_123"
        }
        """
        return await self.call_action("_del_group_notice", kwargs)

    async def delete_group_file(
        self, **kwargs: Unpack[DeleteGroupFilePostRequest]
    ) -> DeleteGroupFilePostResponse:
        """
        删除群文件

        描述:
        在群文件系统中删除指定的文件

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "file_id": "file_uuid_123"
        }
        """
        return await self.call_action("delete_group_file", kwargs)

    async def create_group_file_folder(
        self, **kwargs: Unpack[CreateGroupFileFolderPostRequest]
    ) -> CreateGroupFileFolderPostResponse:
        """
        创建群文件目录

        描述:
        在群文件系统中创建新的文件夹

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456789",
          "folder_name": "新建文件夹"
        }

        成功响应 data 示例:
        {
          "result": {},
          "groupItem": {}
        }
        """
        return await self.call_action("create_group_file_folder", kwargs)

    async def delete_group_folder(
        self, **kwargs: Unpack[DeleteGroupFolderPostRequest]
    ) -> DeleteGroupFolderPostResponse:
        """
        删除群文件目录

        描述:
        在群文件系统中删除指定的文件夹

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "folder_id": "folder_uuid_123"
        }
        """
        return await self.call_action("delete_group_folder", kwargs)

    async def get_group_file_system_info(
        self, **kwargs: Unpack[GetGroupFileSystemInfoPostRequest]
    ) -> GetGroupFileSystemInfoPostResponse:
        """
        获取群文件系统信息

        描述:
        获取群聊文件系统的空间及状态信息

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        {
          "file_count": 10,
          "limit_count": 10000,
          "used_space": 1024,
          "total_space": 10737418240
        }
        """
        return await self.call_action("get_group_file_system_info", kwargs)

    async def get_group_files_by_folder(
        self, **kwargs: Unpack[GetGroupFilesByFolderPostRequest]
    ) -> GetGroupFilesByFolderPostResponse:
        """
        获取群文件夹文件列表

        描述:
        获取指定群文件夹下的文件及子文件夹列表

        标签: Go-CQHTTP

        请求示例:
        {
          "group_id": "123456",
          "folder_id": "folder_id"
        }

        成功响应 data 示例:
        {
          "files": [],
          "folders": []
        }
        """
        return await self.call_action("get_group_files_by_folder", kwargs)

    async def nc_get_packet_status(
        self, **kwargs: Unpack[NcGetPacketStatusPostRequest]
    ) -> NcGetPacketStatusPostResponse:
        """
        获取Packet状态

        描述:
        获取底层Packet服务的运行状态

        标签: 系统接口

        请求示例:
        {}
        """
        return await self.call_action("nc_get_packet_status", kwargs)

    async def set_restart(
        self, **kwargs: Unpack[SetRestartPostRequest]
    ) -> SetRestartPostResponse:
        """
        重启服务

        描述:
        重启服务

        标签: 系统接口

        请求示例:
        {}
        """
        return await self.call_action("set_restart", kwargs)

    async def group_poke(
        self, **kwargs: Unpack[GroupPokePostRequest]
    ) -> GroupPokePostResponse:
        """
        发送戳一戳

        描述:
        在群聊或私聊中发送戳一戳动作

        标签: 核心接口

        请求示例:
        {
          "user_id": "123456789"
        }
        """
        return await self.call_action("group_poke", kwargs)

    async def friend_poke(
        self, **kwargs: Unpack[FriendPokePostRequest]
    ) -> FriendPokePostResponse:
        """
        发送戳一戳

        描述:
        在群聊或私聊中发送戳一戳动作

        标签: 核心接口

        请求示例:
        {
          "user_id": "123456789"
        }
        """
        return await self.call_action("friend_poke", kwargs)

    async def nc_get_user_status(
        self, **kwargs: Unpack[NcGetUserStatusPostRequest]
    ) -> NcGetUserStatusPostResponse:
        """
        获取用户在线状态

        标签: 系统扩展

        请求示例:
        {
          "user_id": "123456789"
        }

        成功响应 data 示例:
        {
          "status": 10,
          "ext_status": 0
        }
        """
        return await self.call_action("nc_get_user_status", kwargs)

    async def nc_get_rkey(
        self, **kwargs: Unpack[NcGetRkeyPostRequest]
    ) -> NcGetRkeyPostResponse:
        """
        获取 RKey

        标签: 系统扩展

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "key": "rkey_value",
            "expired": 1734567890
          }
        ]
        """
        return await self.call_action("nc_get_rkey", kwargs)

    async def set_group_special_title(
        self, **kwargs: Unpack[SetGroupSpecialTitlePostRequest]
    ) -> SetGroupSpecialTitlePostResponse:
        """
        设置专属头衔

        描述:
        设置群聊中指定成员的专属头衔

        标签: 扩展接口

        请求示例:
        {
          "group_id": "123456",
          "user_id": "123456789",
          "special_title": "头衔"
        }
        """
        return await self.call_action("set_group_special_title", kwargs)

    async def set_diy_online_status(
        self, **kwargs: Unpack[SetDiyOnlineStatusPostRequest]
    ) -> SetDiyOnlineStatusPostResponse:
        """
        设置自定义在线状态

        描述:
        设置自定义在线状态

        标签: 用户扩展

        请求示例:
        {
          "face_id": "123",
          "face_type": "1",
          "wording": "自定义状态"
        }

        成功响应 data 示例:
        ""
        """
        return await self.call_action("set_diy_online_status", kwargs)

    async def get_group_shut_list(
        self, **kwargs: Unpack[GetGroupShutListPostRequest]
    ) -> GetGroupShutListPostResponse:
        """
        获取群禁言列表

        标签: 群组接口

        请求示例:
        {
          "group_id": "123456789"
        }

        成功响应 data 示例:
        [
          {
            "user_id": 123456789,
            "nickname": "禁言用户",
            "shut_up_time": 1734567890
          }
        ]
        """
        return await self.call_action("get_group_shut_list", kwargs)

    async def get_group_file_url(
        self, **kwargs: Unpack[GetGroupFileUrlPostRequest]
    ) -> GetGroupFileUrlPostResponse:
        """
        获取群文件URL

        描述:
        获取指定群文件的下载链接

        标签: 文件接口

        请求示例:
        {
          "group_id": "123456",
          "file_id": "file_id_123",
          "busid": 102
        }

        成功响应 data 示例:
        {
          "url": "http://..."
        }
        """
        return await self.call_action("get_group_file_url", kwargs)

    async def get_mini_app_ark(
        self, payload: GetMiniAppArkPostRequest
    ) -> GetMiniAppArkPostResponse:
        """
        获取小程序 Ark

        标签: 系统扩展

        请求示例:
        {
          "type": "bili",
          "title": "测试标题",
          "desc": "测试描述",
          "picUrl": "http://example.com/pic.jpg",
          "jumpUrl": "http://example.com"
        }

        成功响应 data 示例:
        {
          "data": {
            "ark": "ark_content"
          }
        }
        """
        return await self.call_action("get_mini_app_ark", payload)

    async def get_ai_record(
        self, **kwargs: Unpack[GetAiRecordPostRequest]
    ) -> GetAiRecordPostResponse:
        """
        获取 AI 语音

        描述:
        通过 AI 语音引擎获取指定文本的语音 URL

        标签: AI 扩展

        请求示例:
        {
          "character": "ai_char_1",
          "group_id": "123456",
          "text": "你好"
        }

        成功响应 data 示例:
        "http://example.com/ai_voice.silk"
        """
        return await self.call_action("get_ai_record", kwargs)

    async def send_group_ai_record(
        self, **kwargs: Unpack[SendGroupAiRecordPostRequest]
    ) -> SendGroupAiRecordPostResponse:
        """
        发送群 AI 语音

        描述:
        发送 AI 生成的语音到指定群聊

        标签: AI 扩展

        请求示例:
        {
          "character": "ai_char_1",
          "group_id": "123456",
          "text": "你好"
        }
        """
        return await self.call_action("send_group_ai_record", kwargs)

    async def get_ai_characters(
        self, **kwargs: Unpack[GetAiCharactersPostRequest]
    ) -> GetAiCharactersPostResponse:
        """
        获取AI角色列表

        描述:
        获取群聊中的AI角色列表

        标签: 扩展接口

        请求示例:
        {
          "group_id": "123456"
        }

        成功响应 data 示例:
        [
          {
            "type": "string",
            "characters": [
              {
                "character_id": "id",
                "character_name": "name",
                "preview_url": "url"
              }
            ]
          }
        ]
        """
        return await self.call_action("get_ai_characters", kwargs)

    async def send_packet(
        self, **kwargs: Unpack[SendPacketPostRequest]
    ) -> SendPacketPostResponse:
        """
        发送原始数据包

        标签: 系统扩展

        请求示例:
        {
          "cmd": "Example.Cmd",
          "data": "123456",
          "rsp": true
        }

        成功响应 data 示例:
        "123456"
        """
        return await self.call_action("send_packet", kwargs)

    async def send_poke(
        self, **kwargs: Unpack[SendPokePostRequest]
    ) -> SendPokePostResponse:
        """
        发送戳一戳

        描述:
        在群聊或私聊中发送戳一戳动作

        标签: 核心接口

        请求示例:
        {
          "user_id": "123456789"
        }
        """
        return await self.call_action("send_poke", kwargs)

    async def get_group_system_msg(
        self, **kwargs: Unpack[GetGroupSystemMsgPostRequest]
    ) -> GetGroupSystemMsgPostResponse:
        """
        获取群系统消息

        描述:
        获取群系统消息

        标签: 系统接口

        请求示例:
        {
          "count": 50
        }

        成功响应 data 示例:
        {
          "invited_requests": [],
          "InvitedRequest": [],
          "join_requests": []
        }
        """
        return await self.call_action("get_group_system_msg", kwargs)

    async def bot_exit(
        self, **kwargs: Unpack[BotExitPostRequest]
    ) -> BotExitPostResponse:
        """
        退出登录

        标签: 系统扩展

        请求示例:
        {}
        """
        return await self.call_action("bot_exit", kwargs)

    async def click_inline_keyboard_button(
        self, **kwargs: Unpack[ClickInlineKeyboardButtonPostRequest]
    ) -> ClickInlineKeyboardButtonPostResponse:
        """
        点击内联键盘按钮

        标签: 消息扩展

        请求示例:
        {
          "group_id": "123456",
          "bot_appid": "1234567890",
          "button_id": "btn_1",
          "callback_data": "",
          "msg_seq": "10086"
        }
        """
        return await self.call_action("click_inline_keyboard_button", kwargs)

    async def get_private_file_url(
        self, **kwargs: Unpack[GetPrivateFileUrlPostRequest]
    ) -> GetPrivateFileUrlPostResponse:
        """
        获取私聊文件URL

        描述:
        获取指定私聊文件的下载链接

        标签: 文件接口

        请求示例:
        {
          "user_id": "123456789",
          "file_id": "file_id_123"
        }

        成功响应 data 示例:
        {
          "url": "http://..."
        }
        """
        return await self.call_action("get_private_file_url", kwargs)

    async def get_unidirectional_friend_list(
        self, **kwargs: Unpack[GetUnidirectionalFriendListPostRequest]
    ) -> GetUnidirectionalFriendListPostResponse:
        """
        获取单向好友列表

        标签: 用户扩展

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "uin": 123456789,
            "uid": "u_123",
            "nick_name": "单向好友",
            "age": 20,
            "source": "来源"
          }
        ]
        """
        return await self.call_action("get_unidirectional_friend_list", kwargs)

    async def clean_cache(
        self, **kwargs: Unpack[CleanCachePostRequest]
    ) -> CleanCachePostResponse:
        """
        清理缓存

        描述:
        清理缓存

        标签: 系统接口

        请求示例:
        {}
        """
        return await self.call_action("clean_cache", kwargs)

    async def get_group_ignore_add_request(
        self, **kwargs: Unpack[GetGroupIgnoreAddRequestPostRequest]
    ) -> GetGroupIgnoreAddRequestPostResponse:
        """
        获取群被忽略的加群请求

        标签: 群组接口

        请求示例:
        {}

        成功响应 data 示例:
        [
          {
            "request_id": 12345,
            "invitor_uin": 123456789,
            "invitor_nick": "邀请者",
            "group_id": 123456789,
            "message": "加群请求",
            "group_name": "群名称",
            "checked": false,
            "actor": 0,
            "requester_nick": "请求者"
          }
        ]
        """
        return await self.call_action("get_group_ignore_add_request", kwargs)

    async def get_collection_list(
        self, **kwargs: Unpack[GetCollectionListPostRequest]
    ) -> GetCollectionListPostResponse:
        """
        获取收藏列表

        标签: 系统扩展

        请求示例:
        {
          "category": "0",
          "count": "50"
        }

        成功响应 data 示例:
        {
          "errCode": 0,
          "errMsg": "",
          "collectionSearchList": {
            "collectionItemList": [
              {
                "cid": "123456",
                "type": 8,
                "status": 1,
                "author": {
                  "type": 2,
                  "numId": "123456",
                  "strId": "昵称",
                  "groupId": "123456",
                  "groupName": "群名",
                  "uid": "123456"
                },
                "bid": 1,
                "category": 1,
                "createTime": "1769169157000",
                "collectTime": "1769413477691",
                "modifyTime": "1769413477691",
                "sequence": "1769413476735",
                "shareUrl": "",
                "customGroupId": 0,
                "securityBeat": false,
                "summary": {
                  "textSummary": null,
                  "linkSummary": null,
                  "gallerySummary": null,
                  "audioSummary": null,
                  "videoSummary": null,
                  "fileSummary": null,
                  "locationSummary": null,
                  "richMediaSummary": {
                    "title": "",
                    "subTitle": "",
                    "brief": "text",
                    "picList": [],
                    "contentType": 1,
                    "originalUri": "",
                    "publisher": "",
                    "richMediaVersion": 0
                  }
                }
              }
            ],
            "hasMore": false,
            "bottomTimeStamp": "1769413477691"
          }
        }
        """
        return await self.call_action("get_collection_list", kwargs)

    async def create_flash_task(
        self, **kwargs: Unpack[CreateFlashTaskPostRequest]
    ) -> CreateFlashTaskPostResponse:
        """
        创建闪传任务

        标签: 文件扩展

        请求示例:
        {
          "files": "C:\\test.jpg",
          "name": "test_task"
        }

        成功响应 data 示例:
        {
          "task_id": "task_123"
        }
        """
        return await self.call_action("create_flash_task", kwargs)

    async def get_flash_file_list(
        self, **kwargs: Unpack[GetFlashFileListPostRequest]
    ) -> GetFlashFileListPostResponse:
        """
        获取闪传文件列表

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123"
        }

        成功响应 data 示例:
        [
          {
            "file_name": "test.jpg",
            "size": 1024
          }
        ]
        """
        return await self.call_action("get_flash_file_list", kwargs)

    async def get_flash_file_url(
        self, **kwargs: Unpack[GetFlashFileUrlPostRequest]
    ) -> GetFlashFileUrlPostResponse:
        """
        获取闪传文件链接

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123"
        }

        成功响应 data 示例:
        {
          "url": "http://example.com/flash.jpg"
        }
        """
        return await self.call_action("get_flash_file_url", kwargs)

    async def send_flash_msg(
        self, **kwargs: Unpack[SendFlashMsgPostRequest]
    ) -> SendFlashMsgPostResponse:
        """
        发送闪传消息

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123",
          "user_id": "123456789"
        }

        成功响应 data 示例:
        {
          "message_id": 123456
        }
        """
        return await self.call_action("send_flash_msg", kwargs)

    async def get_share_link(
        self, **kwargs: Unpack[GetShareLinkPostRequest]
    ) -> GetShareLinkPostResponse:
        """
        获取文件分享链接

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123"
        }

        成功响应 data 示例:
        "http://example.com/share"
        """
        return await self.call_action("get_share_link", kwargs)

    async def get_fileset_info(
        self, **kwargs: Unpack[GetFilesetInfoPostRequest]
    ) -> GetFilesetInfoPostResponse:
        """
        获取文件集信息

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123"
        }

        成功响应 data 示例:
        {
          "fileset_id": "set_123",
          "file_list": []
        }
        """
        return await self.call_action("get_fileset_info", kwargs)

    async def get_online_file_msg(
        self, **kwargs: Unpack[GetOnlineFileMsgPostRequest]
    ) -> GetOnlineFileMsgPostResponse:
        """
        获取在线文件消息

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789"
        }
        """
        return await self.call_action("get_online_file_msg", kwargs)

    async def send_online_file(
        self, **kwargs: Unpack[SendOnlineFilePostRequest]
    ) -> SendOnlineFilePostResponse:
        """
        发送在线文件

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789",
          "file_path": "C:\\path\\to\\file.txt",
          "file_name": "test.txt"
        }
        """
        return await self.call_action("send_online_file", kwargs)

    async def send_online_folder(
        self, **kwargs: Unpack[SendOnlineFolderPostRequest]
    ) -> SendOnlineFolderPostResponse:
        """
        发送在线文件夹

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789",
          "folder_path": "C:\\path\\to\\folder"
        }
        """
        return await self.call_action("send_online_folder", kwargs)

    async def receive_online_file(
        self, **kwargs: Unpack[ReceiveOnlineFilePostRequest]
    ) -> ReceiveOnlineFilePostResponse:
        """
        接收在线文件

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789",
          "msg_id": "123",
          "element_id": "456"
        }
        """
        return await self.call_action("receive_online_file", kwargs)

    async def refuse_online_file(
        self, **kwargs: Unpack[RefuseOnlineFilePostRequest]
    ) -> RefuseOnlineFilePostResponse:
        """
        拒绝在线文件

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789",
          "msg_id": "123"
        }
        """
        return await self.call_action("refuse_online_file", kwargs)

    async def cancel_online_file(
        self, **kwargs: Unpack[CancelOnlineFilePostRequest]
    ) -> CancelOnlineFilePostResponse:
        """
        取消在线文件

        标签: 文件扩展

        请求示例:
        {
          "user_id": "123456789",
          "msg_id": "123"
        }
        """
        return await self.call_action("cancel_online_file", kwargs)

    async def download_fileset(
        self, **kwargs: Unpack[DownloadFilesetPostRequest]
    ) -> DownloadFilesetPostResponse:
        """
        下载文件集

        标签: 文件扩展

        请求示例:
        {
          "fileset_id": "set_123"
        }
        """
        return await self.call_action("download_fileset", kwargs)

    async def get_fileset_id(
        self, **kwargs: Unpack[GetFilesetIdPostRequest]
    ) -> GetFilesetIdPostResponse:
        """
        获取文件集 ID

        标签: 文件扩展

        请求示例:
        {
          "share_code": "123456"
        }

        成功响应 data 示例:
        {
          "fileset_id": "set_123"
        }
        """
        return await self.call_action("get_fileset_id", kwargs)
