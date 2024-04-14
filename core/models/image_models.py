from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey
from core.database import Base


class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(String())


