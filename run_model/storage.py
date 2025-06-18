
import logging

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

import config


def upload_params_to_blob(
    params: dict, metadata: dict, credential: DefaultAzureCredential
) -> None:
    client = BlobServiceClient(config.STORAGE_ENDPOINT, credential)
    container = client.get_container_client("queue")
    try:
        container.upload_blob(f"{metadata['id']}.json", params, metadata=metadata)
        logging.info("params uploaded to queue")
    except ResourceExistsError:
        logging.warning("file already exists, skipping upload")