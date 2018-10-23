# database abstraction layer
from pymongo.errors import DuplicateKeyError as DKE
from pymongo import ASCENDING, DESCENDING
import pytz
from textwrap import TextWrapper
from nzdb.dbconnect import twitterdb
from nzdb.cmdline import processCmdLine
from nzdb.dupdetect import tokenize
import json
from bson import json_util

wrapper = TextWrapper(width=60, initial_indent='+====>',
                      subsequent_indent='       ')

utc = pytz.UTC


class StatusNotFound(Exception):
    pass


class AuthorNotFound(Exception):
    pass


class DuplicateStatus(Exception):
    pass


class QueryParseException(Exception):
    pass


class TopicNotFound(Exception):
    pass


# db abstraction section

def get_status_date_range():
    """
    Return first, last status dates
    :return: (earliest date in db, latest date in db)
    :rtype: (datetime, datetime)
    """
    cursor = twitterdb.statuses.find({}, projection={"created_at": True})
    cursor_dn = cursor.clone()
    maxdate = cursor.sort("created_at", DESCENDING).limit(1)
    mindate = cursor_dn.sort("created_at", ASCENDING).limit(1)
    return mindate[0]["created_at"], maxdate[0]["created_at"]


def mapStatusIDtoStatus(status_id):
    return twitterdb.statuses.find_one({"id": status_id})


def getAuthors():
    """
    :return: list of authors from db
    :rtype: list of strings
    """
    authrecs = twitterdb.authors.find()
    return [authrec["author"] for authrec in authrecs]


def mapAuthorToLang(author):
    author_record = twitterdb.authors.find_one({"author": author})
    if author_record is None:
        raise AuthorNotFound(author)
    else:
        return author_record["language_code"]


def getUnknownAuthors():
    unknowns = twitterdb.authors.find({"language_code": "U"})
    return unknowns


def getCount():
    """
    Get count of statusids in db
    :return: count
    :rtype: int
    """
    return twitterdb.statuses.estimated_document_count()


def getTopics():
    """
    Get topics from db, sorted on the description field
    :return: cursor of topics
    :rtype: topic document
    """
    return twitterdb.topics.find(
        projection={"_id": False}).sort("desc", ASCENDING)


def cleanTopicsCollection():
    twitterdb.topics.drop()


def storeTopic(topic):
    """
    Stores topic dict in topics collectiion, indexed by topic
    :param topic: dictionary(topic, desc cat query)
    """
    # twitterdb.topics.update({"topic": topic["topic"]}, topic, upsert=True)
    twitterdb.topics.insert(topic)


def storeAuthor(author, lang):
    """
    Store authors in db authors collection
    :param str author:
    :param str lang:
    :return: nothing
    """
    row = {"author": author, "language_code": lang}
    twitterdb.authors.update({"author": author}, row, upsert=True)


def storeStatus(status):
    """
    Store trimmed twitter status doc in statuses collection
    :param json status: trimmed status doc from twitter
    :return: nothing
    :raises: DuplicateKeyError
    """
    try:
        twitterdb.statuses.insert(status)
    except DKE:
        raise DuplicateStatus(status)


def sid_to_topics(sid, lang):
    """status id to topics"""
    c = twitterdb.topids.find({"id": sid, "lang": lang})
    return [t["topic"] for t in c]


def docDate(doc):
    """
    Return date of doc (created_at field)
    :param  doc: a status doc
    :return: created_at datetime
    :rtype: datetime
    """
    docid = doc["docid"]
    doc = twitterdb.statuses.find_one({"id": docid}, {"created_at": 1})
    return utc.localize(doc["created_at"])


def mapTopicToQuery(topic):
    """
Map topic to query
    :param str topic:
    :return: query associated with topic
    :rtype: string
    """
    row = twitterdb.topics.find_one({"topic": topic})
    if row is not None:
        return row["query"]
    else:
        raise TopicNotFound(topic)


def expand_topic(query):
    """
      Expand topics that begin with *
    :param str query:
    :return: expanded query
    :rtype: str
    """
    if query and not query.startswith("*"):
        return query
    else:
        # look up query after stripping off asterisk
        try:
            query = query[1:]
            query = mapTopicToQuery(query)
        except Exception as e:
            msg = "Exception in lookup of: {}\n".format(e)
            raise QueryParseException(msg)
        else:
            return query


def _setup_mongo_query(search_context):
    """
      Prepare query based on search_context
    :param search_context:
    :type: search_context or None
    :return: query
    :rtype: mongodb query
    """
    start = search_context.startdate
    end = search_context.enddate
    searchon = {"created_at": {"$gte": start, "$lte": end}}
    # if query is None, we don't do text search but search for all in
    #   date window
    if search_context.query is not None:
        query = search_context.query
        query = expand_topic(query)
        searchon["$text"] = {"$search": query}
    return searchon


def esearch(search_context, sort_dir=ASCENDING):
    """
      If query is None, search on date range only
    :param: search_context
    :type: search_context or None
    :return: cursor of full statuses based on query
    :rtype: err, cursor
    """
    try:
        searchon = _setup_mongo_query(search_context)
        cursor = twitterdb.statuses.find(searchon,
                                         projection={"$diacriticSensitive":
                                                     False})
        return None, cursor.sort("created_at", sort_dir)
    except QueryParseException as e:
        return e, []


def websearch(query):
    search_context = processCmdLine(query)
    return esearch(search_context, DESCENDING)


def find_topic_all(topic, lang):
    """
    return all statuses for topic
    """
    query = expand_topic(topic)
    cursor = twitterdb.statuses.find({"$text": {"$search": query,
                                                "$language": lang}},
                                     projection=({"$diacriticSensitive":
                                                  False}))
    return cursor


def get_all_texts():
    """
    :return: cursor
    :rtype: cursor
    """
    # mindate, maxdate = get_status_date_range()
    return twitterdb.statuses.find(projection={"_id": False, "text": True})


def cleanup(text):
    # remove urls, @xxx, RT from text
    # tokenize removes urls
    tokens = tokenize(text)
    tokens = [tok for tok in tokens if tok != "RT" and
              not tok.startswith('@')]
    return " ".join(tokens)


def sample(skip=0, nsamples=10000):
    # tokenize strips out urls
    cursor = get_all_texts()
    cursor = cursor.skip(skip).limit(nsamples)
    return (cleanup(s["text"]) for s in cursor)


def explain_pp(cursor):
    """pretty print cursor explanation"""
    explanation = cursor.explain()
    better_explanation = json.dumps(explanation, default=json_util.default,
                                    sort_keys=True, indent=4)
    print(better_explanation)


def status_from_id(id):
    """
    :param: id
    :return: status
    """
    return twitterdb.statuses.find_one({"id": id})


def fetch_recent(cmdline="-H 3 dummy"):
    """fetch recent statuses as defined by cmdline

    :param cmdline: a dummy cmdline, such as "-H 8 dummy"
    :returns: cursor of statuses as for esearch
    :rtype: pymongo cursor

    """
    search_context = processCmdLine(cmdline)
    search_context.query = None
    return esearch(search_context, DESCENDING)


def get_lastread():
    last = twitterdb.lastread.find_one()
    if not last:
        return (0, 0)
    else:
        return last["_id"], last["maxid"]


def store_lastread(maxid):
    _id, oldmaxid = get_lastread()
    twitterdb.lastread.update({"_id": _id, "maxid": oldmaxid},
                              {"_id": _id, "maxid": maxid}, upsert=True)


if __name__ == '__main__':
    sc = processCmdLine(None)
    err, cursor = esearch(sc)
    for s in cursor:
        print(s)
