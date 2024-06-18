import { ContainedListItem } from '@carbon/react';
import { useNavigate, useParams } from 'react-router-dom';
import { useWorkflowList } from '../api';
import style from './workflow.module.scss';
import { useEffect } from 'react';

export default function WorkflowList() {
    const nav = useNavigate();
    const workflows = useWorkflowList();
    const params = useParams<{ name: string }>();

    return (
        <>
            {(workflows.data?.list ?? []).map((wf, i) => (
                <ContainedListItem
                    key={i}
                    onClick={() => {
                        nav(`/workflow/${wf}`);
                    }}
                    className={params.name === wf ? style.Active : ''}
                >
                    {wf}
                </ContainedListItem>
            ))}
        </>
    );
}
