from datetime import datetime

from pydantic import Field

from schemas.base import CamelCaseSchema


class NotificationResponse(CamelCaseSchema):
    id: int
    title: str
    message: str
    created_at: datetime
    read: bool = Field(validation_alias="is_read")


class UnreadCountResponse(CamelCaseSchema):
    count: int


class MarkAllReadResponse(CamelCaseSchema):
    updated: int
