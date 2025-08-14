import json

import azure.functions as func
from nhp.aci.run_model import create_model_run

bp_run_model = func.Blueprint()


@bp_run_model.route(route="run_model", auth_level=func.AuthLevel.FUNCTION)
def run_model(req: func.HttpRequest) -> func.HttpResponse:
    # parse request
    params = req.get_json()
    app_version = req.params.get("app_version", "latest")
    save_full_model_results = (
        req.params.get("save_full_model_results", "").lower() == "true"
    )
    # submit model run
    metadata = create_model_run(params, app_version, save_full_model_results)

    # return response
    return func.HttpResponse(json.dumps(metadata), mimetype="application/json")
