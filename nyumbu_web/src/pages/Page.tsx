import {
    Grid,
    Column,
    Button,
    Layer,
    ContainedList,
    ContainedListItem,
    Heading,
    Tile,
    VStack,
} from '@carbon/react';
import { Renew, Edit, Checkmark } from '@carbon/icons-react';
import { Spinner } from '@primer/react';
import { useWorkflowList } from '../api';
import style from './workflow.module.scss';
import EnvironmentList from './Environment';
import Run from './RunStatus';
import WorkflowList from './WorkflowList';
import { useParams } from 'react-router-dom';
import RunsList from './Runs';
import { useState } from 'react';

export default function WorkflowListPage() {
    const workflows = useWorkflowList();
    const params = useParams<{ name: string; os: string; run: string }>();

    const [editingRuns, setEditingRuns] = useState(false);

    return (
        <Grid condensed fullWidth style={{ padding: 0 }}>
            <Column sm={4} md={4} lg={2} className={style.WorkflowColumn}>
                <Layer>
                    <ContainedList
                        label="Workflows"
                        className={style.Column}
                        action={
                            <Button
                                hasIconOnly
                                iconDescription="Refresh"
                                renderIcon={Renew}
                                tooltipPosition="left"
                                onClick={() => {
                                    workflows.reload();
                                }}
                            />
                        }
                    >
                        {workflows.loading ? (
                            <ContainedListItem>
                                <Spinner />
                            </ContainedListItem>
                        ) : workflows.err ? (
                            <ContainedListItem>Error</ContainedListItem>
                        ) : workflows.data ? (
                            <WorkflowList />
                        ) : (
                            'None'
                        )}
                    </ContainedList>
                </Layer>
            </Column>
            <Column sm={4} md={4} lg={4} className={style.RunsColumn}>
                <Layer>
                    <ContainedList
                        label="Runs"
                        className={style.Column}
                        action={
                            <Button
                                hasIconOnly
                                iconDescription="Edit List"
                                renderIcon={editingRuns ? Checkmark : Edit}
                                tooltipPosition="left"
                                kind={editingRuns ? "primary" : "secondary"}
                                onClick={() => setEditingRuns(!editingRuns)}
                            />
                        }
                    >
                        {params.name && <RunsList editing={editingRuns} />}
                    </ContainedList>
                </Layer>
            </Column>
            <Column sm={4} md={8} lg={10} className={style.ExpandedColumn}>
                <Layer>
                    <VStack>
                        {params.run ? (
                            <Run />
                        ) : (
                            <Heading className={style.SelectRunPlaceholder}>
                                Select a run to view details
                            </Heading>
                        )}
                    </VStack>
                </Layer>
            </Column>
        </Grid>
    );
}
