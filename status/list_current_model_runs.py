from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config
from status.helpers import get_container_group_instance_state


def get_current_model_runs() -> dict:
    """
    Get the status of all current model runs.
    """
    client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), config.SUBSCRIPTION_ID
    )
    resource_group = config.RESOURCE_GROUP

    containers = {
        i.name: get_container_group_instance_state(i.name, client, resource_group)
        for i in client.container_groups.list_by_resource_group(resource_group)
    }

    return containers
