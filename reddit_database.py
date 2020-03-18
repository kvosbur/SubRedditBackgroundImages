import sqlite3
from util import base_directory, current_date_string, parse_date_string
import os
import datetime
from typing import List
from reddit_image import RedditImage
from combine_image import CombineImages
DBFileName = "image_db.db"


class RedditDatabase:
    # static variables
    Singleton = None

    # object variables
    connection = None

    @staticmethod
    def get_object():
        if RedditDatabase.Singleton is None:
            RedditDatabase.Singleton = RedditDatabase()

        return RedditDatabase.Singleton

    def __init__(self):
        self.get_connection()

    def do_init(self):
        self.connection.execute('''
            CREATE TABLE images(
                imageId INTEGER PRIMARY KEY,
                imageURL TEXT,
                postURL TEXT,
                imagePath TEXT,
                dateReceived TEXT,
                blackListedDate Text
            );
        ''')
        self.connection.execute('''
            CREATE TABLE combined(
                combineId INTEGER,
                imageId INTEGER,
                position INTEGER,
                PRIMARY KEY (combineId, imageId),
                FOREIGN KEY(imageId) REFERENCES images(imageId) ON DELETE CASCADE
            );
        ''')
        self.connection.execute('''
            CREATE TABLE weekly(
                weeklyId INTEGER PRIMARY KEY,
                imageId INTEGER,
                combineId INTEGER,
                isCurrent INTEGER,
                FOREIGN KEY(imageId) REFERENCES images(imageId) ON DELETE CASCADE,
                FOREIGN KEY(combineId) REFERENCES combine(combineId) ON DELETE CASCADE
            );
        ''')
        self.connection.execute('''
            CREATE TABLE daily(
                dailyId INTEGER PRIMARY KEY,
                imageId INTEGER,
                combineId INTEGER,
                isCurrent INTEGER,
                FOREIGN KEY(imageId) REFERENCES images(imageId) ON DELETE CASCADE,
                FOREIGN KEY(combineId) REFERENCES combine(combineId) ON DELETE CASCADE
            );
        ''')

    def get_connection(self):
        db_path = os.path.join(base_directory, "PictureSource", DBFileName)
        do_init = not os.path.exists(db_path)
        # if db doesn't exist connect will create the necessary file
        self.connection = sqlite3.connect(db_path)
        # enable foreign keys for this database connection
        self.connection.execute('''PRAGMA foreign_keys = ON;''')
        if do_init:
            self.do_init()

    def get_next_primary(self, table_name):
        tables = {"images": "imageId", "combined": "combineId", "weekly": "weeklyID", "daily": "dailyId"}
        res = self.connection.execute("Select max(" + tables[table_name] + ") from " + table_name + ";")
        amount = res.fetchone()[0]
        # case to catch if table is empty
        if amount is None:
            amount = 0
        return amount + 1

    def insert_all_combined(self, all_combined_object: List[CombineImages]):
        [self.insert_combined(x) for x in all_combined_object]

    def insert_combined(self, combined_object: CombineImages):
        newId = self.get_next_primary("combined")
        images = combined_object.get_selected_images()
        for image_index in range(len(images)):
            sub_image = images[image_index]
            if sub_image.imageId is None:
                self.insert_image(sub_image)
            self.connection.execute('''
                INSERT INTO combined (combineId, imageId, position) VALUES (?,?,?)
            ''', [newId, sub_image.imageId, image_index + 1])

        combined_object.combineId = newId

    def insert_images(self, image_objects: List[RedditImage]):
        [self.insert_image(x) for x in image_objects]

    def insert_image(self, image_object: RedditImage):
        if image_object.imageId is not None:
            return image_object.imageId
        newId = self.get_next_primary("images")
        argument_list = [newId, image_object.imageUrl, image_object.submissionUrl, image_object.get_image_path(),
                         current_date_string(), ""]
        self.connection.execute(''' 
            INSERT INTO images (imageId, imageURL, postURL, imagePath, dateReceived, blackListedDate) Values(?,?,?,?,?,?);
        ''', argument_list)
        self.connection.commit()
        image_object.imageId = newId
        return newId



if __name__ == "__main__":
    obj = RedditDatabase.get_object()
    temp = RedditImage("url", "submissionurl")
    obj.insert_image(temp)
    print(obj.get_next_primary("images"))


