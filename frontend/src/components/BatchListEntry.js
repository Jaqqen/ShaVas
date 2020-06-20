import React, { Component } from 'react'

export default class BatchListEntry extends Component {
    showEntryBatchAndSetSelected() {
        const { setCurrentSamplesBatchAndIndex, samplesBatch, listEntryIndex } = this.props;

        setCurrentSamplesBatchAndIndex(listEntryIndex, samplesBatch);
    }

    render() {
        const { listEntryIndex, isSelectedState } = this.props;

        return (
            <div style={{display: 'flex', height: '25px', position: 'relative'}}>
                {isSelectedState ? 
                    <React.Fragment>
                        <span className="active-batch-arrow">➤</span> <li
                            className="sample-li-batch"
                            onClick={() => this.showEntryBatchAndSetSelected()}
                            >
                            Batch #{listEntryIndex+1}
                        </li>
                    </React.Fragment>
                    :
                    <React.Fragment>
                        <li
                            className="sample-li-batch"
                            onClick={() => this.showEntryBatchAndSetSelected()}
                            >
                            Batch #{listEntryIndex+1}
                        </li>
                    </React.Fragment>
                }
            </div>
        )
    }
}
