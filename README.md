# Starter kit per la pubblicazione su API interoperabili


Questo repository contiene il template di un progetto utile a pubblicare delle API interoperabili.

## Contenuto

- Un progetto di esempio in python
- Una directory `openapi` dove scrivere le specifiche, che include script e suggerimenti

## Istruzioni

Gli step per la creazione di API interoperabili sono:

.1 scrivere le specifiche in formato OpenAPI v3 partendo da `openapi/openapi.yaml`;
.2 se si utilizzano strumenti per generare il codice a partire dalle specifiche, puo' essere necessario
   convertirle in formato swagger (OpenAPI v2). Il progetto contiene dei tool di conversione.
.3 scrivere i metodi dell'applicazione

## Panoramica

Un servizio REST con supporto TLS per ricercare le organizzazioni via .ldap. Le credenziali - reperibili sul sito di indicepa.gov.it
vengono passate tramite basic auth

        Authorization: basic XXXX

Il server viene generato tramite [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
Questo esempio utilizza la libreria [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requisiti
Docker o Python 3.6+

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

