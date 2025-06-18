import azure.functions as func

from status.list_current_model_runs import list_current_model_runs
from status.model_run_status import model_run_status

bp_status = func.Blueprint()

bp_status.route(route="list_current_model_runs", auth_level=func.AuthLevel.FUNCTION)(
    list_current_model_runs
)
bp_status.route(route="model_run_status", auth_level=func.AuthLevel.FUNCTION)(
    model_run_status
)
