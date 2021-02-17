import sys
from pymongo import MongoClient  # , TEXT, ASCENDING
from pymongo.errors import ConnectionFailure
from nzdb.configurator import nzdbConfig

DBNAME = nzdbConfig["DBNAME"]
DBHOST = nzdbConfig['DBHOST']

_thedb = None


def conn():
    """connect to Mongo db dbname

    Args:
        dbname ([string]): name of the db

    Returns:
        mongo db: a mongo db instance
    """
    # db with 4 collections: statuses, authors, topics, hashestodocids
    print("db init", DBHOST)
    client = MongoClient(DBHOST, connect=False)
    return client


def get_db():
    global _thedb
    if _thedb is None:
        client = conn()
        max_retries = 20
        tried = 0
        connected = False
        while tried < max_retries and not connected:
            try:
                client.admin.command("ismaster")
                connected = True
            except ConnectionFailure:
                print("Waiting for connection")
                tried += 1

        if not connected:
            print(f"Could not connect to server {DBHOST} after {tried} retries; quitting")
            sys.exit(1)
        else:
            _thedb = client[DBNAME]
    return _thedb


if __name__ == "__main__":
    db = get_db()
    print("db is", db)
    for a in db.authors.find():
        print(a)
