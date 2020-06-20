import React, { Component } from 'react'
import SampleCanvas from './SampleCanvas';

export default class SamplesBlock extends Component {


    renderCanvasWithArray() {
        const sampleDimensions = {h: 100, w: 100};
        const { currentSamplesBatch, shapeNumber } = this.props;

        try {
            if (currentSamplesBatch !== undefined && currentSamplesBatch !== null) {
                return currentSamplesBatch.map((sample, index) => {
                    return <SampleCanvas
                        dimensions={sampleDimensions}
                        key={index}
                        shapeNumber={shapeNumber}
                        indexNumber={index}
                        sample={sample}
                        />;
                });
            }
        } catch (err) {
            console.error('Canvas Ref could not be filled', err);
        }
    }


    render() {
        return (
            <ul id="samplesBlockHolder" className="samples-block">
                {this.renderCanvasWithArray()}
            </ul>
        )
    }
}
