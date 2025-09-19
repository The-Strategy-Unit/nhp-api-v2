import json
import logging

import azure.functions as func
from nhp.aci.status import get_current_model_runs, get_model_run_status

bp_status = func.Blueprint()
logger = logging.getLogger(__name__)


@bp_status.route(route="model_run_status/{id}", auth_level=func.AuthLevel.FUNCTION)
def model_run_status(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("getting status for model run")

    container_group_name = req.route_params.get("id")
    try:
        res = get_model_run_status(container_group_name)

        if res:
            status_code = 200
        else:
            status_code = 404
            res = {"error": f"no model run found for f{container_group_name}"}
            logger.error(res["error"])
    except Exception as e:
        res = {"error": {"type": type(e).__name__, "text": str(e)}}
        logger.error(res["error"])
        status_code = 500

    return func.HttpResponse(
        json.dumps(res), mimetype="application/json", status_code=status_code
    )


@bp_status.route(route="list_current_model_runs", auth_level=func.AuthLevel.FUNCTION)
def list_current_model_runs(
    req: func.HttpRequest,
) -> func.HttpResponse:  # pylint: disable=unused-argument
    logging.info("listing all active model runs")

    try:
        res = get_current_model_runs()
        status_code = 200
    except Exception as e:
        res = {"error": {"type": type(e).__name__, "text": str(e)}}
        logger.error(res["error"])
        status_code = 500

    return func.HttpResponse(
        json.dumps(res), mimetype="application/json", status_code=status_code
    )
