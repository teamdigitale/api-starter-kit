# Starter kit per la pubblicazione su API interoperabili


Questo repository contiene il template di un progetto utile a pubblicare delle API interoperabili.

## Contenuto

- Due progetti di esempio: uno in python e uno in XXX.
- Una directory `openapi` dove scrivere le specifiche, che include script e suggerimenti

## Istruzioni

Gli step per la creazione di API interoperabili sono:

.1 scrivere le specifiche in formato OpenAPI v3 partendo dagli esempi in `openapi`;

.2 scrivere o generare il codice a partire dalle specifiche. Alcuni strumenti per auto-generare il codice utilizzano ancora il formato swagger (openapi v2). Nella directory `scripts` ci sono dei tool di conversione basati su docker.

.3 scrivere i metodi dell'applicazione

E' possibile subito generare il codice ed eseguire `prj-simple` lanciando:

        make prj-simple-quickstart

### Scrivere le specifiche

TBD

### Convertire tra vari formati
Ad oggi, la maggioranza dei tool di generazione delle specifiche è basata ancora su Swagger 2.0.
La directory `scripts` contiene uno script per convertire da OpenAPI a Swagger:

        # Generare delle specifiche swagger a partire da openapi.
        ./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

**NB: le specifiche Swagger convertite vanno utilizzate solo per generare il codice,
 in attesa di un rilascio piu' capillare dei nuovi tool**

### Generare il codice del server
`prj-simple` contiene dei file che implementano il servizio, e che sostituiscono i template autogenerati.

Rigenerando il codice con:

        make prj-simple

possiamo vedere le modifiche tra i file che implementano il servizio ed i template

        git diff prj-simple

Le modifiche sono descritte dai relativi commenti e:

  - Erogano il servizio via HTTPS e modificano di conseguenza il Dockerfile
  - Correggono un bug del framework nei test
  - Implementano il servizio


## swagger_server/__main__.py
Un servizio REST con supporto TLS per ricercare le organizzazioni via .ldap. Le credenziali - reperibili sul sito di indicepa.gov.it
vengono passate tramite basic auth

        Authorization: basic XXXX

Il server viene generato tramite [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
Questo esempio utilizza la libreria [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requisiti
Docker e Python 3.6+


## prj-simple

Per eseguire prj-simple:

        make prj-simple-quickstart

Una volta avviato il servizio:

        curl -k https://172.17.0.2:8443/datetime/v1/echo
        {
        "timestamp": "2018-05-25T17:49:49.847141Z"
        }


