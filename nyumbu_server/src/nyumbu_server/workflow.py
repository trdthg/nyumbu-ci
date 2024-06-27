from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import datetime
import importlib
import inspect
import json
import multiprocessing
import os
from typing import List

from .config import WfRunConfig, WfRunJobConfig
from .job import Job, Status, count_jobs, update_jobs_status_by_map, walk_jobs
from .db import DB
from .util import fixup_job_path, get_timestamp
from .vm import VM
from .worker import Workder

class WorkflowRun:
    name: str
    run_name: str
    os_list: List[str]
    jobs: List[Job]

    fs: FS

    def __init__(self, fs: FS, wf_name: str, os_list: List[str], jobs: List[Job], dry_run: bool = False):
        self.fs = fs
        self.name = wf_name
        self.os_list = os_list
        self.jobs = jobs

        self.dry_run = dry_run

        formatted_now = datetime.datetime.now().strftime("run_%y_%m_%d_%H_%M_%S")
        print(f"运行工作流: {wf_name}, run: {formatted_now}")
        self.run_name = str(formatted_now)

    def prepare_run(self):
        # set initial status
        os.makedirs(self.fs.get_wf_runs_run_dir(self.name, self.run_name))
        self.save_run_all_os(Status.PENDING)

        for os_name in self.os_list:
            # create run_os_dir
            run_os_dir = self.fs.get_wf_run_single_os_dir(self.name, self.run_name, os_name)
            if not os.path.exists(run_os_dir):
                os.makedirs(run_os_dir)

            self.save_run_single_os(os_name, Status.PENDING)

        return self

    def _run_single_os(self, os_name: str):
        run_os_status = Status.RUNNING

        try:
            domain_xml_str = open(self.fs.get_single_os_domain_xml(os_name), "r").read()
            vm = VM(domain_xml_str)

            print("操作系统启动完了, 准备运行")
            vm.start()

            try:
                toml_config_path = self.fs.get_single_os_toml(os_name)

                print(f"共有 jobs {count_jobs(self.jobs)} 个")

                # FIXME
                w = Workder(self.name, toml_config_path, self.fs.get_wf_run_single_os_dir(self.name, self.run_name, os_name), vm, self.jobs)

                if not self.dry_run:
                    try:
                        print("开始运行")
                        w.run()
                        self.jobs = w.jobs

                        all_pass = True
                        def _check_fail(job: Job) -> bool:
                            nonlocal all_pass
                            if job.status != Status.PASS:
                                all_pass = False
                                return False
                        walk_jobs(self.jobs, _check_fail)

                        print("运行成功")
                        run_os_status = Status.from_bool(all_pass)
                    except Exception as e:
                        print("worker 发出 Exception", e)
                        run_os_status = Status.FAIL
                        pass

            except Exception as e:
                print("worker 启动失败", e)
                run_os_status = Status.FAIL

            print("停止虚拟机中")
            vm.stop()

        except Exception as e:
            print("操作系统启动异常", e)
            run_os_status = Status.FAIL

        print("保存测试状态", run_os_status.value)
        self.save_run_single_os(os_name, run_os_status)

    def run(self):
        self.save_run_all_os(Status.RUNNING)

        for os_name in self.os_list:
            self.save_run_single_os(os_name, Status.RUNNING)

            print(f"正在运行工作流: {self.name}, 操作系统: {os_name}")
            self._run_single_os(os_name)

        # save last_result
        any_failed = False
        for os_name in self.os_list:
            try:
                run_os_status = Status(open(self.fs.get_wf_run_single_os_status_file(self.name, self.run_name, os_name), "r").read())
            except:
                run_os_status = Status.FAIL

            if run_os_status == Status.FAIL:
                any_failed = True

        self.save_run_all_os(Status.PASS if not any_failed else Status.FAIL)

    def save_run_single_os(self, os_name: str, status: Status):
        run_os_result_file = self.fs.get_wf_run_single_os_result_file(self.name, self.run_name, os_name)
        c = WfRunConfig([os_name], [job.to_config() for job in self.jobs])

        print(f"共有 jobs {count_jobs(self.jobs)} 个")
        print(json.dumps(c.to_dict()))
        open(run_os_result_file, "w").write(json.dumps(c.to_dict()))

        run_os_status_file = self.fs.get_wf_run_single_os_status_file(self.name, self.run_name, os_name)
        open(run_os_status_file, "w").write(status.value)

    def save_run_all_os(self, status: Status):
        run_status_file = self.fs.get_wf_run_all_os_status_file(self.name, self.run_name)
        open(run_status_file, "w").write(status.value)

class FS:
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

    def get_wf_runs_run_dir(self, wf_name: str, run_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name)

    def get_wf_run_single_os_dir(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name)

    def get_wf_run_single_os_status_file(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name, "status")

    def get_wf_run_single_os_result_file(self, wf_name: str, run_name: str, os_name: str) -> str:
        return os.path.join(self._base_dir, self._wf_dir, wf_name, self._runs_dir, run_name, os_name, "config.result.json")

    def get_wf_run_single_os_job_dir(self, wf_name: str, run_name: str, os_name: str, job_path: str, no_base_url: bool = False) -> str:
        res = os.path.join(self._wf_dir, wf_name, self._runs_dir, run_name, os_name, fixup_job_path(job_path))
        if not no_base_url:
            res = os.path.join(self._base_dir, res)
        return res

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

    def _lode_job_tree_with_func(self, jobs_config: List[WfRunJobConfig]) -> List[Job]:
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

    def get_wf_config(self, wf_name: str) -> WfRunConfig:
        return WfRunConfig.from_json(open(self.get_wf_config_file(wf_name), "r").read())

class Manager:
    def __init__(self, fs: FS):
        self.fs = fs
        self.pool = ThreadPoolExecutor(max_workers=3)

    def spawn_run(self, wf_name: str, run_dry: bool = False):
        _c = self.fs.get_wf_config(wf_name)
        jobs = self.fs._lode_job_tree_with_func(_c.jobs)
        wf = WorkflowRun(self.fs, wf_name,  _c.os_list, jobs, dry_run=run_dry)
        wf.prepare_run()
        self.pool.submit(wf.run)

    # TODO: implement not complete
    # def spawn_run_failed(self, wf_name: str, os_name:str, run_name: str):
    #     c = WfRunConfig.from_json(open(self.fs.get_wf_run_single_os_result_file(wf_name, os_name, run_name), "r").read())
    #     jobs = self.fs._lode_job_tree_with_func(c.jobs)
    #     self.fs._run_all_os(wf_name, run_name, c.os_list, jobs, True)

