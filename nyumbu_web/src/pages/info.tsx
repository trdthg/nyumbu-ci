import { Box, Button } from "@primer/react";
import WorkflowAPI from "../api";
import { useParams } from "react-router-dom";

export default function WorkflowInfoPage(props: {}) {
  const params = useParams<{ name: string }>();

  const wf = WorkflowAPI.getWorkflowConfig(params.name || "");

  return (
    <Box
      style={{
        margin: "auto",
        width: "80%",
      }}
    >
      <Button onClick={() => { }}>{wf.data?.name || "none"}</Button>
    </Box>
  );
}
