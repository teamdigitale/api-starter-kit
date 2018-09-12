# Flask SPID API

A simple API authenticating with SPID.

## Requirements

Docker

## Running

Start the compose file, which sets up:

  - a spid-testenv2 from the docker hub image
  - an API aka Service Provider

	docker-compose up  simple spid-testenv 

In another console, retrieve the container ip addresses:

	CONTAINERS=$(docker ps -q)	
	docker inspect --format ' {{.Name}} {{.NetworkSettings.IPAddress}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINERS

which results in


	/pythonflaskspid_spid-testenv_1  172.22.0.3
	/pythonflaskspid_simple_1  172.22.0.2

and connect to the API in your browser

	firefox https://172.22.0.2

Then follow the login links from there!
