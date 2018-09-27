#! /usr/bin/env python

"""
Configuration module for nzdb app
"""

import configparser
import os
import sys

config = configparser.ConfigParser()


nzdbConfig = {}


def expand(path):
    return os.path.expanduser(path)


# must set environment variable NZDBCONF to path of config file
config_file = os.getenv("NZDBCONF")
if config_file:
    config_file = expand(config_file)
    read = config.read(config_file)
    if len(read) == 0:
        print(f'Configuration file {config_file} not found')
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

nzdbConfig['authfile'] = expand(config.get('authors', 'authfile'))
nzdbConfig['topicsfile'] = expand(config.get('topics', 'topicsfile'))

nzdbConfig['logfile'] = expand(config.get('logging', 'logfile'))
nzdbConfig['logname'] = config.get('logging', 'logname')

nzdbConfig['owner'] = config.get('twitter', 'owner')
nzdbConfig['slug'] = config.get('twitter', 'slug')

nzdbConfig['templates'] = expand(config.get('app', 'template-dir'))
nzdbConfig['static'] = expand(config.get('app', 'static-dir'))

if __name__ == '__main__':
    print(nzdbConfig)
