# NHP API v2

This project is an Azure Functions-based Python API for managing and running NHP model runs using Azure Container Instances.

It is a thin wrapper around the [nhp-aci](https://github.com/the-strategy-unit/nhp_aci) package.

## Endpoints

- `POST /api/run_model` — Start a new model run
- `GET /api/model_run_status/{id}` — Get status for a specific model run
- `GET /api/list_current_model_runs` — List all active model runs

## Setup

1. **Install dependencies**  

Create a virtual environment and install requirements:

```sh
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Local development**

Configure environment variables by copying `.env.sample` to `.env`.

Use VS Code tasks to start the Azure Functions host:

```sh
func start
```

Or use the provided VS Code launch configuration to attach the debugger.

## Deployment

Currently deploying via GitHub actions is disabled. Locally, run

```sh
func azure functionapp publish [FUNCTION_APP_NAME]
```
