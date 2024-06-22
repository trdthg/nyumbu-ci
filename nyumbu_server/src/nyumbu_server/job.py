
from enum import Enum
import json
from typing import Callable, List
import pyautotest

from .config import WfRunConfig, WfRunJobConfig, Status

class Job:
    path: str
    fn: Callable[[pyautotest.Driver], bool]
    status: Status
    skip: bool
    children: List["Job"]

    def to_dict(self) -> str:
        res = {"path": self.path, "status": self.status.value, "children": []}
        return res

    def to_config(self) -> WfRunJobConfig:
        return WfRunJobConfig(self.path, [child.to_config() for child in self.children], self.status)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __init__(self, path, case_fn, children=[], skip=False):
        self.path = path
        self.fn = case_fn
        self.children = children
        self.status = Status.PENDING
        self.skip = skip


def walk_jobs(jobs: List[Job], f: Callable[[Job], bool]):
    for job in jobs:
        if f(job):
            walk_jobs(job.children, f)

def count_jobs(jobs: List[Job]) -> int:
    count = 0
    def _count_jobs(job: Job) -> bool:
        nonlocal count
        count += 1
        return True
    walk_jobs(jobs, _count_jobs)
    return count

def update_jobs_status(jobs: List[Job], status: Status):
    def _set_status(job: Job):
        job.status = status
        return True

    walk_jobs(jobs, _set_status)

def update_jobs_status_by_map(jobs: List[Job], results: dict[str, Status]):
    def _set_status(job: Job):
        if results.get(job.path) is not None:
            status = Status(results.get(job.path))
            if status != Status.PASS:
                return False
            job.status = status
            return True

    walk_jobs(jobs, _set_status)
