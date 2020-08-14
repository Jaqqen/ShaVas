
import React, { Component } from "react";

export default class CanvasTemplate extends Component {
    constructor(props) {
        super(props);
        this.state = {
            canvasHeight: props._dimensions.h,
            canvasWidth: props._dimensions.w,
            idNumber: props.idNumber,
            isGenerating: props.isGenerating,
            hasNeuralNetworkBeenBuilt: props.hasNeuralNetworkBeenBuilt,
            painting: false,
        };
        this.canvasRef = React.createRef();
        this.clearCanvas = this.clearCanvas.bind(this);
        this.mouseDownHandler = this.mouseDownHandler.bind(this);
        this.mouseMoveHandler = this.mouseMoveHandler.bind(this);
        this.mouseUpHandler = this.mouseUpHandler.bind(this);
    }

    static getDerivedStateFromProps(props, state) {
        if (props.hasNeuralNetworkBeenBuilt !== state.hasNeuralNetworkBeenBuilt) {
            state.hasNeuralNetworkBeenBuilt = props.hasNeuralNetworkBeenBuilt;
            return props.hasNeuralNetworkBeenBuilt;
        }
        return null;
    }

    componentDidMount() {
        const props = this.props;

        // #### pre setup for drawing ####
        const ctx = this.canvasRef.current.getContext("2d");
        ctx.lineWidth = 14;
        ctx.lineCap = "round";
        ctx.fillStyle = "white";
        ctx.fillRect(0, 0, this.state.canvasWidth, this.state.canvasHeight);

        // #### when mouse is DOWN on CANVAS ####
        this.canvasRef.current.addEventListener("mousedown",
            e => this.mouseDownHandler(props, e, ctx));

        // #### when mouse is UP on WINDOW ####
        // window.addEventListener("mouseup", () => this.mouseUpHandler(ctx));
        window.addEventListener("mouseup", () => this.mouseUpHandler(ctx));

        // #### when mouse is MOVING on CANVAS ####
        this.canvasRef.current.addEventListener("mousemove",
            e => this.mouseMoveHandler(e, ctx));

        // #### passing the clearCanvas-function to the parent component ####
        props.selectClearingMethod(this.clearCanvas);
    }

    mouseDownHandler(props, e, ctx) {
        if (!this.state.hasNeuralNetworkBeenBuilt) {
            props.registerCanvasInteractions(this.props._id);
            this.setState({
                painting: true
            });
            this.draw(e, ctx);
        } else if (this.state.hasNeuralNetworkBeenBuilt) {
            const confirmResetOnInputCanvas = window.confirm('Do you want to start over?');
            if (confirmResetOnInputCanvas) {
                props.resetInputCanvasLogic();
                this.setState({
                    hasNeuralNetworkBeenBuilt: false,
                });
            }
        } else if ((props.registerCanvasInteractions === undefined && this.state.hasNeuralNetworkBeenBuilt === undefined)) {
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

    mouseMoveHandler(e, ctx) { this.draw(e, ctx); }

    shouldDrawBeExecuted() {
        if (!this.state.painting || this.props.isGenerating || this.props.hasNeuralNetworkBeenBuilt) {
            return true;
        }
        return false;
    }

    draw(_event, context) {
        if (this.shouldDrawBeExecuted()) return;
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
        this.props.registerClearActivity(this.props._id);
    }

    render() {
        const props = this.props;

        return (
            <React.Fragment>
                <canvas
                    height={props._dimensions.h}
                    id={props._id}
                    ref={this.canvasRef}
                    width={props._dimensions.w}
                />
            </React.Fragment>
        );
    }
}
