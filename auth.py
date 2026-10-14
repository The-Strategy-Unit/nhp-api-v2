import base64
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import azure.functions as func


def get_client_principal(req: func.HttpRequest) -> dict:
    value = req.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not value:
        raise ValueError("No authenticated client principal")

    decoded = base64.b64decode(value).decode("utf-8")

    return json.loads(decoded)


def get_roles(req: func.HttpRequest) -> set[str]:
    principal = get_client_principal(req)

    return {
        claim["val"]
        for claim in principal.get("claims", [])
        if claim.get("typ") == "roles"
    }


def has_role(req: func.HttpRequest, *required_roles: str) -> bool:
    return bool(get_roles(req) & set(required_roles))


def require_role(*roles: str) -> Callable:
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(
            req: func.HttpRequest, *args: Any, **kwargs: Any
        ) -> func.HttpResponse:
            if not has_role(req, *roles):
                return func.HttpResponse("Forbidden", status_code=403)

            return handler(req, *args, **kwargs)

        return wrapper

    return decorator
