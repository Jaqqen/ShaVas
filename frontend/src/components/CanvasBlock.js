import React, { Component } from "react";
import MyCanvas from "./MyCanvas";

export default class CanvasBlock extends Component {
  constructor(props) {
    super(props);
    this.state = {
      clearFunction: null,
    };
    this.clearCanvasOnClick = this.clearCanvasOnClick.bind(this);
  }

  clearCanvasOnClick(clearFunc) {
    this.setState({
      clearFunction: clearFunc
    });
  }

  render() {
    const props = this.props;
    return (
      <div className="canvas-block-holder">
        <h2>Shape {props.shapeNumber}</h2>
        <MyCanvas
          _dimensions={props.canvasDimensions}
          neuralNetworkHasBeenBuild={props.neuralNetworkHasBeenBuild}
          idNumber={props.idNumber}
          _id={props._id}
          isGenerating={props.isGenerating}
          registerCanvasInteractions={props.registerCanvasInteractions}
          resetInputCanvasLogic={props.resetInputCanvasLogic}
          selectClearingMethod={this.clearCanvasOnClick}
        />
        <div className="button-container">
          <button
            disabled={props.isGenerating || props.neuralNetworkHasBeenBuild}
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
