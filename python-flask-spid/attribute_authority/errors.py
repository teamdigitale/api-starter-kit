import jwt
from connexion import problem
from flask import current_app as app
from flask import request


def invalid_token_handler(exception):
    try:
        deserialized = jwt.decode(request.data, verify=0)
    except Exception as e:
        deserialized = {"err": repr(e)}
    return problem(
        title="invalid token",
        status=400,
        detail="Expected audience was {audience}".format(
            audience=app.config["entityId"]
        ),
        type="https://www.spid.gov.it/aa/problem/InvalidToken",
        ext={"data": request.data, "json": deserialized},
    )
