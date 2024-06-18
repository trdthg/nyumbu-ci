import {
    Grid,
    Column,
    Button,
    Layer, ContainedList,
    ContainedListItem,
    Heading,
    Tile
} from '@carbon/react';
import { Spinner } from '@primer/react';
import { useWorkflowList } from '../api';
import style from './workflow.module.scss';
import EnvironmentList from './Environment';
import Run from './Run';
import WorkflowList from './WorkflowList';


export default function WorkflowListPage() {
    const workflows = useWorkflowList();

    return (
        <Grid condensed fullWidth style={{ padding: 0 }}>
            <Column sm={4} md={4} lg={4} className={style.WorkflowColumn}>
                <Layer>
                    <ContainedList
                        label="Workflows"
                        className={style.Column}
                        action={
                            <Button
                                onClick={() => {
                                    workflows.reload();
                                }}
                            >
                                Refresh
                            </Button>
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
            <Column sm={4} md={4} lg={4} className={style.EnvironmentColumn}>
                <Layer>
                    <ContainedList
                        label="Environments"
                        className={style.Column}
                    >
                        <EnvironmentList />
                    </ContainedList>
                </Layer>
            </Column>
            <Column sm={4} md={8} lg={8}>
                <Layer>
                    <Run />
                </Layer>
            </Column>
        </Grid>
    );
}
