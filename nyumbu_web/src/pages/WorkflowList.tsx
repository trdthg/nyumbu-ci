import { Button, ContainedListItem } from '@carbon/react';
import { useNavigate, useParams } from 'react-router-dom';
import { baseUrl, useWorkflowList } from '../api';
import { Play } from '@carbon/icons-react';
import style from './workflow.module.scss';

export default function WorkflowList() {
    const nav = useNavigate();
    const workflows = useWorkflowList();
    const params = useParams<{ name: string }>();

    const run = (workflow: string) => {
        fetch(`${baseUrl}/workflows/${workflow}/run`);
    };

    return (
        <>
            {(workflows.data?.list ?? []).map((wf, i) => (
                <ContainedListItem
                    key={i}
                    onClick={() => {
                        nav(`/workflow/${wf}`);
                    }}
                    action={
                        <Button
                            iconDescription="Run"
                            renderIcon={Play}
                            kind="tertiary"
                            tooltipPosition="left"
                            hasIconOnly
                            onClick={(e) => {
                                e.stopPropagation();
                                run(wf);
                            }}
                        />
                    }
                    className={params.name === wf ? style.Active : ''}
                >
                    {wf}
                </ContainedListItem>
            ))}
        </>
    );
}
