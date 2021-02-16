import pymongo
import time

client = pymongo.MongoClient("elite.local")
time.sleep(10)
db = client["euronews"]
auths = db.authors.find()
for a in auths:
    print(a)
