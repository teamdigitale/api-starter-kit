# Starter kit per la pubblicazione su API interoperabili

[![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit)
[![Join the #api channel](https://img.shields.io/badge/Slack-%23api-blue.svg?logo=slack)](https://developersitalia.slack.com/messages/CDKBYTG74)
[![Get invited](https://slack.developers.italia.it/badge.svg)](https://slack.developers.italia.it/)
[![API on forum.italia.it](https://img.shields.io/badge/Forum-interoperabilit%C3%A0-blue.svg)](https://forum.italia.it/c/piano-triennale/interoperabilita)

Questo repository contiene una guida per la scrittura di API interoperabili.

Progetti associati:

- [API Starter Kit per Java](https://github.com/teamdigitale/api-starter-kit-java) [![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit-java.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit-java)
- [API Starter Kit per Python](https://github.com/teamdigitale/api-starter-kit-python) [![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit-python.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit-python)
- [API Starter Kit per Go *sperimentale*](https://github.com/teamdigitale/api-starter-kit-go) [![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit-go.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit-go)
- [Schemi riusabili per specifiche OAS3](https://teamdigitale.github.io/openapi/) [![CircleCI](https://circleci.com/gh/teamdigitale/openapi.svg?style=svg)](https://circleci.com/gh/teamdigitale/openapi)
- [Validatore per specifiche OAS3](https://github.com/italia/api-oas-checker)

## Contenuto

- Un progetto di esempio in python
- Una directory `openapi` dove scrivere le specifiche, che include script e suggerimenti

## Istruzioni

Gli step per la creazione di API interoperabili sono:

1. scrivere le specifiche in formato OpenAPI v3 partendo dagli esempi in `openapi`;

2. scrivere o generare il codice a partire dalle specifiche. Gli esempi per python e java che trovate nei progetti
   associati funzionano nativamente in formato OAS3 usando swagger-codegen-cli. 
   Linguaggi meno diffusi o altri tool possono essere legati ancora a swagger (openapi v2).
   Nella directory `scripts` ci sono dei tool di conversione basati su docker.

3. scrivere i metodi dell'applicazione

### Scrivere le specifiche

TBD

### Convertire tra vari formati

La directory `scripts` contiene dei tool per convertire tra vari formati.
Prima di convertire le specifiche bisogna verificare che non ci siano
riferimenti esterni.

        # Generare delle specifiche swagger a partire da openapi.
        ./scripts/openapi2swagger.sh openapi/simple.yaml > /tmp/swagger.yaml

### Effettuare il bundle di una specifica

Per agevolare la scrittura delle specifiche è possibile utilizzare feature come:

- yaml anchors
- json `$ref`erences

Per consolidare le specifiche in un singolo file, autonomamente spendibile,
è possibile creare un bundle col comando:

	python -m openapi_resolver my-spec.yaml

In questo repository, per chiarezza, i file di specifica che utilizzano
yaml anchors e $ref hanno estensione `yaml.src`.

Notate che questi file sono formalmente corretti e specifiche valide
a tutti gli effetti. La creazione di un bundle viene effettuata solamente
per una maggiore portabilità del risultato.

### Generare il codice del server con swagger-codegen

Degli esempi di generazione di codice (o creazione degli stub) tramite
[swagger-codegen](https://github.com/swagger-api/swagger-codegen) e
`swagger-codegen-cli` sono presenti nei Makefile degli starter kit di Java e Python.

- https://github.com/teamdigitale/api-starter-kit-java/blob/master/Makefile
- https://github.com/teamdigitale/api-starter-kit-python/blob/master/Makefile

Il generatore non sovrascrive i file contenuti in `.swagger-codegen-ignore`.

### API nativamente OAS3 (senza stub)

La libreria python [Connexion](https://github.com/zalando/connexion) basata su Flask e aiohttp
permette *anche* di implementare direttamente i metodi
associati agli endpoint senza necessariamente passare dalla generazione di codice.

  - un esempio completo di API native in OAS3 che si autenticano con uno SPID IDP 
    di test.  Per fare il build dei container con l'IDP e l'API lanciare:

        make python-flask-spid

    Le applicazioni verranno servite sugli IP dei container docker, che e' possibile
    individuare utilizzando

        docker inspect --format '{{.Name}} {{.NetworkSettings.IPAddress}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [ELENCO DEI CONTAINER]

    Se l'API non trova l'IDP, basta ricrearlo con:

        docker-compose up -d idp 

## Requisiti
Docker e Python 3.6+

Testare e scaricare le dipendenze con:

        tox 
