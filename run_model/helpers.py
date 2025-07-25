import json
import logging
import re
import zlib
from datetime import datetime, timezone
from typing import Tuple

import requests
from azure.identity import DefaultAzureCredential
from jsonschema import validate

from run_model.aci import create_and_start_container
from run_model.storage import upload_params_to_blob


def generate_id(params: str, metadata: dict) -> str:
    crc32 = f"{zlib.crc32(params.encode('utf-8')):x}"
    scenario_sanitized = re.sub("[^a-z0-9]+", "-", metadata["scenario"])
    # id needs to be of length 1-63, but the last 9 characters are a - and the hash
    return (f"{metadata['dataset']}-{scenario_sanitized}"[0:54] + "-" + crc32).lower()


def get_metadata(params: dict) -> dict:
    """
    Extract metadata from the parameters dictionary.
    """
    metadata = {
        k: str(v)
        for k, v in params.items()
        if not isinstance(v, dict) and not isinstance(v, list)
    }

    return metadata


def prepare_params(params: dict, app_version: str) -> Tuple[str, dict]:
    # check that the params are valid according to the schema
    validate_params(params, app_version)

    # the id paramerter used to be submitted, but is now generated here to prevent issues with the
    # containers being created with invalid ids.
    if "id" in params:
        params.pop("id")
    # force the create_datetime to be the current time, do not accept values from the user
    params["create_datetime"] = f"{datetime.now(timezone.utc):%Y%m%d_%H%M%S}"

    # get the metadata from the params
    metadata = get_metadata(params)
    # set the app_version in the params and metadata
    params["app_version"] = metadata["app_version"] = app_version

    # convert params to a JSON string
    params_str = json.dumps(params)
    # generate the id based on the params and metadata
    metadata["id"] = generate_id(params_str, metadata)

    return params_str, metadata


def validate_params(params: dict, app_version: str) -> None:
    uri = f"https://the-strategy-unit.github.io/nhp_model/{app_version}/params-schema.json"
    req = requests.get(uri)
    if req.status_code != 200:
        logging.warning("Unable to validate schema for app_version %s", app_version)
        return
    schema = req.json()
    validate(params, schema)


def create_model_run(
    params: dict, app_version: str, save_full_model_results: bool = False
) -> dict:
    credential = DefaultAzureCredential()

    # 1. prepare params and metadata
    params_str, metadata = prepare_params(params, app_version)

    logging.info(
        "received request for model run %s (%s)",
        metadata["id"],
        metadata["app_version"],
    )

    # 2. upload params to blob storage
    upload_params_to_blob(params_str, metadata, credential)

    # 3. create a new container instance
    create_and_start_container(metadata, credential, save_full_model_results)

    return metadata
