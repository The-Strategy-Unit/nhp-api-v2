import logging

import azure.functions as func

from run_model import bp_run_model
from status import bp_status

logging.getLogger("azure").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

app.register_functions(bp_run_model)
app.register_functions(bp_status)
