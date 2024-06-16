import { ThemeProvider, BaseStyles } from "@primer/react";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import WorkflowListPage from "./pages/workflow.tsx";
import WorkflowInfoPage from "./pages/info.tsx";

function Header(_props: {}) {
  return (
    <div
      style={{
        backgroundColor: "#f6f8fa",
        padding: "16px 16px 8px",
      }}
    >
      <div
        style={{
          paddingBottom: "4rem",
        }}
      >
        placeholder
      </div>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <WorkflowListPage />,
    children: [
      {
        path: "/workflow/:name",
        element: <WorkflowInfoPage />,
      },
    ],
  },
]);

function App() {
  return (
    <ThemeProvider>
      <BaseStyles>
        <Header></Header>

        <RouterProvider router={router} />
      </BaseStyles>
    </ThemeProvider>
  );
}

export default App;
