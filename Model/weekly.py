from Model import Base
from sqlalchemy import Column, Integer, ForeignKey, Sequence


class Weekly(Base):
    __tablename__ = "weekly"

    weeklyId = Column(Integer, primary_key=True)
    imageId = Column(Integer, ForeignKey("images.imageId", ondelete="CASCADE"))
    combineId = Column(Integer, ForeignKey("combined.combineId", ondelete="CASCADE"))
    isCurrent = Column(Integer, nullable=False)

    def __init__(self, imageId, combineId, isCurrent):
        self.imageId = imageId
        self.combineId = combineId
        self.isCurrent = isCurrent





