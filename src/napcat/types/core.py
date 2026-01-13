# src/napcat/types/core.py

from dataclasses import dataclass
from typing import Any, Literal

from .responses import ResponseDataBase
from .utils import IgnoreExtraArgsMixin, TypeValidatorMixin


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatRequest(TypeValidatorMixin, IgnoreExtraArgsMixin):
    action: str
    params: dict[str, Any]
    echo: str | None = None


@dataclass(slots=True, frozen=True, kw_only=True)
class NapCatResponse[T: ResponseDataBase](TypeValidatorMixin, IgnoreExtraArgsMixin):
    """
    OneBot 响应通用包装类
    T: 具体的 data 类型 (例如 LoginInfoData)
    """

    status: Literal["ok", "failed"]
    retcode: int
    data: T | dict[str, Any]  # 泛型字段
    message: str = ""
    wording: str = ""
    echo: str | None = None

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],  # <--- 修正点：必须叫 data，与 Mixin 保持一致
        data_type: type[T] | None = None,
    ) -> NapCatResponse[T]:
        """
        从字典构建响应对象，并尝试自动解析 data 字段
        :param data: 原始字典数据 (API 返回的完整 JSON)
        :param data_type: 期望的 data 数据类型
        """
        # 为了防止混淆，先把字典里的 payload data 取个别名
        raw_payload: dict[str, Any] = data.get("data", {})
        parsed_payload = raw_payload

        # 核心逻辑：如果指定了类型且数据是字典，尝试递归解析
        if data_type and raw_payload != {}:
            parsed_payload = data_type.from_dict(raw_payload)

        return cls(
            status=data.get("status", "failed"),
            retcode=data.get("retcode", -1),
            data=parsed_payload,
            message=data.get("message", ""),
            wording=data.get("wording", ""),
            echo=data.get("echo"),
        )

    @property
    def is_ok(self) -> bool:
        return self.status == "ok" and self.retcode == 0

    @property
    def result(self) -> T | dict[str, Any]:
        if not self.is_ok:
            raise RuntimeError(f"API Error {self.retcode}: {self.message}")
        return self.data
