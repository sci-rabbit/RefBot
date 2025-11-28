from sqlalchemy import String, LargeBinary, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    message_id: Mapped[BigInteger] = mapped_column(
        BigInteger,
        nullable=False,
        unique=True,
    )
    media_group_id: Mapped[BigInteger] = mapped_column(
        BigInteger, nullable=True, index=True
    )
    token_file: Mapped[str] = mapped_column(String, nullable=True)
    hash_tags: Mapped[str] = mapped_column(String, nullable=True)
    photo: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)

    __table_args__ = (
        Index(
            "ix_messages_hash_tags_trgm",
            "hash_tags",
            postgresql_using="gin",
            postgresql_ops={"hash_tags": "gin_trgm_ops"},
        ),
    )
