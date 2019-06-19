# Starter kit per la pubblicazione su API interoperabili

[![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit)


Questo repository contiene il template di un progetto utile a pubblicare delle API interoperabili.

Progetti associati:

- [API Starter Kit per Java](https://github.com/teamdigitale/api-starter-kit-java) [![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit-java.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit-java)
- [API Starter Kit per Python](https://github.com/teamdigitale/api-starter-kit-python) [![CircleCI](https://circleci.com/gh/teamdigitale/api-starter-kit-python.svg?style=svg)](https://circleci.com/gh/teamdigitale/api-starter-kit-python)


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
il programma `swagger-codegen-cli` sono presenti 
nei Makefile degli starter kit di Java e Python.

- https://github.com/teamdigitale/api-starter-kit-java/blob/master/Makefile
- https://github.com/teamdigitale/api-starter-kit-python/blob/master/Makefile

Il generatore non sovrascrive i file contenuti in `.swagger-codegen-ignore`.

### API nativamente OAS3 (senza stub)

La libreria python `connexion` permette di implementare direttamente i metodi
associati agli endpoint senza necessariamente passare dalla generazione di codice.

  - un esempio completo di API native in OAS3 che si autenticano con uno SPID IDP 
    di test.  Per fare il build dei container con l'IDP e l'API lanciare:

        make python-flask-spid

    Le applicazioni verranno servite sugli IP dei container docker, che e' possibile
    individuare utilizzando

        docker inspect --format '{{.Name}} {{.NetworkSettings.IPAddress}} {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' [ELENCO DEI CONTAINER]

    Se l'API non trova l'IDP, basta ricrearlo con:

        docker-compose up -d idp 



## swagger_server/__main__.py
Un servizio REST con supporto TLS. 

Il server viene generato tramite [swagger-codegen](https://github.com/swagger-api/swagger-codegen).
Questo esempio utilizza la libreria [Connexion](https://github.com/zalando/connexion) library on top of Flask.

## Requisiti
Docker e Python 3.6+

Testare e scaricare le dipendenze con:

        tox 
