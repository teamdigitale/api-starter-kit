import connexion
import six
import datetime

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.timestampa import Timestampa  # noqa: E501
from swagger_server import util
from random import randint
from connexion import problem


def get_echo():  # noqa: E501
    """Ritorna un timestamp in formato RFC5424.

    Ritorna un timestamp in formato RFC5424 prendendola dal server attuale.  # noqa: E501


    :rtype: Timestampa
    """
    return Timestampa(datetime.datetime.utcnow())


def get_status():  # noqa: E501
    """Ritorna lo stato dell'applicazione.

    Ritorna lo stato dell'applicazione.  # noqa: E501


    :rtype: Object
    """
    p = randint(0, 10)

    if p < 7:
        return {"result": "ok", "status": 200}
    if p < 9:
        return problem(status=503, title="Service Unavailable",
                       detail="Questo errore viene ritornato randomicamente.",
                       headers={'Retry-After': '1'}
                       )
    if p < 10:
        return problem(status=429, title="Too Many Requests",
                       detail="Questo errore viene ritornato randomicamente.",
                       headers={
                           'X-RateLimit-Limit': '10',
                           'X-RateLimit-Reset': '1',
                           'X-RateLimit-Remaining': '0',
                           'Retry-After': '1',
                       })
