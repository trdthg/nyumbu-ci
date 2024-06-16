

import importlib
import inspect
import json
import os
import time
import tomlkit
from typing import List

from .src.nyumbu_server.job import Job, Status, update_jobs_status, work_jobs
from .src.nyumbu_server.db import DB
from .src.nyumbu_server.util import get_timestamp
from .src.nyumbu_server.vm import VM
from .src.nyumbu_server.worker import Workder

import pyautotest

class WfRunJobConfig:
    name: str
    children: List["WfRunJobConfig"]

    def __init__(self, name, children=[]):
        self.name = name
        self.children = children


class WfRunConfig:
    os_list: List[str]
    jobs: List[WfRunJobConfig]

    def __init__(self, os_list: List[str], jobs: List[WfRunJobConfig]):
        self.os_list = os_list
        self.jobs = jobs

    @staticmethod
    def deserialize_from_dict(config_dict: dict):
        c = WfRunConfig([], [])
        c.os_list = config_dict.get("os_list", [])

        def _deserialize_job(job_dict: dict):
            name = job_dict.get("name", "")
            children = []
            for child_dict in job_dict.get("children", {}):
                children.append(_deserialize_job(child_dict))
            return WfRunJobConfig(name, children)

        for job_dict in config_dict.get("jobs"):
            c.jobs.append(_deserialize_job(job_dict))
        return c


class Workflow:
    db: DB

    def __init__(self, base_dir: str = "nyumbu_workspace", db: DB = DB()):
        self.db = db
        self.base_dir = base_dir
        self.os_dir = os.path.join(base_dir, "os")
        self.wf_dir = os.path.join(base_dir, "workflows")
        self.job_dir = os.path.join(base_dir, "jobs")

    def run(self, wf_name: str, wf_json_config_path: str, only_failed: bool = False):
        config_dict = json.loads(open(wf_json_config_path, "r").read())
        c = WfRunConfig.deserialize_from_dict(config_dict)

        start_timestamp = get_timestamp()
        self.db.use(wf_name)[str(start_timestamp)] = {}

        for os_name in c.os_list:

            def _load_jobs(jobs_config: List[WfRunJobConfig]):
                res = []
                for job_config in jobs_config:
                    file_path = f"{self.wf_dir}/{wf_name}/{job_config.name}.py"
                    print(file_path)
                    module_name = os.path.basename(file_path).replace(".py", "")
                    spec = importlib.util.spec_from_file_location(
                        module_name, file_path
                    )
                    module = importlib.util.module_from_spec(spec)

                    spec.loader.exec_module(module)

                    attributes = dir(module)
                    for attr in attributes:
                        if attr.startswith == "main" and inspect.isfunction(getattr(module, attr)):
                            res.append(
                                Job(
                                    job_config.name,
                                    getattr(module, attr),
                                    _load_jobs(job_config.children),
                                )
                            )
                            break
                return res

            jobs = _load_jobs(c.jobs)

            if only_failed:
                results = self.load_result(wf_name, os_name)
                print("loaded results")
                print(results)
                update_jobs_status(jobs, results)

            try:
                os_dir = os.path.join(self.os_dir, os_name)
                domain_xml_str = open(f"{os_dir}/domain.xml", "r").read()

                vm = VM(os_name, domain_xml_str)
                vm.start()

                log_dir = f"./logs/ruyi/{start_timestamp}/{os_name}"
                toml_config_str = open(f"{os_dir}/pyautotest.toml", "r").read()
                # load toml
                toml_config = tomlkit.loads(toml_config_str)
                toml_config["log_dir"] = log_dir
                d = pyautotest.Driver(tomlkit.dumps(toml_config))

                time.sleep(5)
                w = Workder(wf_name, vm, d, jobs)
                w.run()

                print("*" * 100)
                print("jobs: ")
                print(w)
                print("*" * 100)

                d.stop()
                vm.stop()
            except Exception as e:
                print(f"{wf_name} - {os_name} - run failed")
                print(e)

            self.save_result(wf_name, start_timestamp, os_name, w.jobs)
            print("*" * 100)

    # FIX: hahaha~~~
    def load_result(self, wf_name: str, os_name: str):

        def _deserialize_dict(data: dict[str, dict]) -> dict[str, Status]:
            res = {}

            def _deserialize_job(job_map: dict[str, dict]):
                print("job_map", job_map)
                for name, info in job_map.items():
                    res[name] = info.get("status", Status.EMPTY)
                    for child in info.get("children", {}):
                        _deserialize_job(child)

            _deserialize_job(data)
            return res

        def _load_latest_workflow() -> dict[str, Status]:
            time_list = [int(i) for i in self.db.use(wf_name).keys()]
            if len(time_list) == 0:
                return {}

            time_list.sort()
            max_timestamp = str(time_list[-1])
            print("load", wf_name, max_timestamp)
            print(self.db.use(wf_name).get(max_timestamp).get(os_name))
            return _deserialize_dict(
                self.db.use(wf_name).get(max_timestamp, {}).get(os_name, {})
            )

        results = _load_latest_workflow()
        return results

    def save_result(
        self, wf_name: str, start_timestamp: int, os_name: str, jobs: List[Job]
    ):
        def serialize_dict():
            res = {}

            def _serialize_job(job: Job):
                res[job.path] = job.to_dict()
                for child in job.children:
                    _serialize_job(child)
                return True

            work_jobs(jobs, _serialize_job)
            return res

        def serialize_str(self):
            return json.dumps(self.serialize_dict())

        self.db.use(wf_name)[str(start_timestamp)][os_name] = serialize_dict()
        print("save")
        print(self.db.use(wf_name))
        self.db.save()

