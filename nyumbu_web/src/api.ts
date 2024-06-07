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

export interface WorkflowList {
  list: string[];
}

export interface WorkflowJob {
  name: string;
  status: string;
  children: WorkflowJob[];
}

export interface WorkflowInfo {
  name: string;
  os_list: string[];
  runs: string[];
}

export interface RunWorkflowResponse {
  // 运行工作流的响应结构
}

export interface WorkflowStatus {
  // 工作流状态的响应结构
}

export class WorkflowAPI {
  static baseUrl: string;

  static getAll(): FetchResult<WorkflowList> {
    return useFetch(`${this.baseUrl}/workflows`, {});
  }

  static getInfo(name: string): FetchResult<WorkflowInfo> {
    return useFetch(`${this.baseUrl}/workflows/${name}/info`);
  }

  static run(
    name: string,
    runOnlyFailed: boolean = false,
  ): FetchResult<RunWorkflowResponse> {
    return useFetch(
      `${this.baseUrl}/workflows/${name}/run?runonlyfailed=${runOnlyFailed}`,
    );
  }

  static getWorkflowStatus(workflowName: string): FetchResult<WorkflowStatus> {
    return useFetch(`${this.baseUrl}/workflows/${workflowName}/jobs`);
  }
}

WorkflowAPI.baseUrl = "http://localhost:5000";

export default WorkflowAPI;
