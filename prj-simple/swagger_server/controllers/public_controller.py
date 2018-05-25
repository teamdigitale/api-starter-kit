import connexion
import six
import datetime

from swagger_server.models.problem import Problem  # noqa: E501
from swagger_server.models.timestampa import Timestampa  # noqa: E501
from swagger_server import util


def get_echo():  # noqa: E501
    """Ritorna un timestamp in formato RFC5424.

    Ritorna un timestamp in formato RFC5424 prendendola dal server attuale.  # noqa: E501


    :rtype: Timestampa
    """
    return Timestampa(datetime.datetime.utcnow())