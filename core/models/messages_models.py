from sqlalchemy import TIME, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(String(length=1000), nullable=False)
    time_send: Mapped[TIME] = mapped_column(TIME)

    user = relationship("Users", back_populates="message")

    def __str__(self):
        return f"Message: {self.message}"
