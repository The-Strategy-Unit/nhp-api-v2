import json
import logging

import azure.functions as func

from status.list_current_model_runs import get_current_model_runs
from status.model_run_status import get_model_run_status

bp_status = func.Blueprint()


@bp_status.route(route="model_run_status/{id}", auth_level=func.AuthLevel.FUNCTION)
def model_run_status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("getting status for model run")

    container_group_name = req.route_params.get("id")
    try:
        status = get_model_run_status(container_group_name)

        if status:
            status_code = 200
        else:
            status_code = 404
            status = {"error": f"no model run found for f{container_group_name}"}
    except Exception as e:
        status_code = 500
        status = {"error": str(e)}

    return func.HttpResponse(
        json.dumps(status), mimetype="application/json", status_code=status_code
    )


@bp_status.route(route="list_current_model_runs", auth_level=func.AuthLevel.FUNCTION)
def list_current_model_runs(
    req: func.HttpRequest,
) -> func.HttpResponse:  # pylint: disable=unused-argument
    logging.info("listing all active model runs")

    current_model_runs = get_current_model_runs()

    return func.HttpResponse(
        json.dumps(current_model_runs), mimetype="application/json"
    )
