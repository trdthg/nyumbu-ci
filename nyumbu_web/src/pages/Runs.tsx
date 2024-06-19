import { ContainedListItem } from '@carbon/react';
import { useNavigate, useParams } from 'react-router-dom';
import { useWorkflowRuns, RunResult } from '../api';
import { ThumbsUp, ThumbsDown, Fade } from '@carbon/icons-react';
import style from './workflow.module.scss';

function SuccessIcon() {
    return <ThumbsUp fill="green" />;
}

function FailureIcon() {
    return <ThumbsDown fill="red" />;
}

function PendingIcon() {
    return <Fade fill="blue" />;
}

export const statusIcon = (result: string): React.ComponentType<{}> => {
    switch (result) {
        case 'pass':
            return SuccessIcon;
        case 'fail':
            return FailureIcon;
        default:
            return PendingIcon;
    }
};

export default function RunsList() {
    const nav = useNavigate();
    const params = useParams<{ name: string; run: string }>();
    const workflows = useWorkflowRuns(params.name!);

    return (
        <>
            {(workflows.data?.list ?? []).map((wf, i) => (
                <ContainedListItem
                    key={i}
                    onClick={() => {
                        nav(`/workflow/${params.name}/${wf.run_name}`);
                    }}
                    className={params.run === wf.run_name ? style.Active : ''}
                    renderIcon={statusIcon(wf.status)}
                >
                    {wf.run_name}
                </ContainedListItem>
            ))}
        </>
    );
}
