from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config
from status.helpers import get_container_group_instance_state


def get_model_run_status(container_group_name: str) -> dict:
    """
    Get the status of a model run by its container group name.
    """
    client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), config.SUBSCRIPTION_ID
    )
    resource_group = config.RESOURCE_GROUP

    container = get_container_group_instance_state(
        container_group_name, client, resource_group
    )

    return container
