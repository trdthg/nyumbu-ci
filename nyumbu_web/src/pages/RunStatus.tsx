import {
    Button,
    Column,
    ContainedList, Grid,
    Heading,
    Layer,
    Section, Tile,
    VStack
} from '@carbon/react';
import { Renew } from '@carbon/icons-react';
import style from './workflow.module.scss';
import { useWorkflowRunAllResult } from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import RunExpanded from './RunExpanded';
import EnvironmentList from './Environment';

export default function Run() {
    const nav = useNavigate();
    const params = useParams<{ name: string; os: string; run: string }>();
    const runResult = useWorkflowRunAllResult(params.name!, params.run!);

    return (
        <VStack>
            <Tile className={[style.RunInfo].join(', ')}>
                <Heading style={{ fontWeight: 500 }}>Run Result</Heading>
            </Tile>
            <br />
            <Grid fullWidth className={style.Padding}>
                <Column sm={4} md={4} lg={5}>
                    <Layer level={0}>
                        <Tile className={style.Tile}>
                            <Section>
                                <ContainedList
                                    className={style.RunsList}
                                    label={
                                        <Heading className={style.RunsHeader}>
                                            Environments
                                        </Heading>
                                    }
                                    action={
                                        <Button
                                            hasIconOnly
                                            iconDescription="Refresh"
                                            renderIcon={Renew}
                                            tooltipPosition="left"
                                        />
                                    }
                                >
                                    <EnvironmentList />
                                </ContainedList>
                            </Section>
                        </Tile>
                    </Layer>
                </Column>
                {params.os && <RunExpanded />}
            </Grid>
        </VStack>
    );
}
