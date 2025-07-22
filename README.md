# NHP Model Runner

A serverless Azure Function App for running and monitoring National Health Planning (NHP) simulation models in Azure Container Instances.

## Overview

This application provides an API-driven service to execute healthcare planning simulation models in a scalable, cloud-native environment. The NHP models help healthcare planners analyse patient flows, resource utilisation, and capacity requirements across inpatient, outpatient, and A&E (Accident & Emergency) services.

### Why This Approach?

Traditional approaches to running these models often involve manual execution on local machines, leading to:
- Limited computational resources
- Inconsistent environments
- Poor scalability for multiple scenarios
- Difficulty tracking progress

This solution addresses these challenges by:
- Automating model execution in isolated containers
- Standardising the execution environment
- Enabling parallel runs with controlled resource allocation
- Providing real-time status monitoring

## Architecture

```
┌───────────────┐      ┌───────────────┐      ┌───────────────────────┐
│  HTTP Client  │──────▶  Azure        │──────▶  Azure Container      │
│  (API User)   │      │  Function App │      │  Instances (Models)   │
└───────────────┘      └───────┬───────┘      └───────────┬───────────┘
                               │                          │
                               │                          │
                               ▼                          ▼
                      ┌────────────────┐         ┌────────────────┐
                      │ Azure Blob     │◀────────│ Model Output & │
                      │ Storage        │─────────▶ Progress Data  │
                      └────────────────┘         └────────────────┘
                               ▲
                               │
                               ▼
                      ┌────────────────┐
                      │ Log Analytics  │
                      │ Workspace      │
                      └────────────────┘
```

### Key Components

- **Run Model API**: Validates parameters, generates run IDs, provisions containers
- **Status API**: Monitors container state and model execution progress
- **Azure Container Instances**: Executes the NHP model code with specified resources
- **Azure Blob Storage**: Stores input parameters and tracks model progress
- **Azure Log Analytics**: Collects and centralises container logs

## Project Structure

```
.
├── config.py                        # Configuration and environment variables
├── function_app.py                  # Azure Function App registration
├── host.json                        # Function App host configuration
├── params-sample.json               # Example model parameters
├── requirements.txt                 # Python dependencies
├── run_model                        # Model execution module
│   ├── __init__.py                  # Blueprint registration
│   ├── aci.py                       # Container Instance creation
│   ├── helpers.py                   # Parameter processing utilities
│   └── storage.py                   # Blob storage operations
└── status                           # Model status module
    ├── __init__.py                  # Blueprint registration
    ├── helpers.py                   # Shared status utilities
    ├── list_current_model_runs.py   # Container listing functionality
    └── model_run_status.py          # Individual run status checks
```

## Prerequisites

- Azure subscription
- Azure CLI installed (for deployment)
- The following Azure resources:
  - Storage Account with a `queue` container
  - Log Analytics Workspace
  - User-assigned Managed Identity with permissions for:
    - Storage Blob Data Contributor on the Storage Account
    - Contributor on the Container Instance resource group
  - Virtual Network with subnet delegated to Container Instances
  - Resource Group for all resources

## Setup

1. Clone this repository
2. Create a `.env` file based on the template below
3. Deploy to Azure Functions

### Environment Variables

Create a `.env` file with the following variables:

```
# Azure Resources
STORAGE_ACCOUNT=<storage-account-name>
SUBSCRIPTION_ID=<azure-subscription-id>
AZURE_LOCATION=<azure-region>
RESOURCE_GROUP=<resource-group-name>

# Container Configuration
CONTAINER_IMAGE_GHCR=<github-container-registry-path>  # e.g., ghcr.io/the-strategy-unit/nhp_model
CONTAINER_MEMORY=4
CONTAINER_CPU=2
AUTO_DELETE_COMPLETED_CONTAINERS=true

# Networking
SUBNET_NAME=<subnet-name>
SUBNET_ID=<subnet-resource-id>

# Identity & Monitoring
USER_ASSIGNED_IDENTITY=<managed-identity-resource-id>
LOG_ANALYTICS_WORKSPACE_ID=<workspace-id>
LOG_ANALYTICS_WORKSPACE_KEY=<workspace-key>
LOG_ANALYTICS_WORKSPACE_RESOURCE_ID=<workspace-resource-id>
```

Note: `CONTAINER_IMAGE`, `REGISTRY_USERNAME`, and `REGISTRY_PASSWORD` are defined in the config but not actively used. The system uses `CONTAINER_IMAGE_GHCR` with managed identity authentication instead.

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up local settings
cp queue/params-sample.json local.settings.json
# Edit local.settings.json with your values

# Run locally
func start
```

### Azure Deployment

```bash
# Login to Azure
az login

# Deploy to Azure Functions
func azure functionapp publish <app-name>
```

## Supported Model Versions

The system supports multiple versions of the NHP model:

- **Before v4.0**: Uses `/opt/docker_run.py` as the entry point
- **v4.0 and later**: Uses `/app/.venv/bin/python -m nhp.docker` as the entry point
- **dev tag**: Uses the v4.0+ entry point

Version-specific parameter schemas are fetched from `https://the-strategy-unit.github.io/nhp_model/{app_version}/params-schema.json`.

## API Usage

### Run a Model

```
POST /api/run_model?app_version=v4.0&save_full_model_results=true
Content-Type: application/json

{
  "dataset": "northwest-region",
  "scenario": "capacity-increase-10pct",
  "model_runs": 100,
  "random_seed": 42,
  "parameters": {
    "length_of_stay": {
      "mean": 5.2,
      "std_dev": 1.3
    },
    "arrival_rate": {
      "weekday": 45,
      "weekend": 65
    }
  }
}
```

Query Parameters:
- `app_version`: Model version to use (default: "latest")
- `save_full_model_results`: Whether to store complete results (default: false)

#### Response

```json
{
  "id": "northwest-region-capacity-increase-10pct-a1b2c3d4",
  "dataset": "northwest-region",
  "scenario": "capacity-increase-10pct",
  "model_runs": "100",
  "random_seed": "42",
  "app_version": "v4.0",
  "create_datetime": "20250721_143000"
}
```

### Check Model Run Status

```
GET /api/model_run_status/{id}
```

#### Response

```json
{
  "complete": {
    "inpatients": 75,
    "outpatients": 100,
    "aae": 50
  },
  "model_runs": 100,
  "state": "Running",
  "start_time": "2025-07-21T14:30:00Z",
  "detail_status": "Running"
}
```

Possible states:
- `Creating`: Container is being provisioned
- `Running`: Model is executing
- `Terminated`: Model run has completed (check `detail_status` for outcome)

### List Current Model Runs

```
GET /api/list_current_model_runs
```

#### Response

```json
{
  "northwest-region-capacity-increase-10pct-a1b2c3d4": {
    "state": "Running",
    "start_time": "2025-07-21T14:30:00Z",
    "detail_status": "Running"
  },
  "northwest-region-baseline-e5f6g7h8": {
    "state": "Terminated",
    "start_time": "2025-07-21T13:00:00Z",
    "exit_code": 0,
    "detail_status": "Completed"
  }
}
```

## End-to-End Example

1. **Submit a model run**:
   ```bash
   curl -X POST https://your-function-app.azurewebsites.net/api/run_model?app_version=v4.0 \
     -H "Content-Type: application/json" \
     -H "x-functions-key: your-function-key" \
     -d @queue/params-sample.json
   ```

2. **Monitor progress**:
   ```bash
   curl https://your-function-app.azurewebsites.net/api/model_run_status/northwest-region-baseline-a1b2c3d4 \
     -H "x-functions-key: your-function-key"
   ```

3. **Access results**: When complete, model results are stored in the Storage Account:
   - Standard results: `https://{storage-account}.blob.core.windows.net/results/{id}.json`
   - Full results (if requested): `https://{storage-account}.blob.core.windows.net/results/{id}_full.json`

## Accessing Container Logs

1. Navigate to the Log Analytics workspace in Azure Portal
2. Select "Logs" from the left menu
3. Query container logs with:
   ```kusto
   ContainerInstanceLogs_CL
   | where ContainerGroup_s == "your-model-id"
   | order by TimeGenerated asc
   | project TimeGenerated, LogMessage_s
   ```

## Extending the Code

### Adding New API Endpoints

1. Create a new function in an existing blueprint or create a new blueprint:
   ```python
   @bp_status.route(route="new_endpoint", auth_level=func.AuthLevel.FUNCTION)
   def new_endpoint(req: func.HttpRequest) -> func.HttpResponse:
       # Implementation
       return func.HttpResponse(json.dumps(result), mimetype="application/json")
   ```

2. Register the blueprint in `function_app.py` if creating a new one:
   ```python
   from new_module import bp_new_module
   app.register_functions(bp_new_module)
   ```

### Modifying Container Configuration

Container configuration is managed in `run_model/aci.py`. The key aspects you can modify:

- **Resource allocation**: Change `CONTAINER_MEMORY` and `CONTAINER_CPU` in the environment
- **Environment variables**: Add to the `environment_variables` list in the `Container` constructor
- **Entry command**: Modify the `command` logic based on version requirements
- **Networking**: Update subnet configuration or add network security groups
- **Monitoring**: Adjust Log Analytics settings

## Troubleshooting

- **Container Creation Failures**:
  - Check Azure Portal > Container Instances > your-model-id > Events
  - Verify network connectivity to storage and the container registry
  - Ensure the managed identity has appropriate permissions

- **Parameter Validation Errors**:
  - Check that your parameters match the schema for the specified app version
  - Verify the schema is accessible at the expected URL
  - Review the example in `queue/params-sample.json` for guidance

- **Missing Results**:
  - Check container logs for execution errors
  - Verify the storage account is accessible from the container
  - Check for blob storage errors in the Function App logs

- **Function App Errors**:
  - Review logs in Azure Portal > Function App > your-app > Functions > function-name > Monitor

## Licence

[Add appropriate licence information]

## Contributing

[Add contribution guidelines]
