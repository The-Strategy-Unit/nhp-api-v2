import logging
import re

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


def _build_container_command(
    model_id: str, tag: str, save_full_model_results: bool
) -> list[str]:
    # before v4.0, the containers are started using /opt/docker_run.py
    match = re.match(r"^v(\d+)\.", tag)
    before_v4 = match and int(match.group(1)) < 4
    command = (
        ["/opt/docker_run.py"]
        if before_v4
        else ["/app/.venv/bin/python", "-m", "nhp.docker"]
    )

    command.append(f"{model_id}.json")
    if save_full_model_results:
        command.append("--save-full-model-results")

    return command


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

    command = _build_container_command(model_id, tag, save_full_model_results)

    container = Container(
        name=model_id,
        image=f"{config.CONTAINER_IMAGE}:{tag}",
        resources=container_resource_requirements,
        environment_variables=[
            EnvironmentVariable(name="STORAGE_ACCOUNT", value=config.STORAGE_ACCOUNT)
        ],
        command=command,
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
    logging.info("container created with command: %s", " ".join(command))
    logging.info("container created with command: %s", " ".join(command))
