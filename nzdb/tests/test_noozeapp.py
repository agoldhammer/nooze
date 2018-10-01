from nzdb.noozeapp import parse_query, extract_options, app

testqs = ["-d 1 *Executive *Judicial",
          "-H 8 Warren Gillibrand",
          "-d 5 *Business Schumer",
          "-s 12/15/2017 -e 12/16/2017 Jones *Executive"]


def test_extract_options():
    expected = ["-d 1", "-H 8", "-d 5",
                "-s 12/15/2017 -e 12/16/2017"]
    for i in range(len(testqs)):
        parts = testqs[i].split(" ")
        options, _ = extract_options(parts)
        assert(options == expected[i])


def test_parse_query():
    expected = [["-d 1 *Executive", "-d 1 *Judicial"],
                ['-H 8 "Warren Gillibrand"'],
                ["-d 5 *Business", '-d 5 "Schumer"'],
                ["-s 12/15/2017 -e 12/16/2017 *Executive",
                 '-s 12/15/2017 -e 12/16/2017 "Jones"']]
    for i in range(len(testqs)):
        _, queries = parse_query(testqs[i])
        assert(queries == expected[i])


def test_routes():
    client = app.test_client()
    resp = client.get('/')
    assert(b'html' in resp.data)
    resp = client.get('/statuses/-s 2018-09-30 -e 2018-10-01 Macron')
    assert(b'Macron' in resp.data)
    resp = client.get('/error')
    assert(b'html' in resp.data)
    resp = client.get('/stats')
    assert(b'html' in resp.data)
    resp = client.get('/help')
    assert(b'html' in resp.data)
