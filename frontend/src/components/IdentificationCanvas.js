import React, { Component } from 'react'
import { identifyerContainerId } from '../shared/constants/IDGlobal';

export default class IdentificationCanvas extends Component {
  constructor(props) {
    super(props);
    this.state = {
      canvasHeight: props._dimensions.h,
      canvasWidth: props._dimensions.w,
      identificationBlock: props.identificationBlock,
      painting: false,
    };
    this.canvasRef = React.createRef();
    this.clearCanvas = this.clearCanvas.bind(this);
  }

  componentDidMount() {
    this.setState({
      isMounted: true,
    });

    const ctx = this.canvasRef.current.getContext("2d");
    // #### pre setup for drawing ####
    ctx.lineWidth = 14;
    ctx.lineCap = "round";
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.state.canvasWidth, this.state.canvasHeight);

    // #### when mouse is DOWN on CANVAS ####
    this.canvasRef.current.addEventListener("mousedown",
      e => this.mouseDownHandler(e, ctx));

    // #### when mouse is UP on WINDOW ####
    document.getElementById(identifyerContainerId).addEventListener("mouseup", () => this.mouseUpHandler(ctx));

    // #### when mouse is MOVING on CANVAS ####
    this.canvasRef.current.addEventListener("mousemove",
      e => this.mouseMoveHandler(e, ctx));

    // #### passing the clearCanvas-function to the parent component ####
    this.props.selectClearingMethod(this.clearCanvas);
  }

  mouseDownHandler(e, ctx) {
    this.setState({
      painting: true,
    });
    this.draw(e, ctx);
  }

  mouseUpHandler(ctx) {
    this.setState({
      painting: false,
    });
    ctx.beginPath();
  }

  mouseMoveHandler(e, ctx) {
    this.draw(e, ctx);
  }

  draw(_event, context) {
    if (!this.state.painting) return;
    const rect = this.canvasRef.current.getBoundingClientRect();
    context.lineTo(_event.clientX - rect.left, _event.clientY - rect.top);
    context.stroke();
    context.beginPath();
    context.moveTo(_event.clientX - rect.left, _event.clientY - rect.top);
  }

  clearCanvas() {
    const canvasContext = this.canvasRef.current.getContext("2d");
    canvasContext.clearRect(
      0,
      0,
      this.state.canvasWidth,
      this.state.canvasHeight
    );
    canvasContext.fillStyle = "white";
    canvasContext.fillRect(
      0,
      0,
      this.state.canvasWidth,
      this.state.canvasHeight
    );
  }

  render() {
    const props = this.props;

    return (
      <div className="identification-canvas-wrapper">
        <canvas
          id={props._id}
          ref={this.canvasRef}
          height={props._dimensions.h}
          width={props._dimensions.w}
        />
      </div>
    )
  }
}
