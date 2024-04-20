from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(length=200), nullable=False)
    role: Mapped[int]

    message = relationship("Messages", back_populates="user")

    def __str__(self):
        return f"Name: {self.name}"
