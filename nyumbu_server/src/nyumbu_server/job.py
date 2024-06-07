
from enum import Enum
import json
from typing import Callable, List
import pyautotest


class Status(Enum):
    EMPTY = "empty"
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class Job:
    name: str
    fn: Callable[[pyautotest.Driver], bool]
    status: Status
    skip: bool
    children: List["Job"]

    def serialize_dict(self) -> str:
        return {"name": self.name, "status": self.status.value, "children": []}

    def serialize_str(self) -> str:
        return json.dumps(self.serialize_dict())

    def __init__(self, name, case_fn, children=[], skip=False):
        self.name = name
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
        if results.get(job.name) is not None:
            status = Status(results.get(job.name))
            if status != Status.PASS:
                return False
            job.status = status
            return True

    work_jobs(jobs, _set_status)
