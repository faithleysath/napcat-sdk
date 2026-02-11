"""
NapCat SDK exception hierarchy.

Use these to distinguish API failures, protocol/data issues, and runtime state errors.
"""

from __future__ import annotations

from typing import Any


class NapCatError(Exception):
    """Base exception for all NapCat SDK errors."""


class NapCatAPIError(NapCatError):
    """API call failed with a non-ok response or non-zero retcode."""

    def __init__(
        self,
        message: str,
        *,
        action: str | None = None,
        retcode: int | None = None,
        response: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.action = action
        self.retcode = retcode
        self.response = response


class NapCatProtocolError(NapCatError, ValueError):
    """Inbound event/data payload does not conform to expected schema."""


class NapCatStateError(NapCatError, RuntimeError):
    """SDK is used in an invalid lifecycle state (e.g., not connected)."""
