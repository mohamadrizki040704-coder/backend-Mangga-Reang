from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from models.domain_models import Notification


def create(db: Session, notification: Notification) -> Notification:
    db.add(notification)
    db.flush()
    return notification


def list_for_user(
    db: Session,
    user_id: int,
    *,
    unread_only: bool = False,
    offset: int = 0,
    limit: int = 50,
) -> list[Notification]:
    query = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        query = query.where(Notification.is_read.is_(False))
    query = (
        query.order_by(Notification.created_at.desc(), Notification.id.desc())
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(query))


def get_for_user(db: Session, user_id: int, notification_id: int) -> Notification | None:
    return db.scalar(
        select(Notification).where(
            Notification.id == notification_id, Notification.user_id == user_id
        )
    )


def count_unread(db: Session, user_id: int) -> int:
    return int(
        db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        )
        or 0
    )


def mark_all_read(db: Session, user_id: int) -> int:
    result = db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read.is_(False))
        .values(is_read=True)
    )
    return int(result.rowcount or 0)
