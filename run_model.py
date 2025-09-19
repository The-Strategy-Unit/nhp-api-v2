import json
import logging

import azure.functions as func
from nhp.aci.run_model import create_model_run

bp_run_model = func.Blueprint()

logger = logging.getLogger(__name__)


@bp_run_model.route(route="run_model", auth_level=func.AuthLevel.FUNCTION)
def run_model(req: func.HttpRequest) -> func.HttpResponse:
    # parse request
    params = req.get_json()
    app_version = req.params.get("app_version", "latest")
    save_full_model_results = (
        req.params.get("save_full_model_results", "").lower() == "true"
    )
    # submit model run
    try:
        res = create_model_run(params, app_version, save_full_model_results)
        status_code = 200
    except Exception as e:
        res = {"error": {"type": type(e).__name__, "text": str(e)}}
        logger.error(str(e))
        status_code = 500
    return func.HttpResponse(
        json.dumps(res), mimetype="application/json", status_code=status_code
    )
