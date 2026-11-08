from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from crud import notifications
from models.domain_models import (
    LogisticsMilestone,
    Notification,
    RfqTransaction,
    Role,
    User,
)

MILESTONE_LABELS = {
    LogisticsMilestone.DIPROSES_PETANI: "Pesanan sedang diproses petani",
    LogisticsMilestone.SORTIR_GUDANG: "Pesanan sedang disortir di gudang",
    LogisticsMilestone.IN_TRANSIT: "Pesanan sedang dalam pengiriman",
    LogisticsMilestone.DELIVERED: "Pesanan sudah sampai di tujuan",
}


def _tonase(value: Decimal) -> str:
    return format(Decimal(value).normalize(), "f")


def _rupiah(value: Decimal) -> str:
    return "Rp" + f"{int(value):,}".replace(",", ".")


def notify(db: Session, user_id: int, title: str, message: str) -> Notification:
    """Buat notifikasi. Ikut transaksi pemanggil (commit dilakukan oleh route)."""
    return notifications.create(
        db,
        Notification(user_id=user_id, title=title[:150], message=message[:1000]),
    )


def notify_admins(db: Session, title: str, message: str) -> None:
    admin_ids = db.scalars(select(User.id).where(User.role == Role.ADMIN_GUDANG))
    for admin_id in admin_ids:
        notify(db, admin_id, title, message)


def notify_welcome(db: Session, user: User) -> None:
    notify(
        db,
        user.id,
        "Selamat datang di Juragan Mangga Reang",
        f"Halo {user.nama_lengkap}, akunmu berhasil dibuat. Selamat berbelanja mangga!",
    )


def notify_rfq_created(db: Session, order: RfqTransaction, buyer_name: str | None = None) -> None:
    detail = f"{_tonase(order.tonase_diminta)} ton dengan total {_rupiah(order.total_harga)}"
    notify(
        db,
        order.id_buyer,
        "Permintaan penawaran terkirim",
        f"Permintaan #{order.id} sebanyak {detail} menunggu persetujuan admin gudang.",
    )
    who = f" dari {buyer_name}" if buyer_name else ""
    notify_admins(
        db,
        "Permintaan penawaran baru",
        f"Ada permintaan #{order.id}{who} sebanyak {detail} yang perlu ditinjau.",
    )


def notify_rfq_approved(db: Session, order: RfqTransaction) -> None:
    notify(
        db,
        order.id_buyer,
        "Penawaran disetujui",
        f"Permintaan #{order.id} sebanyak {_tonase(order.tonase_diminta)} ton telah disetujui. "
        "Pesananmu mulai diproses.",
    )


def notify_tracking_update(
    db: Session, order: RfqTransaction, milestone: LogisticsMilestone
) -> None:
    notify(
        db,
        order.id_buyer,
        "Status pengiriman diperbarui",
        f"Pesanan #{order.id}: {MILESTONE_LABELS.get(milestone, milestone.value)}.",
    )
