from Model import Base
from sqlalchemy import Column, Integer, ForeignKey, Sequence


class Combined(Base):
    __tablename__ = "combined"

    combineId = Column(Integer, primary_key=True, autoincrement=True)
    imageId = Column(Integer, ForeignKey("images.imageId", ondelete="CASCADE"), primary_key=True, nullable=False)
    position = Column(Integer, nullable=False)

    def __init__(self, combineId, imageId, position):
        self.combineId = combineId
        self.imageId = imageId
        self.position = position





