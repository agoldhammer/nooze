import re
from itertools import chain
from itertools import groupby
from collections import defaultdict, OrderedDict
from flask import (Flask, request, render_template, redirect,
                   flash, url_for, jsonify)

from flask_bootstrap import Bootstrap
from flask_script import Manager

from nzdb.dbif import websearch, getTopics, getCount, fetch_recent
from nzdb.dupdetect import dedupe
from nzdb.configurator import nzdbConfig


class WebQueryParseException(Exception):
    pass


# configuration
DEBUG = False


SECRET_KEY = 'ag3rf8-(cnc&my7&)a2(!v*mj9*7v#3cgix@=&5&qam&57n7&o0=$'
USERNAME = 'admin'
PASSWORD = 'default'

templates = nzdbConfig['templates']
static = nzdbConfig['static']
app = Flask(__name__,
            template_folder=templates,
            static_folder=static)
# app.config.from_object(__name__)

manager = Manager(app)
bootstrap = Bootstrap(app)


def getStats():
    """
    :returns: dictionary {"size": total num statuses,
        "cats": dict of stats} where
        a stat is a dictionary {"query": str descriptor of topic, "stat":
            is slug describing no of entries on topic and % of total}
    """
    size = getCount()
    topics = list(getTopics())
    topics = sorted(topics, key=lambda topic: topic["cat"])
    # for topic in topics:
    #     # TODO: fix this, looking back only 1 week but comparing to all time
    #     query = "-d 7 " + topic["query"]
    #     err, cursor = websearch(query)
    #     if not err:
    #         n = cursor.estimated_document_count()
    #         topic["count"] = n
    #         topic["percent"] = "{:.2%}".format(1.0 * n / size)
    groups = groupby(topics, key=lambda topic: topic["cat"])
    temp = defaultdict(list)
    for cat, group in groups:
        for topic in group:
            temp[cat].append(topic)
    cats = OrderedDict()
    keys = sorted([k for k in temp])
    for key in keys:
        cats[key] = temp[key]
    return size, cats


# added this to speed up load of home page
# differs from longer getStats by not providing topic stats,
# which are not needed for home page, only for stats page
def getShortStats():
    """
    :returns: dictionary {"size": total num statuses,
        "cats" is dict of "topics", where
        "topics": list of stats}
    """
    size = getCount()
    topics = list(getTopics())
    topics = sorted(topics, key=lambda topic: topic["cat"])
    groups = groupby(topics, key=lambda topic: topic["cat"])
    temp = defaultdict(list)
    for cat, group in groups:
        for topic in group:
            temp[cat].append(topic)
    cats = OrderedDict()
    keys = sorted([k for k in temp])
    for key in keys:
        cats[key] = temp[key]
    return size, cats


class Row():
    """docstring for Row"""
    def __init__(self, header, statuses):
        self.statuses = statuses
        self.header = header


@app.template_filter('taburlize')
def taburlize(s):
    """flask filter similar to urlize but sets target to new tab """
    pattern = r'(https?://\S+)'
    p = re.compile(pattern)
    return p.sub(r'<a href="\1" target="_blank"> ...more &#10149; </a>', s)


@app.route("/error")
def showError():
    return render_template('error.html')


@app.route("/stats")
def showStats():
    n, cats = getStats()
    return render_template('stats.html', n=n, cats=cats)


@app.route("/help")
def showHelp():
    return render_template('help.html')


def extract_options(parts):
    """
    Extract options from query, such as -d 5 xxx
    """
    options = ""
    newparts = []
    n = len(parts)
    skip = False
    for i in range(len(parts)):
        if skip:
            skip = False
            continue
        if (parts[i].startswith('-')) and i + 1 < n:
            if parts[i][1] not in "dseH":
                # -d -s -e are only valid options
                raise WebQueryParseException
            # remove option indicator and value and add to options
            clause = " ".join([parts[i], parts[i + 1]])
            if options != "":
                options = " ".join([options, clause])
            else:
                options = clause
            skip = True  # skip ahead in iteration
        else:
            newparts.append(parts[i])
    if options == "":
        # valid query must have options
        raise WebQueryParseException
    return options, newparts


def parse_query(query):
    """
    Transform complex query into simpler subqueries that can be processed
    by processCmdLine and then combined in showNews by chaining
    returns err, queries; err is None if no exception, True otherwise
    """
    parts = query.split(" ")
    try:
        if len(parts) < 3:
            # -x 1 somequery is minimal query, so will have 3 or more parts
            raise WebQueryParseException
        options, parts = extract_options(parts)
    # TODO: make this catch more fine-grained.
    # right now taking care of both WebQueryParseException and
    # index out of range exception from parts[1][1] avoe when a bare -
    # is entered in a custom query
    except Exception as e:
        print(query, e)
        return True, []
    starred = []
    unstarred = []
    for part in parts:
        if part.startswith('*'):
            starred.append(part)
        else:
            unstarred.append(part)
    queries = []
    for query in starred:
        queries.append(" ".join([options, query]))
    unstarred_stringed = " ".join(unstarred)
    unstarred_quoted = f'"{unstarred_stringed}"'
    if unstarred:
        queries.append(" ".join([options, unstarred_quoted]))
    return False, queries


def handleQuery(query):
    err, queries = parse_query(query)
    if err:
        flash("Error in query, try again!")
        return redirect(url_for("query"))
    cursors = []
    for subquery in queries:
        err, cursor = websearch(subquery)
        if not err:
            cursors.append(cursor)
        elif err:
            flash("Error in query, try again! " + str(err))
    # kludgy error signaling mechanism
    if not cursors:
        query = None
    # eliminate near duplicates from the display
    statuses = dedupe(chain(*cursors))
    return statuses


# to handle multiple *requests, we must parse the query and chain results
@app.route("/statuses/<query>")
def showNews(query):
    statuses = handleQuery(query)
    row = Row(header=query, statuses=statuses)
    return render_template('statuses.html', row=row)


@app.route("/")
def query():
    if request.method == "GET":
        # n, cats = getShortStats()
        # return render_template("query.html", n=n, cats=cats)
        return render_template("index.html")
    else:
        return redirect("/error")


@app.route("/json/cats", methods=["GET", "PUT"])
def cats_json():
    n, cats = getShortStats()
    resp = jsonify(count=n, cats=cats)
    # TODO: This allows cross site request for TESTING, remove LATER
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


def unid(s):
    del s["_id"]
    return s


@app.route("/json/count", methods=["GET"])
def count_json():
    n = getCount()
    resp = jsonify(count=n)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


@app.route("/json/recent", methods=["GET", "POST"])
def recent_json():
    # this will get last 3 hours of posts
    error, cursor = fetch_recent()
    if error is None:
        cursor = [unid(s) for s in cursor]
        resp = jsonify(cursor)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


# TODO: need to do something about flashed error messages in handleQuery
# These won't work with the json interface

@app.route("/json/qry", methods=["GET", "POST"])
def qry_json():
    print(request.args)
    query = request.args.get("data")
    print(query)
    statuses = handleQuery(query)
    statuses = [unid(s) for s in statuses]
    resp = jsonify(statuses)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return resp


if __name__ == '__main__':
    manager.run()
