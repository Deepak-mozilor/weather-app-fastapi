from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Boolean, String

from weather.db.base import Base


class User(Base):
    """Model for demo purpose."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(length=200), index=True, unique=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(length=200), index=True, unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=200), index=True, unique=True, nullable=False
    )
    is_active = mapped_column(Boolean, default=True)
