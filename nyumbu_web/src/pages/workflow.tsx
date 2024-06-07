import { Box, Button, Spinner } from "@primer/react";
import { Link, useNavigate } from "react-router-dom";
import { WorkflowAPI, WorkflowList } from "../api";

import styles from "./workflow.module.css";

function WorkFlowList(props: { data: WorkflowList }) {
  return (
    <Box className={"workflow-list"}>
      {props.data.list.map((wf, i) => (
        <div
          key={i}
          className={styles.workflow}
          onClick={() => {
            useNavigate()(`/workflow/${wf}`);
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
  let workflows = WorkflowAPI.getAll();

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
