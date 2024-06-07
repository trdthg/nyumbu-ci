import json
import os
from pathlib import Path
from flask import Flask
from flask_cors import CORS
from src.nyumbu_server.job import Status
from src.nyumbu_server.workflow import WfRunConfig, Workflow
from serde.json import from_json
app = Flask(__name__)
CORS(app)

base_dir = Path(os.environ.get("BASE_DIR", "nyumbu_workspace"))
wf = Workflow(base_dir = base_dir)

# - job
# - os
# - wf
#     - ruyi
#         - config.json
#         - logs
#             - YYMMDDHHMMSS
#                 - job1
#                 - job2
#     - other
#         - ...
@app.route("/workflows")
def wf_list():
    return {
        "list": os.listdir(wf.wf_dir)
    }

@app.route("/workflows/<wf_name>/info")
def wf_info(wf_name):
    c = from_json(WfRunConfig, open(os.path.join(wf.wf_dir, wf_name, "config.json"), "r").read())
    return {
        "name": wf_name,
        "os_list": c.os_list,
        "runs": os.listdir(os.path.join(wf.wf_dir, wf_name, "runs"))
    }

@app.route("/workflows/<wf_name>/runs/<run_name>/info")
def wf_run_info(wf_name, run_name):
    return {
        "name": run_name,
        "jobs": os.listdir(os.path.join(wf.wf_dir, wf_name, "runs", run_name))
    }

app.run(host="0.0.0.0", port=5000, debug=True)