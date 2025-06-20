"""Configuration values"""

# pylint: disable=line-too-long

import os

import dotenv

dotenv.load_dotenv()

STORAGE_ACCOUNT = os.environ["STORAGE_ACCOUNT"]
STORAGE_ENDPOINT = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
CONTAINER_IMAGE = os.environ["CONTAINER_IMAGE"]
CONTAINER_IMAGE_GHCR = os.environ["CONTAINER_IMAGE_GHCR"]
AZURE_LOCATION = os.environ["AZURE_LOCATION"]
SUBNET_NAME = os.environ["SUBNET_NAME"]
SUBNET_ID = os.environ["SUBNET_ID"]
REGISTRY_USERNAME = os.environ["REGISTRY_USERNAME"]
REGISTRY_PASSWORD = os.environ["REGISTRY_PASSWORD"]
USER_ASSIGNED_IDENTITY = os.environ["USER_ASSIGNED_IDENTITY"]

CONTAINER_MEMORY = os.environ["CONTAINER_MEMORY"]
CONTAINER_CPU = os.environ["CONTAINER_CPU"]

AUTO_DELETE_COMPLETED_CONTAINERS = bool(os.getenv("AUTO_DELETE_COMPLETED_CONTAINERS"))

RESOURCE_GROUP = os.environ["RESOURCE_GROUP"]


LOG_ANALYTICS_WORKSPACE_ID = os.environ["LOG_ANALYTICS_WORKSPACE_ID"]
LOG_ANALYTICS_WORKSPACE_KEY = os.environ["LOG_ANALYTICS_WORKSPACE_KEY"]
LOG_ANALYTICS_WORKSPACE_RESOURCE_ID = os.environ["LOG_ANALYTICS_WORKSPACE_RESOURCE_ID"]
