from __future__ import annotations

from dataclasses import dataclass
import importlib
import inspect
import json
import os
import time
from typing import List

import tomlkit

from .job import Job, Status, update_jobs_status, work_jobs
from .db import DB
from .util import get_timestamp
from .vm import VM
from .worker import Workder

import pyautotest

class WfRunJobConfig:
    path: str
    status: Status
    children: List[WfRunJobConfig]

    def __init__(self, path: str, children: list[WfRunJobConfig] = [], status = Status.EMPTY):
        self.path = path
        self.children = children
        self.status = status

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "status": self.status.value,
            "children": [child.to_dict() for child in self.children]
        }

    def from_dict(config_dict: dict) -> 'WfRunJobConfig':
        path = config_dict.get("path", "")
        children = [WfRunJobConfig.from_dict(child_dict) for child_dict in config_dict.get("children", [])]
        return WfRunJobConfig(path, children, config_dict.get("status", Status.EMPTY))

class WfRunConfig:
    os_list: List[str]
    jobs: List[WfRunJobConfig]

    def __init__(self, os_list: List[str] = [], jobs: List[WfRunJobConfig] = []):
        self.os_list = os_list
        self.jobs = jobs

    @staticmethod
    def from_json(json_str: str) -> 'WfRunConfig':
        config_dict: dict = json.loads(json_str)
        return WfRunConfig(os_list = config_dict.get("os_list", []), jobs= [WfRunJobConfig.from_dict(job_dict) for job_dict in config_dict.get("jobs", [])])

    def to_dict(self) -> dict:
        return {
            "os_list": self.os_list,
            "jobs": [job.to_dict() for job in self.jobs]
        }

class Workflow:
    _os_dir = "os"
    _wf_dir = "workflows"
    _job_dir = "jobs"
    _runs_dir = "runs"


    def __init__(self, base_dir: str = "nyumbu_workspace"):
        self._base_dir = base_dir
        for dir in [self._os_dir, self._wf_dir, self._job_dir]:
            os.makedirs(os.path.join(self._base_dir, dir), exist_ok=True)

    def get_os_dir(self) -> str:
        return os.path.join(self._base_dir, self._os_dir)

    def get_wf_dir(self) -> str:
        return os.path.join(self._base_dir, self._wf_dir)

    def job_dir(self) -> str:
        return os.path.join(self._base_dir, self._job_dir)

    def get_runs_dir(self, wf_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir)

    def get_wf_run_single_os_dir(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name)

    def get_wf_run_single_os_status_file(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name, "status")

    def get_wf_run_single_os_result_file(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name, "config.result.json")

    def get_wf_run_single_os_job_dir(self, wf_name: str, run_name: str, os_name: str, job_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name, job_name)

    def get_wf_run_all_os_status_file(self, wf_name: str, run_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, "status")

    def get_job_file(self, py_filepath_without_ext) -> str:
        return os.path.join(self._base_dir, self._job_dir, py_filepath_without_ext)

    def get_single_os_dir(self, os_name: str) -> str:
        return os.path.join(self._base_dir, self._os_dir, os_name)

    def get_single_os_domain_xml(self, os_name: str) -> str:
        return os.path.join(self._base_dir, self._os_dir, os_name, "domain.xml")

    def get_single_os_toml(self, os_name: str) -> str:
        return os.path.join(self._base_dir, self._os_dir, os_name, "pyautotest.toml")

    def get_wf_config_file(self, wf_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, "config.json")
    
    def _lode_job_tree_with_func(self, jobs_config: List[WfRunJobConfig]):
        res = []
        for job_config in jobs_config:
            file_path = self.get_job_file(job_config.path)
            module_name = os.path.basename(file_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(
                module_name, file_path
            )
            module = importlib.util.module_from_spec(spec)

            spec.loader.exec_module(module)

            attributes = dir(module)

            # find main(pyautotest.Driver) as entry
            for attr in attributes:
                if attr == "main" and inspect.isfunction(getattr(module, attr)):
                    test_function = getattr(module, attr)
                    res.append(
                        Job(
                            job_config.path,
                            test_function,
                            self._lode_job_tree_with_func(job_config.children),
                        )
                    )
                    break

        return res

    def _run_single_os(self, wf_name: str, run_name: str, os_name: str, jobs: List[WfRunJobConfig], run_dry: bool = False):
        run_os_status = Status.EMPTY

        vm = None

        try:
            print("os: ", os_name)
            domain_xml_str = open(self.get_single_os_domain_xml(os_name), "r").read()
            vm = VM(domain_xml_str)
            vm.start()

            print("before try")
            try:
                print("try")
                toml_config_path = self.get_single_os_toml(os_name)
                w = Workder(wf_name, toml_config_path, self.get_wf_run_single_os_dir(), vm, jobs)
                print("worker new")

                if not run_dry:
                    print("try run")
                    try:
                        w.run()
                        jobs = w.jobs
                    except:
                        pass
                vm.stop()
                print("try done")
            except Exception as e:
                run_os_status = Status.FAIL

        except Exception as e:
            print(e)
            run_os_status = Status.FAIL


        self.save_run_single_os(wf_name, run_name, os_name, jobs, run_os_status)


    def _run_all_os(self, wf_name: str, run_name: str, os_list: List[str], jobs: List[Job], run_dry: bool = False):
        # run all
        for os_name in os_list:

            # create run_os_dir
            run_os_dir = self.get_wf_run_single_os_dir(wf_name, run_name, os_name)
            if not os.path.exists(run_os_dir):
                os.makedirs(run_os_dir)

            self._run_single_os(wf_name, run_name, os_name, jobs, run_dry)

        # save last_result
        any_failed = False
        for os_name in os_list:
            try:
                run_os_status = Status(open(self.get_wf_run_single_os_status_file(wf_name, run_name, os_name), "r").read())
            except:
                run_os_status = Status.FAIL

            if run_os_status == Status.FAIL:
                any_failed = True

        self.save_run_all_os(wf_name, run_name, Status.PASS if not any_failed else Status.FAIL)

    def get_wf_config(self, wf_name: str) -> WfRunConfig:
        return WfRunConfig.from_json(open(self.get_wf_config_file(wf_name), "r").read())

    def run(self, wf_name: str, run_dry: bool = False):
        c = self.get_wf_config(wf_name)

        run_name = str(get_timestamp())
        jobs = self._lode_job_tree_with_func(c.jobs)
        self._run_all_os(wf_name, run_name, c.os_list, jobs, False)

    def run_failed(self, wf_name: str, os_name:str, run_name: str):
        c = WfRunConfig.from_json(open(self.get_wf_run_single_os_result_file(wf_name, os_name, run_name), "r").read())
        jobs = self._lode_job_tree_with_func(c.jobs)
        self._run_all_os(wf_name, run_name, c.os_list, jobs, True)

    def save_run_single_os(self, wf_name: str, run_name: str, os_name: str, jobs: List[Job], status: Status):
        run_os_result_file = self.get_wf_run_single_os_result_file(wf_name, run_name, os_name)
        c = WfRunConfig([os_name], jobs)
        open(run_os_result_file, "w").write(json.dumps(c.to_dict()))

        run_os_status_file = self.get_wf_run_single_os_status_file(wf_name, run_name, os_name)
        open(run_os_status_file, "w").write(status.value)

    def save_run_all_os(self, wf_name: str, run_name: str, status: Status):
        run_status_file = self.get_wf_run_all_os_status_file(wf_name, run_name)
        open(run_status_file, "w").write(status.value)
