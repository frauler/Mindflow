from __future__ import annotations
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import Base
from typing import List

class User(Base):
    __tablename__ = "tblUsers"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    passhash: Mapped[str] = mapped_column(String(100), nullable=False)
    admin_id: Mapped[int] = mapped_column(ForeignKey("tblAdmins.admin_id"))

    admin: Mapped["Admin"] = relationship(back_populates="users")
    user: Mapped["UserData"] = relationship(back_populates="user_data")
    statistics: Mapped[List["Statistic"]] = relationship(back_populates="user")

from app.models.admin import Admin
from app.models.userdata import UserData
from app.models.statistic import Statistic