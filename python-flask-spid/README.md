# Flask SPID API

A simple API authenticating with SPID.

NOTE: This API uses the development OAS3 branch of
      the connexion library that will enable the
      production of python OAS3 compliant API without
      requiring a conversion. Give it a try but
      use it in production at your own risk ;)

## Requirements

Just Docker ;)

Further infos:

  - [in the Dockerfile](Dockerfile) you'll find system requirements
  - [in requirements.txt](requirements.txt) you'll find python requirements

## Running

Start the compose file, which sets up:

  - a spid-testenv2 from the docker hub image
  - an API aka Service Provider

        docker-compose up -d simple
        sleep 5;  # give me some startup time ;)
        docker-compose up -d idp

In another console, retrieve the container ip addresses:

	CONTAINERS=$(docker ps -q)	
	docker inspect --format ' {{.Name}} {{.NetworkSettings.IPAddress}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINERS

which results in


	/pythonflaskspid_idp_1  172.22.0.3
	/pythonflaskspid_simple_1  172.22.0.2

and connect to the API in your browser

	# This URL reloads IdP metadata and
	# configures the app.
	curl -kv https://172.22.0.2/config

	# Now you can access the main page whose link
        # will bring you to the login procedure.
	firefox https://172.22.0.2

Then follow the login links from there!

Now check the actual services:

	firefox https://172.22.0.2/echo
	firefox https://172.22.0.2/status

## Run base tests

Run basic tests in docker compose

	docker-compose up test


