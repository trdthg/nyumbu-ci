
from enum import Enum
import json
from typing import Callable, List
import pyautotest


class Status(Enum):
    EMPTY = "empty"
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class Job:
    path: str
    fn: Callable[[pyautotest.Driver], bool]
    status: Status
    skip: bool
    children: List["Job"]

    def to_dict(self) -> str:
        res = {"path": self.path, "status": self.status.value, "children": []}
        return res
    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __init__(self, path, case_fn, children=[], skip=False):
        self.path = path
        self.fn = case_fn
        self.children = children
        self.status = Status.EMPTY
        self.skip = skip


def work_jobs(jobs: List[Job], f: Callable[[Job], bool]):
    for job in jobs:
        if f(job):
            work_jobs(job.children, f)


def update_jobs_status(jobs: List[Job], results: dict[str, Status]):

    def _set_status(job: Job):
        if results.get(job.path) is not None:
            status = Status(results.get(job.path))
            if status != Status.PASS:
                return False
            job.status = status
            return True

    work_jobs(jobs, _set_status)
