from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.storage.blob import BlobServiceClient

import config
from status.helpers import get_container_group_instance_state


def _get_queue_metadata(
    container_group_name: str, cred: DefaultAzureCredential
) -> dict:

    bsc = BlobServiceClient(config.STORAGE_ENDPOINT, cred)
    cc = bsc.get_container_client("queue")
    bc = cc.get_blob_client(f"{container_group_name}.json")

    if not bc.exists():
        return {}

    m = bc.get_blob_properties()["metadata"]

    model_runs = int(m["model_runs"])

    def get_progress(key):
        return min(int(m.get(key, 0)), model_runs)

    return {
        "complete": {
            "inpatients": get_progress("Inpatients"),
            "outpatients": get_progress("Outpatients"),
            "aae": get_progress("AaE"),
        },
        "model_runs": model_runs,
    }


def _get_aci_status(container_group_name: str, cred: DefaultAzureCredential) -> dict:
    client = ContainerInstanceManagementClient(cred, config.SUBSCRIPTION_ID)
    resource_group = config.RESOURCE_GROUP

    return get_container_group_instance_state(
        container_group_name, client, resource_group
    )


def get_model_run_status(container_group_name: str) -> dict:
    """
    Get the status of a model run by its container group name.
    """

    cred = DefaultAzureCredential()
    status = _get_queue_metadata(container_group_name, cred)

    try:
        return {**status, **_get_aci_status(container_group_name, cred)}

    except ResourceNotFoundError:
        if status:
            return {**status, "state": "Creating"}
        return None
