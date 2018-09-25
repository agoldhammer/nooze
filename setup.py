from setuptools import setup, find_packages
setup(name="nzdb",
      version="0.1",
      scripts=['nzdb/bin/query', 'nzdb/bin/maketopics', 'nzdb/bin/readfeed',
               'nzdb/bin/storeauthtable'],
      packages=find_packages())
