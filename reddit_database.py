import sqlite3
from util import base_directory, current_date_string, parse_date_string
import os
import datetime
from typing import List
from reddit_image import RedditImage
from combine_image import CombineImages
from Model import Base, combined
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import sessionmaker

DBFilePath = os.path.join(base_directory, "PictureSource", os.environ["DBFileName"])
engine = create_engine('sqlite:///' + DBFilePath)
Base.metadata.create_all(engine)

class RedditDatabase:
    # static variables
    Singleton = None

    # object variables
    connection = None

    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def get_next_combineid(self):
        res = self.session.query(func.max(combined.Combined.combineId)).one()
        if res[0] is None:
            return 1
        else:
            return None

    def insert_all_combined(self, all_combined_object: List[CombineImages]):
        [self.insert_combined(x) for x in all_combined_object]

    def insert_combined(self, combined_object: CombineImages):
        images = combined_object.get_selected_images()
        combine_id = self.get_next_combineid()
        objects = []
        for index, image in enumerate(images):
            self.insert_image(image)
            obj = combined.Combined(combine_id, image.imageObj.imageId, index)
            objects.append(obj)
            self.session.add(obj)

        self.session.commit()
        combined_object.combineId = combine_id

    def insert_images(self, image_objects: List[RedditImage]):
        [self.insert_image(x) for x in image_objects]

    def insert_image(self, image_object: RedditImage):
        if image_object.imageObj is not None:
            return image_object.imageObj.imageId
        image_object.create_image_model()
        self.session.add(image_object.imageObj)
        self.session.commit()
        return image_object.imageObj.imageId



if __name__ == "__main__":
    obj = RedditDatabase.get_object()
    temp = RedditImage("url", "submissionurl")
    obj.insert_image(temp)
    print(obj.get_next_primary("images"))


