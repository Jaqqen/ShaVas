import React, { Component } from "react";

export default class MyCanvas extends Component {
  constructor(props) {
    super(props);
    this.state = {
      canvasHeight: props._height,
      canvasWidth: props._width,
      painting: false,
      drawingIsNotSet: true,
    };
    this.canvasRef = React.createRef();
    this.clearCanvas = this.clearCanvas.bind(this);
  }

  componentDidMount() {
    const { registerCanvasInteractions, idNumber } = this.props;

    const ctx = this.canvasRef.current.getContext("2d");
    // #### pre setup for drawing ####
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.state.canvasWidth, this.state.canvasHeight);
    // #### when mouse is DOWN on CANVAS ####
    this.canvasRef.current.addEventListener("mousedown", e => {
      registerCanvasInteractions("Canvas" + idNumber);
      this.setState({
        painting: true
      });
      this.draw(e, ctx);
    });
    // #### when mouse is UP on WINDOW ####
    window.addEventListener("mouseup", () => {
      this.setState({
        painting: false
      });
      ctx.beginPath();
    });
    // #### when mouse is MOVING on CANVAS ####
    this.canvasRef.current.addEventListener("mousemove", e => {
      this.draw(e, ctx);
    });

    // #### passing the clearCanvas-function to the parent component ####
    this.props.selectClearingMethod(this.clearCanvas);

  }

  componentDidUpdate() {
    // console.log('=============');
    // console.log('CURRENT STATE --- MYCANVAS.JS', this.state);
    // console.log(this.props.idNumber);
    // console.log('=============');
  }

  componentWillUnmount() {
    console.log('MyCanvs ' + this.props.idNumber + ' has unmounted');
  }

  draw(_event, context) {
    if (this.state.drawingIsNotSet) {
      if (!this.state.painting) return;
      const rect = this.canvasRef.current.getBoundingClientRect();
      context.lineTo(_event.clientX - rect.left, _event.clientY - rect.top);
      context.stroke();
      context.beginPath();
      context.moveTo(_event.clientX - rect.left, _event.clientY - rect.top);
    }
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
    return (
      <React.Fragment>
        <canvas
          className={this.state.drawingIsNotSet ? null : 'canvasHasBeenSet'}
          id={"my-canvas" + this.props.idNumber}
          ref={this.canvasRef}
          height={this.props._dimensions.h}
          width={this.props._dimensions.w}
        />
      </React.Fragment>
    );
  }
}
