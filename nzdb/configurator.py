#! /usr/bin/env python

"""
Configuration module for nzdb app
"""

import configparser
import os
import sys

config = configparser.ConfigParser()

nzdbConfig = {}

# must set environment variable NZDBCONF to path of config file
config_file = os.getenv("NZDBCONF")
if config_file:
    config.read(os.path.expanduser(config_file))
else:
    print("Config error: env var NZDBCONF not set")
    sys.exit(255)

nzdbConfig['OAUTH_TOKEN'] = config.get('authentication', 'OAUTH_TOKEN')
nzdbConfig['OAUTH_TOKEN_SECRET'] = config.get('authentication',
                                              'OAUTH_TOKEN_SECRET')
nzdbConfig['CONSUMER_KEY'] = config.get('authentication', 'CONSUMER_KEY')
nzdbConfig['CONSUMER_SECRET'] = config.get('authentication', 'CONSUMER_SECRET')

host = config.get('db', "HOST")
nzdbConfig['DBHOST'] = 'localhost' if host is None else host
nzdbConfig['DBNAME'] = config.get('db', 'DBNAME')

nzdbConfig['authfile'] = config.get('authors', 'authfile')
nzdbConfig['topicsfile'] = config.get('topics', 'topicsfile')
nzdbConfig['logfile'] = config.get('logging', 'logfile')
nzdbConfig['logname'] = config.get('logging', 'logname')
nzdbConfig['owner'] = config.get('twitter', 'owner')
nzdbConfig['slug'] = config.get('twitter', 'slug')

if __name__ == '__main__':
    print(nzdbConfig)
