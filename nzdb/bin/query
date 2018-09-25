#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from nzdb.cmdline import processCmdLine
from nzdb.dbif import esearch
from nzdb.prettytext import printMatches


class SearchException(Exception):
    pass


def main():
    search_context = processCmdLine()
    err, cursor = esearch(search_context)
    if err is not None:
        print("Error parsing query:", err)
    else:
        printMatches(cursor)


if __name__ == '__main__':
    main()
    sys.exit(0)
