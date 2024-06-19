import { Button, ContainedListItem } from '@carbon/react';
import { useNavigate, useParams } from 'react-router-dom';
import { useWorkflowRuns, RunResult, baseUrl } from '../api';
import {
    CheckmarkOutline,
    ErrorOutline,
    Pending,
    TrashCan,
} from '@carbon/icons-react';
import style from './workflow.module.scss';
import { useEffect, useRef } from 'react';

function SuccessIcon() {
    return <CheckmarkOutline fill="green" />;
}

function FailureIcon() {
    return <ErrorOutline fill="red" />;
}

function PendingIcon() {
    return <Pending fill="gray" />;
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

    const removeRunEntry = (workflow: string, run: string) => {
        fetch(`${baseUrl}/workflows/${workflow}/runs/${run}`, {
            method: 'DELETE',
        });
    };

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
                    action={
                        <Button
                            hasIconOnly
                            iconDescription="Remove"
                            kind="danger"
                            renderIcon={TrashCan}
                            tooltipPosition="left"
                            onClick={() =>
                                removeRunEntry(params.name!, wf.run_name)
                            }
                        />
                    }
                >
                    {wf.run_name}
                </ContainedListItem>
            ))}
        </>
    );
}
