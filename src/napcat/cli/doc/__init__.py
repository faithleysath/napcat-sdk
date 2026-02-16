"""
NapCat 文档查询模块

提供 API 文档、源码和类定义查询功能。
"""

from .logic import (
    ApiDoc,
    logic_get_class_detail,
    logic_get_class_details,
    logic_get_code_file,
    logic_get_code_index,
    logic_get_details,
    logic_get_index,
    logic_get_llms_txt,
    logic_get_missing_apis,
    logic_get_missing_classes,
)

__all__ = [
    "ApiDoc",
    "logic_get_index",
    "logic_get_details",
    "logic_get_code_index",
    "logic_get_code_file",
    "logic_get_class_detail",
    "logic_get_class_details",
    "logic_get_llms_txt",
    "logic_get_missing_apis",
    "logic_get_missing_classes",
]
