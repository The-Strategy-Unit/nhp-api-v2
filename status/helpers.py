from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config


def get_container_group_instance_state(
    container_group_name: str,
    client: ContainerInstanceManagementClient,
    resource_group: str,
) -> dict:
    container = client.container_groups.get(
        resource_group, container_group_name
    ).containers[0]

    if container.instance_view is None:
        return {}

    if (
        config.AUTO_DELETE_COMPLETED_CONTAINERS
        and container.state == "Terminated"
        and container.detail_status == "Completed"
    ):
        client.container_groups.begin_delete(resource_group, container_group_name)

    return container.as_dict()
