import json
import os
import shutil
import sys
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

sys.path.append(str(Path(mgr._base_dir).resolve().absolute()))

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
    res = []
    list_dir = os.listdir(mgr.get_wf_dir())
    for path in list_dir:
        if os.path.isdir(os.path.join(mgr.get_wf_dir(), path)):
            res.append(path)
    return {
        "list": res
    }

@app.route("/workflows/<wf_name>")
def wf_info(wf_name):
    config_file_path = mgr.get_wf_config_file(wf_name)
    if os.path.exists(config_file_path):
        config_str = open(mgr.get_wf_config_file(wf_name), "r").read()
        print(config_str)
        c = WfRunConfig.from_json(config_str)
        return {
            "name": wf_name,
            **c.to_dict(),
        }
    else:
        c = WfRunConfig()
        return {
            "name": wf_name,
            **c.to_dict(),
            "msg": "you don't have config.json"
        }

@app.route("/workflows/<wf_name>/runs")
def wf_runs(wf_name):
    res = []
    runs_dir = mgr.get_runs_dir(wf_name)
    if os.path.exists(runs_dir):
      runs_list = os.listdir(runs_dir)
      runs_list.sort(reverse=True)
    #   runs_list = runs_list[::-1]
    else:
      runs_list = []
    for run_name in runs_list:
        status = Status.PENDING.value
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


@app.delete("/workflows/<wf_name>/runs/<run_name>")
def delete_wf_run(wf_name, run_name):
    run_dir = mgr.get_wf_runs_run_dir(wf_name, run_name)
    shutil.rmtree(run_dir)
    return {}

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

    status_file = mgr.get_wf_run_all_os_status_file(wf_name, run_name)
    if not os.path.exists(status_file):
        status = Status.PENDING.value
    else:
        status = open(status_file, "r").read()
    return {
        "list": res,
        "status": status
    }

@app.route("/workflows/<wf_name>/runs/<run_name>/<os_name>")
def wf_run_os_info(wf_name, run_name, os_name):
    log_path = mgr.get_wf_run_single_os_result_file(wf_name, run_name, os_name)
    if not os.path.exists(log_path):
        print(f"[日志]: 没有 config.result.json, {log_path}")
        return {}
    else:
        return {**json.loads(open(log_path, "r").read()),
    }

@app.route("/workflows/<wf_name>/runs/<run_name>/<os_name>/<path:job_path>")
def wf_run_os_job_info(wf_name, run_name, os_name, job_path):
    log_path = mgr.get_wf_run_single_os_job_dir(wf_name, run_name, os_name, job_path)
    print("查询的日志路径", log_path)
    logs: List[dict] = []
    get_file_tree(log_path, "", logs)
    logs = sorted(logs, key=lambda x: x["name"])

    png_list = []
    txt_list = []
    for log in logs:
        if log["name"].endswith(".png"):
            png_list.append(log)
        else:
            txt_list.append(log)

    return {
        "pyscript": open(mgr.get_job_file(job_path), "r").read(),
        "logs": [*txt_list, *png_list]
    }

def get_file_tree(_base_dir, _relative_dir, logs_ref: List[dict]):
    res = []
    full_dir = os.path.join(_base_dir, _relative_dir)
    if not os.path.exists(full_dir):
        return []
    for f in os.listdir(full_dir):
        print(f"里面有: {f}")
        # 绝对路径
        path = os.path.join(full_dir, _relative_dir, f)

        # 相对路径
        relative_path = os.path.join(_relative_dir, f)

        linkk = str(os.path.join(_base_dir, relative_path))
        linkk = linkk[len(str(base_dir)):]
        link = f"{app.static_url_path}/{linkk}"
        print(f"判断的路径 {path}, is_dir: {os.path.isdir(path)}")
        if os.path.isdir(path):
            res.append({
                "name": f,
                "type": "dir",
                "children": get_file_tree(_base_dir, relative_path, logs_ref)
            })
        else:
            res.append({
                "name": relative_path,
                "path": link,
                "type": "file"
            })
            logs_ref.append({
                "name": relative_path,
                "path": link,
                "type": "file"
            })
    return res

@app.route("/workflows/<wf_name>/run")
def wf_run(wf_name):
    mgr.run(wf_name)
    # threading.Thread(target=mgr.run, args=(wf_name)).start()
    return {  }

app.run(host="0.0.0.0", port=5000, debug=True)