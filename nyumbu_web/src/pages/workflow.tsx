import { Box, Button, Spinner } from "@primer/react";
import { Link, Outlet, useNavigate } from "react-router-dom";
import { WorkflowAPI, WorkflowList } from "../api";

import styles from "./workflow.module.css";

function WorkFlowList(props: { data: WorkflowList }) {
  const nav = useNavigate()

  return (
    <Box className={styles["workflow-list"]}>
      {props.data.list.map((wf, i) => (
        <div
          key={i}
          className={styles.workflow}
          onClick={() => {
            console.log("clicked", wf);
            nav(`/workflow/${wf}`);
          }}
        >
          <div>
            {/* <Link to={""}>{wf}</Link> */}
          </div>
          <div>text</div>
        </div>
      ))}
    </Box>
  );
}

export default function WorkflowListPage(props: {}) {
  let workflows = WorkflowAPI.getWorkflowList();

  return (
    <Box
      style={{
        margin: "auto",
        width: "80%",
      }}
    >
      <Button
        onClick={() => {
          workflows.reload();
        }}
      >
        Refresh
      </Button>

      <div style={{}}>
        {workflows.loading ? (
          <Spinner />
        ) : workflows.err ? (
          <p>Error</p>
        ) : workflows.data ? (
          <WorkFlowList data={workflows.data} />
        ) : (
          "None"
        )}
      </div>
    </Box>
  );
}
