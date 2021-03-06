import sys
from pymongo import MongoClient, TEXT, ASCENDING
from nzdb.configurator import nzdbConfig

DBNAME = nzdbConfig["DBNAME"]
DBHOST = nzdbConfig['DBHOST']
maxServDelay = 10000  # ms timeout on server connect


class Twitterdb:
    """
    :class:
      statuses has fields twid, created_at and text distilled from
       Twitter statuses
      authors has fields author, lang
      topics has fields topic, cat, desc, query
      interface through dbif
    """
    def __init__(self, dbname):
        # db with 4 collections: statuses, authors, topics, hashestodocids
        self.client = MongoClient(DBHOST,
                                  serverSelectionTimeoutMS=maxServDelay,
                                  connect=False)
        self.db = self.client[dbname]
        self.statuses = self.db.statuses
        self.statuses.create_index([("text", TEXT)])
        self.statuses.create_index([("created_at", ASCENDING)])
        self.authors = self.db.authors
        self.topics = self.db.topics
        self.authors.create_index([("author", 1)], unique=True)
        self.topics.create_index([("topic", 1)], unique=True)
        self.lastread = self.db.lastread
        try:
            self.client.server_info()  # test connection made
        except Exception as e:
            print(f"Could not connect to server {DBHOST}; Exception {e}")
            sys.exit(1)


twitterdb = Twitterdb(DBNAME)


if __name__ == '__main__':
    """
    test connection
    """
    print(f"The db host is {DBHOST}")
    print(twitterdb.client.server_info())
