from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, TIME
from core.database import Base


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    message: Mapped[str] = mapped_column(String(length=1000), nullable=False)
    time_sent: Mapped[TIME] = mapped_column(TIME)
