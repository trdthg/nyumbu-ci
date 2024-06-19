import { ContainedListItem } from '@carbon/react';
import {
    useWorkflowConfig,
    useWorkflowRunAllResult,
    useWorkflowRunSingleOSResultConfig,
} from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import style from './workflow.module.scss';
import { statusIcon } from './Runs';
import { useCallback, useEffect } from 'react';

export default function EnvironmentList() {
    const params = useParams<{ name: string; run: string; os: string }>();
    const nav = useNavigate();
    const config = useWorkflowRunAllResult(params.name!, params.run!);

    const navigateToOSRun = useCallback(
        (os: string) => {
            nav(`/workflow/${params.name}/${params.run}/${os}`);
        },
        [nav, params.name, params.run],
    );

    useEffect(() => {
        if (params.os === undefined && (config.data?.list ?? []).length > 0) {
            nav(
                `/workflow/${params.name}/${params.run}/${
                    config.data!.list[0].os
                }`,
            );
        }
    }, [config.data, nav, params.name, params.os]);

    return (
        <>
            {(config?.data?.list ?? []).map((os, i) => (
                <ContainedListItem
                    key={i}
                    onClick={() => navigateToOSRun(os.os)}
                    className={params.os === os.os ? style.Active : ''}
                    renderIcon={statusIcon(os.status)}
                >
                    {os.os}
                </ContainedListItem>
            ))}
        </>
    );
}
