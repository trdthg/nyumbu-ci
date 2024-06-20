
from enum import Enum
import json
from typing import List

class Status(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    CANCEL = "cancel"

    @staticmethod
    def from_bool(v: bool) -> 'Status':
        if v:
            return Status.PASS
        else:
            return Status.FAIL

class WfRunJobConfig:
    path: str
    status: Status
    children: List['WfRunJobConfig']

    def __init__(self, path: str, children: list['WfRunJobConfig'] = [], status = Status.PENDING):
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
        return WfRunJobConfig(path, children, config_dict.get("status", Status.PENDING))

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