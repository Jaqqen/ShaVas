import CanvasButtonGrp from './CanvasButtonGrp';
import React, { Component } from "react";
import MyCanvas from "./MyCanvas";

export default class CanvasBlock extends Component {
  constructor(props) {
    super(props);
    this.state = {
      appendDrawingToState: props.appendDrawingToState,
      clearFunction: null,
      setDrawingFunction: null,
      setIdentifyerDrawing: props.setIdentifyerDrawing,
      setterButtonIdName: "canvas-setter",
    };
    this.clearCanvasOnClick = this.clearCanvasOnClick.bind(this);
    this.setDrawingOnClick = this.setDrawingOnClick.bind(this);
  }

  componentWillUnmount() {
    console.log('CanvasBlock ' + this.props.idNumber + ' has unmounted');
  }

  clearCanvasOnClick(clearFunc) {
    this.setState({
      clearFunction: clearFunc
    });
  }

  setDrawingOnClick(setDrawingFunc) {
    this.setState({
      setDrawingFunction: setDrawingFunc
    });
  }

  render() {
    return (
      <div className="canvas-block-holder">
        <h2>Shape {this.props.identifyer ? 'to identify' : this.props.idNumber}</h2>
        <MyCanvas
          _height={300}
          _width={400}
          addElementToCanvasBlockArray={this.state.appendDrawingToState}
          setIdentifyerDrawing={this.state.setIdentifyerDrawing}
          canvasSetterButtonIdName={this.state.setterButtonIdName}
          identifyer={this.props.identifyer}
          idNumber={this.props.idNumber}
          selectClearingMethod={this.clearCanvasOnClick}
          selectSetDrawingMethod={this.setDrawingOnClick}
        />
        <div className="button-container">
          <CanvasButtonGrp
            clearFunction={this.state.clearFunction}
            setDrawingFunction={this.state.setDrawingFunction}
          />
        </div>

      </div>

    );
  }
}
