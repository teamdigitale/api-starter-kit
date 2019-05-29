# Starter kit per la pubblicazione su API interoperabili


Questo repository contiene il template di un progetto utile a pubblicare delle API interoperabili.

Progetti associati:

- [API Starter Kit per Java](https://github.com/teamdigitale/api-starter-kit-java)

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
Il file `Makefile` contiene:

  - un esempio completo di conversione delle specifiche a v2 e generazione del server in python.
    Per convertire e generare il codice in `python-flask` lanciare:

        make python-flask

Il generatore non sovrascrive i file contenuti in `.swagger-codegen-ignore`.


  - un esempio completo di API native in OAS3 che si autenticano con uno SPID IDP 
    di test.  Per fare il build dei container con l'IDP e l'API lanciare:

        make python-flask-spid

    Le applicazioni verranno servite sugli IP dei container docker, che e' possibile
    individuare utilizzando

        docker inspect --format '{{.Name}} {{.NetworkSettings.IPAddress}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [ELENCO DEI CONTAINER]

    Se l'API non trova l'IDP, basta ricrearlo con:

        docker-compose up -d idp 

## Python

### Usare HTTPS
Per erogare un servizio python via https basta sostituire

        # in Dockerfile
        FROM python:3.6-alpine
        +RUN apk add --no-cache libffi-dev build-base openssl-dev
        -EXPOSE 8080
        +EXPOSE 8443

        # in swagger_server/__main__.py
        -app.run(port=8080)
        +app.run(port=8443, ssl_context='adhoc')



## swagger_server/__main__.py
Un servizio REST con supporto TLS. 

Il server viene generato tramite [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
Questo esempio utilizza la libreria [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requisiti
Docker e Python 3.6+

Testare e scaricare le dipendenze con:

        tox 
