import base64
import binascii
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

import azure.functions as func


def get_client_principal(req: func.HttpRequest) -> dict:
    value = req.headers.get("X-MS-CLIENT-PRINCIPAL")

    if not value:
        raise ValueError("No authenticated client principal")

    try:
        decoded = base64.b64decode(value).decode("utf-8")
    except (ValueError, TypeError, binascii.Error):
        raise ValueError("Invalid authenticated client principal") from None

    try:
        return json.loads(decoded)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid authenticated client principal") from exc


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
            try:
                if not has_role(req, *roles):
                    return func.HttpResponse("Forbidden", status_code=403)
            except (TypeError, ValueError):
                return func.HttpResponse("Unauthorized", status_code=401)

            return handler(req, *args, **kwargs)

        return wrapper

    return decorator
