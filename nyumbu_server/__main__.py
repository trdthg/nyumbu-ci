import json
import os
from pathlib import Path
import threading
from typing import List
from flask import Flask, jsonify
from flask_cors import CORS
from src.nyumbu_server.job import Status
from src.nyumbu_server.workflow import WfRunConfig, Workflow, WfRunJobConfig

base_dir = Path(os.environ.get("BASE_DIR", "nyumbu_workspace"))

app = Flask(__name__, static_folder=base_dir, static_url_path="/static")
CORS(app)

mgr = Workflow(base_dir = base_dir)

# - job
#   - test1.py
#   - test2.py
# - os
#   - ubuntu
#       - pyautotest.toml
#       - domain.xml
#       - ubuntu24.04.img
#       - disk.block
# - wf
#     - ruyi
#         - config.json
#           - name, os_list, jobs: [ {name, children }]
#         - runs
#             - YYMMDDHHMMSS
#                 - status (all os_status)
#                 - os1 (singal os status)
#                    - status
#                    - result.json
#                       - jobs: [ { name, status, children? } ]
#                    - job1
#                    - job1-1
#                    - job1-2
#                       - os1
#                       - a.log
#                 - os2
#                    - a.log
#                    - b.jpg
#             - YYMMDDHHMMSS
#             - YYMMDDHHMMSS
#             - YYMMDDHHMMSS
#     - other
#         - ...
@app.route("/workflows")
def wf_list():
    return {
        "list": os.listdir(mgr.get_wf_dir())
    }

@app.route("/workflows/<wf_name>")
def wf_info(wf_name):
    config_str = open(mgr.get_wf_config_file(wf_name), "r").read()
    print(config_str)
    c = WfRunConfig.from_json(config_str)
    return {
        "name": wf_name,
        **c.to_dict(),
    }

@app.route("/workflows/<wf_name>/runs")
def wf_runs(wf_name):
    res = []
    for run_name in os.listdir(mgr.get_runs_dir(wf_name)):
        status = "empty"
        try:
            status_file = mgr.get_wf_run_all_os_status_file(wf_name, run_name)
            status = open(status_file, "r").read()
        except:
            pass

        res.append({
            "status": status,
            "run_name": run_name
        })
    return {
        "list": res
    }

@app.route("/workflows/<wf_name>/runs/<run_name>")
def wf_run_info(wf_name, run_name):
    c = mgr.get_wf_config(wf_name)
    res = []
    for os_name in c.os_list:
        status_file = mgr.get_wf_run_single_os_status_file(wf_name, run_name, os_name)
        try:
            status = open(status_file, "r").read()
        except:
            status = Status.PENDING.value
        res.append({
            "os": os_name,
            "status": status,
        })
    return {
        "list": res,
        "status": open(mgr.get_wf_run_all_os_status_file(wf_name, run_name), "r").read()
    }

@app.route("/workflows/<wf_name>/runs/<run_name>/<os_name>")
def wf_run_os_info(wf_name, run_name, os_name):
    log_path = mgr.get_wf_run_single_os_dir(wf_name, run_name, os_name)
    return {
        **json.loads(open(mgr.get_wf_run_single_os_result_file(wf_name, run_name, os_name), "r").read()),
    }

@app.route("/workflows/<wf_name>/runs/<run_name>/<os_name>/<path:job_path>")
def wf_run_os_job_info(wf_name, run_name, os_name, job_path):
    log_path = mgr.get_wf_run_single_os_job_dir(wf_name, run_name, os_name, job_path)
    return {
        "pyscript": open(mgr.get_job_file(job_path), "r").read(),
        "logs": get_file_tree(log_path, "")
    }

def get_file_tree(base_dir, _relative_dir):
    res = []
    full_dir = os.path.join(base_dir, _relative_dir)
    print(base_dir)
    print(_relative_dir)
    if not os.path.exists(full_dir):
        return []
    for f in os.listdir(full_dir):
        path = os.path.join(full_dir, _relative_dir, f)
        relative_dir = os.path.join(_relative_dir, f)
        final_relative_dir = os.path.join(base_dir, relative_dir)
        if os.path.isdir(path):
            res.append({
                "type": "dir",
                "path": final_relative_dir,
                "children": get_file_tree(base_dir, relative_dir)
            })
        else:
            res.append({
                "path": final_relative_dir,
                "type": "file"
            })
    return res

@app.route("/workflows/<wf_name>/run")
def wf_run(wf_name):
    mgr.run(wf_name)
    # threading.Thread(target=mgr.run, args=(wf_name)).start()
    return {  }

app.run(host="0.0.0.0", port=5000, debug=True)