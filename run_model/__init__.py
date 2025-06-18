import json
import logging
from datetime import datetime, timezone

import azure.functions as func
from azure.identity import DefaultAzureCredential

from run_model.aci import create_and_start_container
from run_model.helpers import generate_id
from run_model.storage import upload_params_to_blob

bp_run_model = func.Blueprint()


@bp_run_model.route(route="run_model", auth_level=func.AuthLevel.FUNCTION)
def run_model(req: func.HttpRequest) -> func.HttpResponse:
    params = req.get_json()
    if "id" in params:
        params.pop("id")
    params["create_datetime"] = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"

    metadata = {
        k: str(v)
        for k, v in params.items()
        if not isinstance(v, dict) and not isinstance(v, list)
    }
    params["app_version"] = metadata["app_version"] = req.params.get(
        "app_version", "latest"
    )

    save_full_model_results = (
        req.params.get("save_full_model_results", "").lower() == "true"
    )

    params = json.dumps(params)
    metadata["id"] = generate_id(params, metadata)

    logging.info(
        "received request for model run %s (%s)",
        metadata["id"],
        metadata["app_version"],
    )

    credential = DefaultAzureCredential()

    # 1. upload params to blob storage
    upload_params_to_blob(params, metadata, credential)

    # 2. create a new container instance
    create_and_start_container(metadata, credential, save_full_model_results)

    return func.HttpResponse(json.dumps(metadata), mimetype="application/json")
