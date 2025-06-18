import logging

from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (
    Container,
    ContainerGroup,
    ContainerGroupDiagnostics,
    ContainerGroupIdentity,
    ContainerGroupSubnetId,
    EnvironmentVariable,
    LogAnalytics,
    OperatingSystemTypes,
    ResourceRequests,
    ResourceRequirements,
)

import config


def create_and_start_container(
    metadata: dict,
    credential: DefaultAzureCredential,
    save_full_model_results: bool = False,
) -> None:
    model_id = metadata["id"]
    tag = metadata["app_version"]

    client = ContainerInstanceManagementClient(credential, config.SUBSCRIPTION_ID)

    container_resource_requests = ResourceRequests(
        memory_in_gb=config.CONTAINER_MEMORY, cpu=config.CONTAINER_CPU
    )
    container_resource_requirements = ResourceRequirements(
        requests=container_resource_requests
    )

    # before v4.0, the containers are started using /opt/docker_run.py
    if tag == "dev" or tag[:2] >= "v4":
        command = "/app/.venv/bin/python -m nhp.docker"
    else:
        command = "/opt/docker_run.py"

    container = Container(
        name=model_id,
        image=f"{config.CONTAINER_IMAGE_GHCR}:{tag}",
        resources=container_resource_requirements,
        environment_variables=[
            EnvironmentVariable(name="STORAGE_ACCOUNT", value=config.STORAGE_ACCOUNT)
        ],
        command=[
            command,
            f"{model_id}.json",
            *(["--save-full-model-results"] if save_full_model_results else []),
        ],
    )

    subnet = ContainerGroupSubnetId(id=config.SUBNET_ID, name=config.SUBNET_NAME)

    identity = ContainerGroupIdentity(
        type="UserAssigned",
        user_assigned_identities={config.USER_ASSIGNED_IDENTITY: {}},
    )

    diagnostics = ContainerGroupDiagnostics(
        log_analytics=LogAnalytics(
            workspace_id=config.LOG_ANALYTICS_WORKSPACE_ID,
            workspace_key=config.LOG_ANALYTICS_WORKSPACE_KEY,
            workspace_resource_id=config.LOG_ANALYTICS_WORKSPACE_RESOURCE_ID,
            log_type="ContainerInstanceLogs",
        )
    )

    cgroup = ContainerGroup(
        identity=identity,
        location=config.AZURE_LOCATION,
        containers=[container],
        os_type=OperatingSystemTypes.linux,
        diagnostics=diagnostics,
        restart_policy="Never",
        subnet_ids=[subnet],
        tags={"project": "nhp"},
    )

    client.container_groups.begin_create_or_update(
        config.RESOURCE_GROUP, f"{model_id}", cgroup
    )
    logging.info("container created with command: %s", " ".join(container.command))
