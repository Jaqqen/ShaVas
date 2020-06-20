import React, { Component } from 'react'

export default class SampleCanvas extends Component {
    constructor(props) {
        super(props);
        this.state = {
            sample: props.sample,
        }
        this.canvasRef = React.createRef();
    }

    componentDidMount() {
        try {
            const { dimensions } = this.props;
            const ctx = this.canvasRef.current.getContext('2d');
            const imageData = ctx.createImageData(dimensions.w, dimensions.h);
            let i = 0;

            this.state.sample.forEach(row => {
                row.forEach(col => {
                    if (col <= 250) {
                        imageData.data[i] = 0;
                        imageData.data[i + 1] = 0;
                        imageData.data[i + 2] = 0;
                        imageData.data[i + 3] = 255;
                    } else {
                        imageData.data[i] = 255;
                        imageData.data[i + 1] = 255;
                        imageData.data[i + 2] = 255;
                        imageData.data[i + 3] = 255;
                    }
                    i += 4;
                });
            });
            ctx.putImageData(imageData, 0, 0);
        } catch (error) {
            console.error('SampleCanvas-Errors: ', error);
        }
    }

    render() {
        const sampleDimension = 100;

        return (
            <div className="samples-tables-sample">
                <canvas
                    height={sampleDimension}
                    ref={this.canvasRef}
                    width={sampleDimension}
                />
            </div>
        )
    }
}
