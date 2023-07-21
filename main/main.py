from utils import init_db

db = init_db()
db.trains.delete_many({'type': 'yt'})

# TODO: init replay folders and subfolders
# TODO: webcams.csv -> to MongoDB
