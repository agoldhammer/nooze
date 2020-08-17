from setuptools import setup, find_packages
setup(name="nzdb",
      version="0.2",
      author="Art Goldhammer",
      description="News Aggregator Web App",
      author_email="art.goldhamme@gmail.com",
      keywords="news aggregator Europe politics",
      url="https://github.com/agoldhammer/nooze",
      scripts=['nzdb/bin/query', 'nzdb/bin/maketopics', 'nzdb/bin/readfeed',
               'nzdb/bin/storeauthtable'],
      packages=find_packages())
