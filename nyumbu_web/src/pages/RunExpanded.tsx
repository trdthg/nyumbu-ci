import {
    Column,
    Layer,
    Section,
    Heading, Tile,
    CodeSnippet, Accordion,
    AccordionItem
} from '@carbon/react';
import { ThumbsUp, ThumbsDown, Fade } from '@carbon/icons-react';
// @ts-ignore
import TreeView from '@carbon/react/lib/components/TreeView/TreeView';
// @ts-ignore
import TreeNode from '@carbon/react/lib/components/TreeView/TreeNode';
import {
    useWorkflowRunSingleOSLogs,
    useWorkflowRunSingleOSResultConfig,
} from '../api';
import { useParams } from 'react-router-dom';
import style from './workflow.module.scss';
import { useState } from 'react';
import StaticResources from './StaticResources';

function RunLog(props: {
    workflow: string;
    os: string;
    run: string;
    path: string;
}) {
    const log = useWorkflowRunSingleOSLogs(
        props.workflow,
        props.run,
        props.os,
        props.path,
    );

    return (
        <Accordion size="lg">
            <AccordionItem title={'Commands'} className={style.FullWidth}>
                <Layer level={1}>
                    <CodeSnippet type="multi">
                        {log.data?.pyscript ?? 'No commands'}
                    </CodeSnippet>
                </Layer>
            </AccordionItem>
            {(log.data?.logs ?? []).map((log, i) => (
                <AccordionItem
                    key={i}
                    title={log.name}
                    className={style.FullWidth}
                >
                    <Layer level={1}>
                        <CodeSnippet type="multi">
                            <StaticResources url={log.path} />
                        </CodeSnippet>
                    </Layer>
                </AccordionItem>
            ))}
        </Accordion>
    );
}

export default function RunExpanded() {
    const params = useParams<{ name: string; os: string; run: string }>();
    const run = useWorkflowRunSingleOSResultConfig(
        params.name!,
        params.run!,
        params.os!,
    );

    const [selectPath, setSelectPath] = useState<string>();

    return (
        <>
            <Column sm={4} md={4} lg={5}>
                <Layer>
                    <Tile className={style.Tile}>
                        <Section>
                            <Heading className={style.TileHeader}>Jobs</Heading>
                            <TreeView label="">
                                {(run.data?.jobs ?? []).map((job, i) => (
                                    <TreeNode
                                        key={i}
                                        label={job.path ?? 'untitled job'}
                                        renderIcon={statusIcon(job.status)}
                                        onClick={() => setSelectPath(job.path!)}
                                    />
                                ))}
                            </TreeView>
                        </Section>
                    </Tile>
                </Layer>
            </Column>
            {selectPath && (
                <Column sm={4} md={8} lg={10}>
                    <Layer>
                        <Tile className={style.Tile}>
                            <Section>
                                <Heading className={style.TileHeader}>
                                    Logs
                                </Heading>
                                {
                                    <RunLog
                                        workflow={params.name!}
                                        os={params.os!}
                                        run={params.run!}
                                        path={selectPath}
                                    />
                                }
                            </Section>
                        </Tile>
                    </Layer>
                </Column>
            )}
        </>
    );
}

function SuccessIcon() {
    return <ThumbsUp fill="green" style={{marginRight: "0.75rem"}} />;
}

function FailureIcon() {
    return <ThumbsDown fill="red" style={{ marginRight: '0.75rem' }} />;
}

function PendingIcon() {
    return <Fade fill="blue" style={{ marginRight: '0.75rem' }} />;
}

const statusIcon = (result: string): React.ComponentType<{}> => {
    switch (result) {
        case 'pass':
            return SuccessIcon;
        case 'fail':
            return FailureIcon;
        default:
            return PendingIcon;
    }
};