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
  externalReloadKey: number = 0,
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
  }, [reloadKey, externalReloadKey]);

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

export const useWorkflowList = (): FetchResult<WorkflowList> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows`);
    setReloadKey(reloadKey + 1);
  }, []);
  return useFetch(url, undefined, reloadKey);
};

export const useWorkflowConfig = (wf_name: string): FetchResult<WorkflowConfig> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}`);
    setReloadKey(reloadKey + 1);
  }, [wf_name]);
  return useFetch(url, undefined, reloadKey);
};

export const useWorkflowRuns = (wf_name: string): FetchResult<WorkflowRunList> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}/runs`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}/runs`);
    setReloadKey(reloadKey + 1);
  }, [wf_name]);
  return useFetch(url, undefined, reloadKey);
};

export const useWorkflowRunAllResult = (wf_name: string, run_name: string): FetchResult<RunSingleOSResult> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}/runs/${run_name}`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}/runs/${run_name}`);
    setReloadKey(reloadKey + 1);
  }, [wf_name, run_name]);
  return useFetch(url, undefined, reloadKey);
};

export const useWorkflowRunSingleOSResultConfig = (wf_name: string, run_name: string, os_name: string): FetchResult<RunSingleOSResultConfig> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}`);
    setReloadKey(reloadKey + 1);
  }, [wf_name, run_name, os_name]);
  return useFetch(url, undefined, reloadKey);
};

export const useWorkflowRunSingleOSLogs = (wf_name: string, run_name: string, os_name: string, path: string): FetchResult<RunSingleOSResultInfo> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}/${path}`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}/runs/${run_name}/${os_name}/${path}`);
    setReloadKey(reloadKey + 1);
  }, [wf_name, run_name, os_name, path]);
  return useFetch(url, undefined, reloadKey);
};

export const useRun = (wf_name: string): FetchResult<void> => {
  const [url, setUrl] = useState(`${baseUrl}/workflows/${wf_name}/run`);
  const [reloadKey, setReloadKey] = useState(0);
  useEffect(() => {
    setUrl(`${baseUrl}/workflows/${wf_name}/run`);
    setReloadKey(reloadKey + 1);
  }, [wf_name]);
  return useFetch(url, undefined, reloadKey);
};

const baseUrl = "http://localhost:5000";
