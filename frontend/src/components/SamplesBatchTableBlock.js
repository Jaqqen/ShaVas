// @flow 
import * as React from 'react';

import { Component } from 'react'
import SamplesTableBlock from './SamplesTableBlock';
import SamplesBlock from './SamplesBlock';

export default class SamplesBatchTableBlock extends Component {
    constructor(props) {
        super(props);
        this.state = {
            currentSamplesBatch: null,
            currentlySelectedBatchIndex: null,
            isGenerating: props.isGenerating,
            neuralNetworkHasBeenBuild: props.neuralNetworkHasBeenBuild,
        };

        this.setCurrentSamplesBatch = this.setCurrentSamplesBatch.bind(this);
        this.renderingSamplesTableBlock = this.renderingSamplesTableBlock.bind(this);
        this.renderSamplesBatches = this.renderSamplesBatches.bind(this);
    }

    renderingSamplesTableBlock() {
        const { shapeNumber, isGenerating, neuralNetworkHasBeenBuild, samplesList } = this.props;
        // const { currentSamplesBatch, currentlySelectedBatchIndex } = this.state;

        if (isGenerating || neuralNetworkHasBeenBuild) {
            return <div className="samples-tables-block-holder">
                        <h3>{shapeNumber+1}. Canvas Samples</h3>
                        <div className="samples-tables-block-content-holder">
                            {
                                samplesList !== undefined && samplesList !== null ?
                                <React.Fragment>
                                    <SamplesTableBlock
                                        samplesList={samplesList}
                                        setCurrentSamplesBatch={this.setCurrentSamplesBatch}
                                    />
                                    {this.renderSamplesBatches(samplesList, shapeNumber)}
                                </React.Fragment>
                                :
                                <p className="default-samples-batch-text">Please wait for Batches to load.</p>
                            }
                        </div>
                    </div>;
        } else {
            return null;
        }
    }

    renderSamplesBatches(samplesList, shapeNumber) {
        const { currentlySelectedBatchIndex } = this.state;

        return samplesList.map((samplesBatch, index) => {
            if (index === currentlySelectedBatchIndex && currentlySelectedBatchIndex !== null) {
                return <SamplesBlock
                    key={index}
                    currentSamplesBatch={samplesBatch}
                    currentlySelectedBatchIndex={currentlySelectedBatchIndex}
                    shapeNumber={shapeNumber}
                />
            }
            return null;
        });
    }

    setCurrentSamplesBatch(index, samplesBatch) {
        this.setState({ 
            currentlySelectedBatchIndex: index,
            currentSamplesBatch: samplesBatch,
        });
    }

    render() {
        return (
            <React.Fragment>
                {this.renderingSamplesTableBlock()}
            </React.Fragment>
        )
    }
}