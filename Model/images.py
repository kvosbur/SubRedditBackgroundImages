from Model import Base
from sqlalchemy import Column, Integer, Text, Date, Sequence


class Images(Base):
    __tablename__ = "images"

    imageId = Column(Integer, primary_key=True)
    postURL = Column(Text)
    imagePath = Column(Text)
    dateReceived = Column(Date)
    blackListedDate = Column(Date)

    def __init__(self, postURL, imagePath, dateReceived, blackListedDate):
        self.postURL = postURL
        self.imagePath = imagePath
        self.dateReceived = dateReceived
        self.blackListedDate = blackListedDate



