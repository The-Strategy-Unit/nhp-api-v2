import json
import logging

import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.mgmt.containerinstance import ContainerInstanceManagementClient

import config
from status.helpers import get_container_group_instance_state


def model_run_status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("getting status for model run")
    container_group_name = req.route_params.get("id")

    client = ContainerInstanceManagementClient(
        DefaultAzureCredential(), config.SUBSCRIPTION_ID
    )
    resource_group = config.RESOURCE_GROUP

    container = get_container_group_instance_state(
        container_group_name, client, resource_group
    )

    return func.HttpResponse(
        json.dumps(container.as_dict()), mimetype="application/json"
    )
