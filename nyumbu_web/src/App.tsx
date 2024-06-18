import { GlobalTheme } from '@carbon/react';
import { RouterProvider, createHashRouter } from 'react-router-dom';
import './global.scss';
import WorkflowListPage from './pages/Page.tsx';

const router = createHashRouter([
    {
        path: '/workflow',
        element: <WorkflowListPage />,
        children: [
            {
                path: '/workflow/:name',
                children: [
                    {
                        path: '/workflow/:name/:os',
                        children: [
                            {
                                path: '/workflow/:name/:os/:run',
                            },
                        ],
                    },
                ],
            },
        ],
    },
]);

function App() {
    return (
        <GlobalTheme>
            <RouterProvider router={router} />
        </GlobalTheme>
    );
}

export default App;
