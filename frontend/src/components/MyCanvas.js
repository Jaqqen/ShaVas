
import React, { Component } from "react";
export default class MyCanvas extends Component {
  constructor(props) {
    super(props);
    this.state = {
      canvasHeight: props._dimensions.h,
      canvasWidth: props._dimensions.w,
      constructionCompleted: props.constructionCompleted,
      idNumber: props.idNumber,
      isGenerating: props.isGenerating,
      painting: false,
    };
    this.canvasRef = React.createRef();
    this.clearCanvas = this.clearCanvas.bind(this);
    this.mouseDownHandler = this.mouseDownHandler.bind(this);
    this.mouseMoveHandler = this.mouseMoveHandler.bind(this);
    this.mouseUpHandler = this.mouseUpHandler.bind(this);
  }

  static getDerivedStateFromProps(props, state) {
    if (props.constructionCompleted !== state.constructionCompleted) {
      state.constructionCompleted = props.constructionCompleted;
      return props.constructionCompleted;
    } else {
      return null;
    }
  }

  componentWillUnmount() {
    window.removeEventListener('mouseup', this.mouseUpHandler, false);
    this.canvasRef.current.removeEventListener('mousedown', this.mouseDownHandler, false);
    this.canvasRef.current.removeEventListener('mousemove', this.mouseMoveHandler, false);

    if (this.state.idNumber === 2) {
      this.props.getRootStateWhenMyCanvasUnmount();
    }
  }

  componentDidMount() {
    const props = this.props;
    const ctx = this.canvasRef.current.getContext("2d");
    // #### pre setup for drawing ####
    ctx.lineWidth = 6;
    ctx.lineCap = "round";
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, this.state.canvasWidth, this.state.canvasHeight);

    // #### when mouse is DOWN on CANVAS ####
    this.canvasRef.current.addEventListener("mousedown",
      e => this.mouseDownHandler(props, e, ctx));

    // #### when mouse is UP on WINDOW ####
    window.addEventListener("mouseup", () => this.mouseUpHandler(ctx));

    // #### when mouse is MOVING on CANVAS ####
    this.canvasRef.current.addEventListener("mousemove",
      e => this.mouseMoveHandler(e, ctx));

    // #### passing the clearCanvas-function to the parent component ####
    this.props.selectClearingMethod(this.clearCanvas);
  }

  mouseDownHandler(props, e, ctx) {
    if ((props.registerCanvasInteractions && !this.state.constructionCompleted)) {
      props.registerCanvasInteractions("Canvas" + this.state.idNumber);
      this.setState({
        painting: true
      });
      this.draw(e, ctx);
    } else if (props.registerCanvasInteractions && this.state.constructionCompleted) {
      const redoConstructionConfirm = window.confirm('Do you want to start over?');
      if (redoConstructionConfirm) {
        props.resetInputLogic();
        this.setState({
          constructionCompleted: false,
        });
      }
    } else if ((props.registerCanvasInteractions === undefined && this.state.constructionCompleted === undefined)) {
      this.setState({
        painting: true
      });
      this.draw(e, ctx);
    }
  }

  mouseUpHandler(ctx) {
    this.setState({
      painting: false
    });
    ctx.beginPath();
  }

  mouseMoveHandler(e, ctx) {
    this.draw(e, ctx);
  }

  draw(_event, context) {
    if (!this.state.painting || this.props.isGenerating || this.props.constructionCompleted) return;
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
    return (
      <React.Fragment>
        <canvas
          id={"my-canvas" + this.state.idNumber}
          ref={this.canvasRef}
          height={this.props._dimensions.h}
          width={this.props._dimensions.w}
        />
      </React.Fragment>
    );
  }
}
