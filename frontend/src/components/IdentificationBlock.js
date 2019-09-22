import React, { Component } from 'react';
import IdentificationCanvas from './IdentificationCanvas';
import { identificationCanvasBlockId } from '../shared/constants/IDGlobal';

export default class IdentifcationCanvasBlock extends Component {
  constructor(props) {
    super(props);
    this.state = {
      clearFunction: null,
    };
    this.identificationBlock = React.createRef;
    this.clearCanvasOnClick = this.clearCanvasOnClick.bind(this);
  }

  componentWillUnmount() {

  }

  clearCanvasOnClick(clearFunc) {
    this.setState({
      clearFunction: clearFunc,
    });
  }

  render() {
    const props = this.props;
    return (
      <div id={identificationCanvasBlockId} className="canvas-block-holder">
        <h2>Shape to identify</h2>
        <IdentificationCanvas
          _dimensions={props.canvasDimensions}
          _id={props._id}
          selectClearingMethod={this.clearCanvasOnClick}
          identificationBlock={this.identificationBlock}
        />
        <div className="button-container">
          <button type='button' onClick={this.state.clearFunction}>
            Clear Canvas
          </button>
          <button type='button' onClick={props.identifyCanvasContent}>
            Identify Drawing
          </button>
        </div>
      </div>
    )
  }
}
