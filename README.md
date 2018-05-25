# Starter kit per la pubblicazione su API interoperabili


Questo repository contiene il template di un progetto utile a pubblicare delle API interoperabili.

## Contenuto

- Un progetto di esempio in python
- Una directory `openapi` dove scrivere le specifiche, che include script e suggerimenti

## Istruzioni

Gli step per la creazione di API interoperabili sono:

.1 scrivere le specifiche in formato OpenAPI v3 partendo dagli esempi in `openapi`;

.2 scrivere o generare il codice a partire dalle specifiche. Alcuni strumenti per auto-generare il codice utilizzano ancora il formato swagger (openapi v2). Nella directory `scripts` ci sono dei tool di conversione basati su docker.

.3 scrivere i metodi dell'applicazione

### Scrivere le specifiche

TBD

### Convertire tra vari formati
La directory `scripts` contiene dei tool per convertire tra vari formati.
Prima di convertire le specifiche bisogna verificare che non ci siano
riferimenti esterni.

        # Generare delle specifiche swagger a partire da openapi.
        ./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

### Generare il codice del server
Il file `Makefile` contiene un esempio completo di conversione delle specifiche e generazione del server.
Per convertire e generare il codice in `prj-simple` lanciare:

        make prj-simple


### Usare HTTPS
Per erogare un servizio via https basta sostituire

        # in Dockerfile
        FROM python:3.6-alpine
        +RUN apk add --no-cache libffi-dev build-base openssl-dev
        -EXPOSE 8080
        +EXPOSE 8443

        # in swagger_server/__main__.py
        -app.run(port=8080)
        +app.run(port=8443, ssl_context='adhoc')


## swagger_server/__main__.py
Un servizio REST con supporto TLS per ricercare le organizzazioni via .ldap. Le credenziali - reperibili sul sito di indicepa.gov.it
vengono passate tramite basic auth

        Authorization: basic XXXX

Il server viene generato tramite [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
Questo esempio utilizza la libreria [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requisiti
Docker e Python 3.6+

## Utilizzo

Per eseguire il servizio è necessario utilizzare docker. Il seguente comando compila ed esegue l'applicazione:

```bash
# starting up a container
docker-compose up
```

che viene servita all'indirizzo:

```
https://localhost:8443/api-starter-kit/1.0.0/
```

I test vengono eseguiti via tox:
```
sudo pip install tox
tox
```

## Running with Docker

