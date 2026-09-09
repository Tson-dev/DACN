from sqlalchemy import Column, Integer, String

from backend.database import Base


class Role(Base):
    __tablename__ = "role"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    desc = Column(String(255))
