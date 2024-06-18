import { useCallback, useEffect, useState } from "react";

export interface FetchResult<T> {
  data: T | null;
  loading: boolean;
  err: any;
  reload: () => void;
}

export const useFetch = <T>(
  url: string,
  options?: RequestInit,
): FetchResult<T> => {
  const [data, setData] = useState<T | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<any>(null);
  const [reloadKey, setReloadKey] = useState(0);

  const reload = useCallback(
    () => setReloadKey((reloadKey) => reloadKey + 1),
    [],
  );

  useEffect(() => {
    console.log(reloadKey);
    setIsLoading(true);
    const fetchData = async () => {
      try {
        const res = await fetch(url, options);
        if (res.ok) {
          const json: T = await res.json();
          setData(json);
        } else {
          throw new Error(res.statusText);
        }
      } catch (error) {
        setError(error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [reloadKey]);

  return { data, loading: isLoading, err: error, reload };
};


// 1
export interface WorkflowList {
  list: string[];
}

// 2
export interface WorkflowJob {
  name: string;
  status: string;
  children: WorkflowJob[];
}

export interface WorkflowConfig {
  name: string;
  os_list: string[];
  jobs: WorkflowJob[];
}

// 3

export interface RunResult {
  status: string
  run_name: string
}
export interface WorkflowRunList {
  list: RunResult[]
}

// 4
export interface RunSingleOSResult {
  os: string
  status: string
}
export interface RunResultInfo {
  list: RunSingleOSResult[]
}

// 5
export type RunSingleOSResultConfig = WorkflowConfig

// 6

export interface FileTree {
  type: "dit" | "file"
  path: string
  children: FileTree[]
}
export interface RunSingleOSResultInfo {
  pyscript: string,
  logs: FileTree[]
}


export class WorkflowAPI {
  static baseUrl: string;

  static getWorkflowList(): FetchResult<WorkflowList> {
    return useFetch(`${this.baseUrl}/workflows`, {});
  }

  static getWorkflowConfig(wf_name: string): FetchResult<WorkflowConfig> {
    return useFetch(`${this.baseUrl}/workflows/${wf_name}`);
  }

  static getWorkflowRuns(wf_name: string): FetchResult<WorkflowRunList> {
    return useFetch(`${this.baseUrl}/workflows/${wf_name}/runs`);
  }

  static getWorkflowRunAllResult(wf_name: string, run_name: string): FetchResult<RunSingleOSResult> {
    return useFetch(`${this.baseUrl}/workflows/${wf_name}/runs/${run_name}`);
  }

  static getWorkflowRunSingleOSResultConfig(wf_name: string, run_name: string, os_name: string): FetchResult<RunSingleOSResultConfig> {
    return useFetch(`${this.baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}`);
  }

  static getWorkflowRunSingleOSLogs(wf_name: string, run_name: string, os_name: string, path: string): FetchResult<RunSingleOSResultInfo> {
    return useFetch(`${this.baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}/${path}`);
  }

  static run(wf_name: string): FetchResult<void> {
    return useFetch(
      `${this.baseUrl}/workflows/${wf_name}/run`,
    );
  }
}

WorkflowAPI.baseUrl = "http://localhost:5000";

export default WorkflowAPI;
