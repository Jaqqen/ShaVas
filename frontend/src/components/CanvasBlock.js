import React, { Component } from "react";
import CanvasTemplate from "./CanvasTemplate";

export default class CanvasBlock extends Component {
    constructor(props) {
        super(props);
        this.state = {
            clearFunction: null,
        };
        this.clearCanvasOnClick = this.clearCanvasOnClick.bind(this);
    }

    clearCanvasOnClick(clearFunc) {
        this.setState({ clearFunction: clearFunc, });
    }

    render() {
        const props = this.props;

        return (
            <div className="canvas-block-holder">
                <h2>{props.shapeNumber + 1 + '.'} Canvas</h2>
                <CanvasTemplate
                    _dimensions={props.canvasDimensions}
                    idNumber={props.idNumber}
                    _id={props._id}
                    isGenerating={props.isGenerating}
                    registerCanvasInteractions={props.registerCanvasInteractions}
                    registerClearActivity={props.registerClearActivity}
                    resetInputCanvasLogic={props.resetInputCanvasLogic}
                    selectClearingMethod={this.clearCanvasOnClick}
                    startingProcessesTime={props.startingProcessesTime}
                />
                <div className="button-container">
                    <button
                        disabled={props.startingProcessesTime !== null}
                        onClick={this.state.clearFunction}
                        type='button'
                    >
                        Clear Canvas
          </button>
                </div>
            </div>
        );
    }
}
