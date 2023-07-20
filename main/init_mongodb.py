from pymongo import MongoClient


def init_db(uri="mongodb://localhost:27017/"):
    client = MongoClient(uri)
    return client.RailcarTracking
