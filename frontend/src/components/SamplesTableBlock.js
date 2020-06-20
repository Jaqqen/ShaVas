import React, { Component } from 'react'
import BatchListEntry from './BatchListEntry';
import { sampleList } from '../shared/constants/IDGlobal';



export default class SamplesTableBlock extends Component {
    constructor(props) {
        super(props);
        this.state = {
            currentlySelectedBatchIndex: null,
        };

        this.renderSamplesArrayBatchesWithArray = this.renderSamplesArrayBatchesWithArray.bind(this);
        this.setCurrentSamplesBatchAndIndex = this.setCurrentSamplesBatchAndIndex.bind(this);
    }

    setCurrentSamplesBatchAndIndex(index, samplesBatch) {
        this.props.setCurrentSamplesBatch(index, samplesBatch);
        this.setState({ currentlySelectedBatchIndex: index });
    }

    renderSamplesArrayBatchesWithArray() {
        const { samplesList } = this.props;

        try {
            if (samplesList !== undefined && samplesList !== null) {
                if (sampleList.length > 0) {
                    return samplesList.map((samplesBatch, index) => {
                        if (index === this.state.currentlySelectedBatchIndex) {
                            return <BatchListEntry
                                isSelectedState={true}
                                samplesBatch={samplesBatch}
                                key={index}
                                listEntryIndex={index}
                                setCurrentSamplesBatchAndIndex={this.setCurrentSamplesBatchAndIndex}
                            />;
                        } else {
                            return <BatchListEntry
                                isSelectedState={false}
                                samplesBatch={samplesBatch}
                                key={index}
                                listEntryIndex={index}
                                setCurrentSamplesBatchAndIndex={this.setCurrentSamplesBatchAndIndex}
                            />;
                        }
                    });
                }
            }
        } catch (err) {
            console.error('Batches could not be rendered', err);
        }
    }

    render() {
        return (
            <ul className="samples-table-block">
                {this.renderSamplesArrayBatchesWithArray()}
            </ul>
        )
    }
}
