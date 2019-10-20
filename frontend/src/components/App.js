import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";
import IdentifcationCanvasBlock from "./IdentificationCanvasBlock";
import * as ID from "../shared/constants/IDGlobal";
import { FetchService } from "../shared/Fetcher";

export default class App extends Component {
    constructor(props) {
        super(props);
        this.initState = {
            canvasNamesWithInteraction: [],
            doesProbabilitiesExist: false,
            getSampleArray: [],
            getSampleInterval: null,
            isGenerating: false,
            isSampleViewOn: false,
            neuralNetworkHasBeenBuild: false,
            probabilities: [],
            sample: {
                isSet: false,
                amount: 0,
            },
            sampleCount: 0,
        };
        this.state = { ...this.initState }

        this.changeInSampleAmount = this.changeInSampleAmount.bind(this);
        this.getSample = this.getSample.bind(this);
        this.identifyCanvasContent = this.identifyCanvasContent.bind(this);
        this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
        this.renderLiWithArray = this.renderLiWithArray.bind(this);
        this.resetInputCanvasLogic = this.resetInputCanvasLogic.bind(this);
        this.restartConfirmAndResetInputLogic = this.restartConfirmAndResetInputLogic.bind(this);
        this.sendDataToBackend = this.sendDataToBackend.bind(this);
        this.setGenerateButtonText = this.setGenerateButtonText.bind(this);

        this.sampleCanvasRef = React.createRef();

        this.dataClearDataLists = this.dataClearDataLists.bind(this);
        this.dataGetSample = this.dataGetSample.bind(this);
        this.dataIdentifyCanvasContent = this.dataIdentifyCanvasContent.bind(this);
        this.dataSendDataToBackend = this.dataSendDataToBackend.bind(this);
        this.dataStartWithExistingNN = this.dataStartWithExistingNN.bind(this);
        // this.startWithExistingNN();
    }

    allCanvasHaveContent() {
        const { canvasNamesWithInteraction } = this.state;
        if (canvasNamesWithInteraction.includes(ID.shapeOneId) && canvasNamesWithInteraction.includes(ID.shapeTwoId)) {
            return true;
        }
        return false;
    }

    changeInSampleAmount(event) {
        if (event.target.value >= 200) {
            this.setState({
                sample: {
                    isSet: true,
                    amount: event.target.value,
                }
            });
        } else {
            this.setState({
                sample: {
                    isSet: false,
                    amount: 0,
                }
            });
        }
    }

    componentDidMount() { this.clearDataLists(); }

    // ##### API-CALL #####
    // GET - Clear lists in backend when starting application or refreshing
    clearDataLists() {
        FetchService.get('/clear_datalist', 'ClearDataLists', this.dataClearDataLists);
    }

    dataClearDataLists(data) {
        Object.keys(data).forEach(key => {
            console.log(key + ' ' + data[key]);
        });
    }

    dataGetSample(data) {
        if (!data['samples_created']) {
            const { getSampleArray, sampleCount } = this.state;
            const currentDataSamples = data['sample_list'].slice(sampleCount);
            const nextSampleCount = sampleCount + currentDataSamples.length;
            let joinedSampleArray;
            if (!(currentDataSamples.length <= 0)) {
                joinedSampleArray = [...getSampleArray, ...currentDataSamples]
                this.setState({
                    sampleCount: nextSampleCount,
                    getSampleArray: joinedSampleArray,
                })
            }
        } else {
            this.setState({
                neuralNetworkHasBeenBuild: true,
                isGenerating: false,
            });
            clearInterval(this.state.getSampleInterval);
        }
    }

    dataIdentifyCanvasContent(data) {
        try {
            let temp_probas = [];
            data[0].forEach((probability) => {
                temp_probas.push(probability);
            })
            this.setState({
                doesProbabilitiesExist: true,
                probabilities: temp_probas
            })
        } catch (e) { }
    }

    dataSendDataToBackend(data) {
        console.log('OK - /send_canvas \n', data);
        setTimeout(() => {
            this.getSample();

            const myInterval = setInterval(() => {
                this.getSample();
            }, 10000)

            this.setState({
                getSampleInterval: myInterval
            });
        }, 1000)
    }

    dataStartWithExistingNN(data) {
        this.setImageIntoDrawingCanvas(ID.shapeOneId, data.shape_one_image);
        this.setImageIntoDrawingCanvas(ID.shapeTwoId, data.shape_two_image);
        this.setState({
            getSampleArray: [...data.sample_list],
            neuralNetworkHasBeenBuild: true
        });
    }

    disableGenerateButton() {
        const { neuralNetworkHasBeenBuild, isGenerating, sample } = this.state;

        if (!this.allCanvasHaveContent() || neuralNetworkHasBeenBuild
            || isGenerating || !sample.isSet) { return true }

        return false;
    }

    disableSampleInput() {
        const { neuralNetworkHasBeenBuild, isGenerating } = this.state;

        if (!this.allCanvasHaveContent() || neuralNetworkHasBeenBuild
            || isGenerating) { return true }

        return false;
    }

    // ##### API-CALL #####
    // GET - SAMPLE OF THE DATA THAT IS BEING GENERATED
    getSample() {
        FetchService.get('/getSample', 'GetSample', this.dataGetSample);
    }

    // ##### API-CALL #####
    // POST - IDENTIFY THE DRAWING
    identifyCanvasContent() {
        const identificationCanvas = document
            .getElementById(ID.shapeIdentificationId).getContext('2d')['canvas'].toDataURL('image/png');

        const obj = { 'dataI': identificationCanvas }

        FetchService.post('/identify', obj, 'IdentifyCanvasContent', this.dataIdentifyCanvasContent);
    }

    registerCanvasInteractions(canvasName) {
        this.setState(prevState => ({
            canvasNamesWithInteraction: [...prevState.canvasNamesWithInteraction, canvasName],
        }));
    }

    renderLiWithArray() {
        const { getSampleArray } = this.state;

        try {
            return getSampleArray.map((image, index) => {
                return <li className="sample-li" onClick={() => this.selectSample(image)} key={index}>Shape #{index}</li>;
            })
        } catch (err) { }
    }

    renderSampleOverlay() {
        const { getSampleArray, isGenerating, neuralNetworkHasBeenBuild, isSampleViewOn, sample } = this.state;

        if (isGenerating || neuralNetworkHasBeenBuild) {
            return <React.Fragment>
                <div id={ID.sampleButtonGroup}>
                    <button className="sample-button" onClick={() => this.restartConfirmAndResetInputLogic()}>Restart</button>
                    <button className="sample-button" onClick={() => this.turnOffSampleOverlay()}>{isSampleViewOn ? 'Show' : 'Hide'} Sample-View</button>
                </div>
                <div id={ID.appSampleOverlayId} className={neuralNetworkHasBeenBuild ? 'finished' : 'loading'}>
                    <h2>Sample View</h2>
                    <h4>{neuralNetworkHasBeenBuild ?
                        'Finished creating Samples and NN'
                        :
                        'Currently generated samples: ' + getSampleArray.length + '/' + sample.amount * 2
                    }</h4>
                    <div id={ID.appSampleContentId}>
                        <canvas
                            className="sample-container"
                            height={75}
                            ref={this.sampleCanvasRef}
                            width={100}
                        />
                        <div id={ID.sampleList} >
                            <h3 className="select-shape-h3">Select a shape</h3>
                            <ul className="sample-container sample-list">
                                {this.renderLiWithArray()}
                            </ul>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        } else {
            return null
        }
    }

    resetInputCanvasLogic() {
        this.setState({ ...this.initState })

        this.clearDataLists();
    }

    restartConfirmAndResetInputLogic() {
        const confirmResetOnSampleView = window.confirm('Do you want to start over?');
        if (confirmResetOnSampleView) {
            this.resetInputCanvasLogic();
        }
    }

    selectSample(image) {
        const ctx = this.sampleCanvasRef.current.getContext("2d");
        const imageData = ctx.createImageData(100, 75);
        let i = 0;
        image.forEach(row => {
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
                i += 4
            });
        });
        ctx.putImageData(imageData, 0, 0);
    }

    // ##### API-CALL #####
    // POST - DATA TO BACKEND
    sendDataToBackend() {
        const { sample } = this.state;

        const canvas0 = document.getElementById(ID.shapeOneId)
            .getContext('2d')['canvas'].toDataURL('image/png');
        const canvas1 = document.getElementById(ID.shapeTwoId)
            .getContext('2d')['canvas'].toDataURL('image/png');

        const sampleAmount = parseInt(sample.amount);

        this.setState({ isGenerating: true });

        const obj = { 'data0': canvas0, 'data1': canvas1, 'sampleAmount': sampleAmount, };

        FetchService.post('/send_canvas', obj, 'SendDataToBackend', this.dataSendDataToBackend);
    }

    setGenerateButtonText() {
        const { isGenerating, neuralNetworkHasBeenBuild } = this.state;
        if (this.allCanvasHaveContent()) {
            if (isGenerating) {
                return 'Generating samples and Neural Network';
            } else if (neuralNetworkHasBeenBuild) {
                return 'Complete';
            } else if (!this.disableSampleInput()) {
                return 'Need sample amount';
            } else {
                return 'Generate samples';
            }
        } else {
            return 'Please draw your shapes!';
        }
    }

    setImageIntoDrawingCanvas(idOfCanvas, image) {
        const ctx = document.getElementById(idOfCanvas).getContext("2d");
        const imageData = ctx.createImageData(400, 300);
        let i = 0;
        image.forEach(row => {
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
                i += 4
            });
        });
        ctx.putImageData(imageData, 0, 0);
    }

    // ##### API-CALL #####
    // GET - Ask user if he wants to start with an existing NN
    startWithExistingNN() {
        const confirmStart = window.confirm('Do you want to start with an existing NN?');
        if (confirmStart) {
            FetchService.get('/start_with_existing_nn', 'StartWithExistingNN', this.dataStartWithExistingNN);
        }
    }

    turnOffSampleOverlay() {
        this.setState(prevState => ({
            isSampleViewOn: !prevState.isSampleViewOn,
        }));

        document.getElementById(ID.appSampleOverlayId).classList.toggle("onOff");
    }


    render() {
        const dimensions = { h: 300, w: 400 };

        const { neuralNetworkHasBeenBuild, isGenerating, doesProbabilitiesExist, probabilities } = this.state;

        return (
            <div>
                <h1>ShaVas</h1>
                <hr />
                <div>
                    {this.renderSampleOverlay()}
                    <div className="App">
                        <CanvasBlock
                            _id={ID.shapeOneId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            shapeNumber={0}
                        />
                        <CanvasBlock
                            _id={ID.shapeTwoId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            shapeNumber={1}
                        />
                    </div>
                    <div id={ID.generateButtonId}>
                        <div>
                            <p>Number of samples to generate (must be at least 200): </p>
                            <input
                                className="inputNumberClass"
                                disabled={this.disableSampleInput()}
                                id={ID.sampleAmountInput}
                                min="200"
                                onChange={this.changeInSampleAmount}
                                type="number"
                            />
                        </div>
                        <button
                            disabled={this.disableGenerateButton()}
                            type='button'
                            onClick={this.sendDataToBackend}>
                            {this.setGenerateButtonText()}
                        </button>
                    </div>
                    <hr />
                </div>
                {
                    neuralNetworkHasBeenBuild ?
                        <div id={ID.identifyerContainerId}>
                            <IdentifcationCanvasBlock
                                _id={ID.shapeIdentificationId}
                                canvasDimensions={dimensions}
                                doesProbabilitiesExist={doesProbabilitiesExist}
                                identifyCanvasContent={this.identifyCanvasContent}
                                probabilities={probabilities}
                            />
                        </div>
                        :
                        <h2>Please draw the shapes and generate samples before identification.</h2>
                }
            </div >
        );
    }
};
