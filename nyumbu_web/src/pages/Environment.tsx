import { ContainedListItem } from '@carbon/react';
import { useWorkflowConfig } from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import style from './workflow.module.scss';

export default function EnvironmentList() {
    const params = useParams<{ name: string; os: string }>();
    const nav = useNavigate();
    const config = useWorkflowConfig(params.name!);

    return (
        <>
            {(config?.data?.os_list ?? []).map((os, i) => (
                <ContainedListItem
                    key={i}
                    onClick={() => {
                        nav(`/workflow/${params.name}/${os}`);
                    }}
                    className={params.os === os ? style.Active : ''}
                >
                    {os}
                </ContainedListItem>
            ))}
        </>
    );
}
