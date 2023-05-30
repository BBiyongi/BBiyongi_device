import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

import os
from dotenv import load_dotenv


class FirebaseDB:
    """
    Firebase CRUD helper class, NEED 'certification.json' in same directory
    """

    def __init__(self):
        """Authentication"""
        load_dotenv(verbose=True)
        DATABASE_URL = os.getenv('DATABASE_URL')
        cred = credentials.Certificate('certification.json')
        firebase_admin.initialize_app(cred, {
            'databaseURL': DATABASE_URL
        })

    # create/update
    def update(self, data: dict):
        ref = db.reference()
        ref.update(data)

    # get
    def get(self, v=None):
        if v:
            ref = db.reference(v)
        else:
            ref = db.reference()
        return ref.get()

    # 데이터 추가 함수
    def add_data(self, collection, data: dict):
        ref = db.reference(collection)
        ref.update(data)

    # delete
    def delete(self, v):
        ref = db.reference(v)
        ref.delete()


def main():
    f = FirebaseDB()


if __name__ == "__main__":
    main()
