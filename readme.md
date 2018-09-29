# nooze -- Twitter list accumulator

## Frontend

The frontend is a separate project, written in Clojurescript and designed as a single-page application.

## Backend

The backend is a mongodb database in a Docker container.

Currently using mongo 4.0.2-xenial image.

## Middleware

The frontend consists of the Python app nooze, which can be configured to work with different databases in the backend and to consume different Twitter lists. See [Configuration](#configuration).

Nooze is built on top of ```twdb2```, which handles all interfacing with the database. Nooze is a Web service based on Flask.

### Application details

`nzdb` installs several scripts used by nooze.

`readfeed` processes the Twitter list feed specified in the configuration file.

`maketopics` stores the topic list specified in `xxtopics.txt`, where `xx` designates the appropriate topic file.

`storeauthtable` stores the author list specified in `xxauthors.txt`.

#### Running on cloud host

Remember to use the NEWSTAG env variable to specify the correct version
of the containers.

`NZTAG=<tag> docker-compose -f cloud-multi.yaml up -d`
`NZTAG=<tag> docker-compose -f cloud-multi.yaml down`
`NZTAG=<tag> docker-compose -f cloud-multi.yaml logs`

#### Configuration

Congiuration files *must* be located in the `app/confs` directory of `noozep`.

Here is a sample docker-compose config file:

```
version: '3.7'
services:
	dbhost:
		image: mongo:4.0.2-xenial
		restart: always
		container_name: dbhost
		volumes:
			- $HOME/backup:/warehouse
			- $HOME/data/db:/data/db
		ports:
			- "27018:27017"
		command: mongod --logpath=/dev/null

	usnews:
		depends_on:
			- dbhost
		image: artgoldhammer/nooze:$NZTAG
		container_name: usnews
		restart: always
		volumes:
			- $HOME/confs:/app/confs
		environment:
			NZDBCONF: /app/confs/cloud-us.conf
		ports:
			- "9090:9090"
			- "3031:3031"

	eunews:
		depends_on:
			- dbhost
		image: artgoldhammer/nooze:$NZTAG
		container_name: eunews
		restart: always
		volumes:
			- $HOME/confs:/app/confs
		environment:
			NZDBCONF: /app/confs/cloud-eu.conf
		ports:
			- "9091:9090"
			- "3032:3031"
```

And here is a sample NZDB conf:

```

[authentication]

OAUTH_TOKEN = my oauth token
OAUTH_TOKEN_SECRET = my oauth secret
CONSUMER_KEY = my consumer key
CONSUMER_SECRET = my consumer secret

[db]
HOST=dbhost
DBNAME=mydbname

[authors]
authfile=/app/confs/myauthors.txt

[topics]
topicsfile=/app/confs/mytopics.txt

[logging]
logfile=/var/log/twdb2/myapp.log
logname=myapp

[twitter]
owner=mytwitterhandle
slug=mylistname
```

#### replacing container on website

```
ubuntu@ip-172-31-42-130:~$ NZTAG=0923 docker-compose -f cloud-multi.yaml up -d
Creating network "ubuntu_default" with the default driver
Creating dbhost ... done
Creating usnews ... done
Creating eunews ... done
```
