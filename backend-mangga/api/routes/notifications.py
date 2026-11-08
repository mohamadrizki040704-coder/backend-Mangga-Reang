from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_current_user
from crud import notifications
from db.session import get_db
from models.domain_models import User
from schemas.notification import (
    MarkAllReadResponse,
    NotificationResponse,
    UnreadCountResponse,
)


router = APIRouter()


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    unread_only: bool = Query(default=False),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    return notifications.list_for_user(
        db, user.id, unread_only=unread_only, offset=offset, limit=limit
    )


@router.get("/unread-count", response_model=UnreadCountResponse)
def unread_count(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> UnreadCountResponse:
    return UnreadCountResponse(count=notifications.count_unread(db, user.id))


@router.put("/read-all", response_model=MarkAllReadResponse)
def read_all(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MarkAllReadResponse:
    updated = notifications.mark_all_read(db, user.id)
    db.commit()
    return MarkAllReadResponse(updated=updated)


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def read_one(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> NotificationResponse:
    item = notifications.get_for_user(db, user.id, notification_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    item.is_read = True
    db.commit()
    db.refresh(item)
    return item
