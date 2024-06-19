
import copy
import os
import time
from typing import List

import tomlkit
from .job import Job, Status, walk_jobs
from .vm import VM
from .util import fixup_job_path

import pyautotest

class Workder:

    def __init__(self, wf_name: str, toml_config_path: str, run_os_dir: str, vm: VM, jobs: List[Job]):
        self.wf_name = wf_name
        self.vm = vm
        self.jobs = jobs

        name_map = {}

        print("worker init 1")

        config_toml_str = open(toml_config_path, "r").read()
        self.config_toml = tomlkit.loads(config_toml_str)
        self.run_os_dir = run_os_dir

        print("worker init")

        def check_name_duplicate(job: Job):
            if name_map.get(job.path) != None:
                raise Exception("duplicate job name: " + job.path)
            else:
                name_map[job.path] = ""
            return True

        walk_jobs(jobs, check_name_duplicate)

        self.jobs = jobs

    # 打印
    def print_job_result_tree(self):
        indent = 0
        res = ""

        def _print_job(job: Job, indent: int):
            res = ""
            job_name = job.fn.__name__
            job_status = job.status.value
            res += f'{" " * indent}- {job_name}: {job_status}\n'
            for child in job.children:
                res += _print_job(child, indent + 2)
            return res

        for job in self.jobs:
            res += _print_job(job, indent)

        return res
    def run(self, base_snapname: str = "init"):
        # 创建初始快照
        self.vm.save_snapshot(base_snapname)
        self._run(base_snapname, self.jobs, [])

    # 运行
    def _run_(self, base_snapname: str, jobs: List[Job], _indexs: List[int]):

        pass

    def _run(self, base_snapname: str, jobs: List[Job], _indexs: List[int]):
        for i, job in enumerate(jobs):
            indexs = copy.deepcopy(_indexs)
            indexs.append(i + 1)
            indexs_str = ".".join(map(lambda x: str(x), indexs))

            next_snapname = job.path
            print(f"running case {indexs_str}: {job.path}({job.fn.__name__})")

            if job.skip:
                job.status = Status.SKIP
                print("hand_skip")
                continue

            try:
                # 如果之前运行过没有通过, 或者无镜像保留, 就运行跳过
                if (
                    job.status != Status.PASS
                    or self.vm.get_snapshot_by_name(next_snapname) == None
                ):
                    # 每个 job 运行前跳转到初始快照
                    self.vm.jump_to_snapshort(base_snapname)


                    # FIXME: log_dir 不同快照如何分离日志
                    # FIXME: worker_run 是否只该负责一次脚本运行
                    print(f"当前处理job {job.path}")
                    self.config_toml.add("log_dir", os.path.join(self.run_os_dir, fixup_job_path(job.path)))

                    print(f"启动 driver")
                    d = pyautotest.Driver(tomlkit.dumps(self.config_toml))
                    print(f"运行测试脚本")

                    run_result = False
                    try:
                        job.fn(d)
                        run_result = True
                        print("运行成功")
                    except Exception as e:
                        run_result = False
                        print("运行失败", e)
                        pass
                    print(f"停止 driver")
                    d.stop()

                    self.config_toml.remove("log_dir")

                    job.status = Status.from_bool(run_result)

                    # 测试通过快照
                    print(f"保存快照")
                    self.vm.save_snapshot(next_snapname)

                    if run_result:
                        print("任务运行成功, 搜索子任务")
                        try:
                            self._run(next_snapname, job.children, indexs)
                            print("子任务云运行成功")
                        except Exception as e:
                            print("子任务运行抛出异常", e)
                            pass

                else:
                    print("pass(skip)")

            except Exception as e:
                job.status = Status.FAIL
                print("任务运行失败", e)
                # 测试失败快照
                print(f'保存快照到 {next_snapname + "-failed"}')
                self.vm.save_snapshot(next_snapname + "-failed")
                continue

    # 打印
    def __str__(self):
        indent = 0
        res = ""

        def _print_job(job: Job, indent: int):
            res = ""
            job_name = job.path
            job_status = job.status.value
            res += f'{" " * indent}- {job_name}: {job_status}\n'
            res += f'{" " * indent}  - fn: {job.fn.__name__}\n'
            res += f'{" " * indent}  - status: {job_status}\n'
            res += f'{" " * indent}  - children: \n'
            for child in job.children:
                res += _print_job(child, indent + 4)
            return res

        for job in self.jobs:
            res += _print_job(job, indent)

        return res
