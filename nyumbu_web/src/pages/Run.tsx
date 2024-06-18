import { Column, Grid, Heading, Layer, Section, Tile, VStack } from "@carbon/react";
import style from "./workflow.module.scss";
import { useWorkflowRunSingleOSResultConfig, useWorkflowRuns } from '../api';
import { useParams } from "react-router-dom";

export default function Run() {
    const params = useParams<{ name: string, os: string, run: string }>();
    const runs = useWorkflowRuns(params.name!);
    const run = useWorkflowRunSingleOSResultConfig(params.name!, params.os!, params.run!);

    return (
        <VStack>
            <Tile className={style.RunInfo}>
                <Heading>Run Result</Heading>
            </Tile>
            <br />
            <Grid fullWidth className={style.Padding}>
                <Column sm={4} md={8} lg={4}>
                    <Layer>
                        <Tile>
                            <Section>
                                <Heading>Runs</Heading>
                                <pre>{JSON.stringify(runs.data?.list)}</pre>
                            </Section>
                        </Tile>
                    </Layer>
                </Column>
                <Column sm={4} md={4} lg={4}>
                    <Layer>
                        <Tile>
                            <Section>
                                <Heading>Run Info</Heading>
                                <pre>{JSON.stringify(run.data, null, 2)}</pre>
                            </Section>
                        </Tile>
                    </Layer>
                </Column>
            </Grid>
        </VStack>
    );
}