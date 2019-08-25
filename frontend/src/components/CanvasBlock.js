import React, { Component } from "react";
import MyCanvas from "./MyCanvas";

export default class CanvasBlock extends Component {
  constructor(props) {
    super(props);
    this.state = {
      clearFunction: null,
      setIdentifyerDrawing: props.setIdentifyerDrawing,
      setterButtonIdName: "canvas-setter",
    };
    this.clearCanvasOnClick = this.clearCanvasOnClick.bind(this);
  }

  componentWillUnmount() {
    console.log('CanvasBlock ' + this.props.idNumber + ' has unmounted');
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
        <h2>Shape {props.isIdentifyBlock ? 'to identify' : props.idNumber}</h2>
        <MyCanvas
          _dimensions={props.canvasDimensions}
          setIdentifyerDrawing={this.state.setIdentifyerDrawing}
          canvasSetterButtonIdName={this.state.setterButtonIdName}
          isIdentifyBlock={props.isIdentifyBlock}
          idNumber={props.idNumber}
          registerCanvasInteractions={props.registerCanvasInteractions}
          selectClearingMethod={this.clearCanvasOnClick}
        />
        <div className="button-container">
          {!props.isIdentifyBlock ?
            <button type={"button"} onClick={this.state.clearFunction}>
              {"Clear Canvas"}
            </button>
            :
            <React.Fragment>
              <button type={"button"} onClick={this.state.clearFunction}>
                {"Clear Canvas"}
              </button>
              <button type={"button"} onClick={props.identifyDrawing}>
                {"Identify Drawing"}
              </button>
            </React.Fragment>
          }
        </div>

      </div>

    );
  }
}
