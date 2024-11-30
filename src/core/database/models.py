from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "study_groups"
    id: Mapped[int] = mapped_column(primary_key=True)
    group_type: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(30))


class Schedule(Base):
    __tablename__ = "schedule"
    id: Mapped[int] = mapped_column(primary_key=True)
    schedule_type: Mapped[str] = mapped_column(String(30))
    group_name: Mapped[str] = mapped_column(String(30))
    day: Mapped[str] = mapped_column(String(30))
    lesson_number: Mapped[str] = mapped_column(String(30))
    lesson_time: Mapped[str] = mapped_column(String(30))
    lesson_title: Mapped[str] = mapped_column(String(100))
