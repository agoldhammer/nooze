import pytest
import os
import sys
from subprocess import call
from nzdb.connectdb import get_db

config_file = os.getenv("NZDBCONF")
if "localtest.conf" not in config_file:
    print("For testing, NZDBCONF must be set to ~/Prog/nooze/confs/localtest.conf")  # noqa
    sys.exit(255)

topdir = os.path.expanduser('~/Prog/nooze/')

testenv = {'NZDBCONF': config_file}
print(f"Test environment {testenv}")
print(f"topdir is {topdir}")


@pytest.fixture(autouse=True, scope='session')
def setup_testdb():
    # setup
    print("running setup")
    wd = os.getcwd()
    print(f"wd = {wd}")
    os.chdir(topdir)
    # run(["./test_setup"], env=testenv,
    #     shell=True, check=True, capture_output=True)
    call("./test_setup", shell=True)
    os.chdir(wd)
    yield

    # teardown
    db = get_db()
    db.client.drop_database('localtest')
