import datetime
from random import randint

from connexion import problem
from swagger_server.models.timestamps import Timestamps  # noqa: E501


def get_echo():  # noqa: E501
    """Ritorna un timestamp in formato RFC5424.

    Ritorna un timestamp in formato RFC5424 prendendola dal server attuale.  # noqa: E501


    :rtype: Timestamps
    """
    return Timestamps(datetime.datetime.utcnow())


def get_status():  # noqa: E501
    """Ritorna lo stato dell'applicazione.

    Ritorna lo stato dell'applicazione.  # noqa: E501


    :rtype: Problem
    """
    p = randint(0, 10)

    if p < 7:
        return problem(status=200, title="Success",
                       detail="Il servizio funziona correttamente",
                       ext={"result": "ok"},
                       headers={
                           'Cache-control': 'no-cache'
                       })
    if p < 9:
        return problem(status=503, title="Service Unavailable",
                       detail="Questo errore viene ritornato randomicamente.",
                       headers={
                           'Retry-After': '1',
                           'Cache-control': 'no-cache'
                       })

    return problem(status=429, title="Too Many Requests",
                   detail="Questo errore viene ritornato randomicamente.",
                   headers={
                       'Cache-control': 'no-cache',
                       'X-RateLimit-Limit': '10',
                       'X-RateLimit-Reset': '1',
                       'X-RateLimit-Remaining': '0',
                       'Retry-After': '1',
                   })
