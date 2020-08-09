import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";
import SamplesBatchTableBlock from "./SamplesBatchTableBlock";
import IdentifcationCanvasBlock from "./IdentificationCanvasBlock";
import * as ID from "../shared/constants/IDGlobal";
import { FetchService } from "../shared/rest/Fetcher";

export default class App extends Component {
    constructor(props) {
        super(props);
        this.initState = {
            canvasNamesWithInteraction: [],
            doesProbabilitiesExist: false,
            finishingProcessInformation: {
                endTime: null,
                timeSpent: null,
            },
            generatedSamples: {},
            isGenerating: false,
            minimumSampleSize: 1100,
            neuralNetworkHasBeenBuild: false,
            probabilities: [],
            sample: {
                isSet: false,
                amount: 0,
            },
            startingProcessInformation: {
                startTime: null,
                batchesPerImg: null,
                prcsStartedPerImg: null,
            },
            neuralNetworkBuildInformation: {
                hasBeenStarted: null,
                startTime: null,
            }
        };
        this.state = { ...this.initState }

        // Simple bindings
        this.changeInSampleAmount = this.changeInSampleAmount.bind(this);
        this.getSamples = this.getSamples.bind(this);
        this.identifyCanvasContent = this.identifyCanvasContent.bind(this);
        this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
        this.renderFinishingProcessInformation = this.renderFinishingProcessInformation.bind(this);
        this.registerClearActivity = this.registerClearActivity.bind(this);
        this.renderStartingProcessInformation = this.renderStartingProcessInformation.bind(this);
        this.resetInputCanvasLogic = this.resetInputCanvasLogic.bind(this);
        this.restartConfirmAndResetInputLogic = this.restartConfirmAndResetInputLogic.bind(this);
        this.sendImagesDataToBackend = this.sendImagesDataToBackend.bind(this);
        this.setGenerateButtonText = this.setGenerateButtonText.bind(this);
        this.buildNeuralNetwork = this.buildNeuralNetwork.bind(this);
        this.hasNeuralNetworkBuildFinished = this.hasNeuralNetworkBuildFinished.bind(this);

        // * Reference to canvas
        this.sampleCanvasRef = React.createRef();

        // Data functions - used in requests
        this.dataGetSamples = this.dataGetSamples.bind(this);
        this.dataIdentifyCanvasContent = this.dataIdentifyCanvasContent.bind(this);
        this.dataSendDataToBackend = this.dataSendDataToBackend.bind(this);
        this.dataBuildNeuralNetwork = this.dataBuildNeuralNetwork.bind(this);
        this.dataHasNeuralNetworkBuildFinished = this.dataHasNeuralNetworkBuildFinished.bind(this);
    }

    /**
     * * This function checks if both canvas' have some kind of cotent.
     * * If both canvas' have content it returns true.
     */
    allCanvasHaveContent() {
        const { canvasNamesWithInteraction } = this.state;
        if (canvasNamesWithInteraction.includes(ID.shapeOneId) &&
            canvasNamesWithInteraction.includes(ID.shapeTwoId)) {
            return true;
        }
        return false;
    }

    buildNeuralNetwork() {
            this.setState({
                isGenerating: true,
                neuralNetworkBuildInformation: {
                    hasBeenStarted: true,
                },
                neuralNetworkHasBeenBuild: false,
            });
        setTimeout(() => {
            FetchService.get('/buildNeuralNetwork', 'BuildNeuralNetwork', this.dataBuildNeuralNetwork);
        }, 5000);
    }

    dataBuildNeuralNetwork(data) {
        if (data.hasBeenStarted) {
            this.setState({
                neuralNetworkBuildInformation: {
                    hasBeenStarted: data.hasBeenStarted,
                }
            });
            this.hasNeuralNetworkBuildFinished();
        } else {
            this.buildNeuralNetwork();
        }
    }

    hasNeuralNetworkBuildFinished() {
        setTimeout(() => {
            FetchService.get('/hasNeuralNetworkBuildFinished', 'HasNeuralNetworkBuildFinished', this.dataHasNeuralNetworkBuildFinished);
        }, 60000);
    }

    dataHasNeuralNetworkBuildFinished(data) {
        if (data.hasBeenBuilt) {
            this.setState({
                isGenerating: false,
                neuralNetworkHasBeenBuild: data.hasBeenBuilt,
            });
        } else {
            this.hasNeuralNetworkBuildFinished();
        }
    }

    changeInSampleAmount(event) {
        if (event.target.value >= this.state.minimumSampleSize) {
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

    dataGetSamples(data) {
        try {
            const { generatedSamples } = this.state;

            let tempGeneratedSamples = generatedSamples;

            if ('samples_end_response' in data && data.samples_created) {

                const frontendContent = data.samples_end_response;
                const allResponsesReturned = frontendContent.all_responses_returned;
                if (allResponsesReturned) {
                    frontendContent.sample_list_batches.forEach(samplesBatch => {
                        const currentImageIndex = samplesBatch._image_index;
                        const currentSamplesList = samplesBatch._samples_list;

                        if (!(currentImageIndex in tempGeneratedSamples)) {
                            tempGeneratedSamples[currentImageIndex.toString()] = [currentSamplesList];
                        } else {
                            tempGeneratedSamples[currentImageIndex.toString()].push(currentSamplesList);
                        }
                    });

                    this.setState({
                        finishingProcessInformation: {
                            endTime: frontendContent.end_time,
                            timeSpent: frontendContent.time_spent
                        },
                        generatedSamples: tempGeneratedSamples,
                    });

                    this.buildNeuralNetwork();
                } else {
                    this.getSamples(5000);
                }
            } else {
                const sampleListBatches = data.sample_list_batches;

                sampleListBatches.forEach(samplesBatch => {
                    const currentImageIndex = samplesBatch._image_index;
                    const currentSamplesList = samplesBatch._samples_list;

                    if (!(currentImageIndex in tempGeneratedSamples)) {
                        tempGeneratedSamples[currentImageIndex.toString()] = [currentSamplesList];
                    } else {
                        tempGeneratedSamples[currentImageIndex.toString()].push(currentSamplesList);
                    }
                });

                this.setState({
                    generatedSamples: tempGeneratedSamples,
                });
                if (Array.isArray(sampleListBatches) && sampleListBatches.length) {
                    this.getSamples(5000);
                } else {
                    this.getSamples(20000);
                }
            }
        } catch (error) {
            console.error(error, new Date().toLocaleTimeString());
            this.getSamples(20000);
        }
    }

    /**
     *
     * @param data an object which holds the probabilities
     */
    dataIdentifyCanvasContent(data) {
        try {
            let temp_probas = [];
            data[0].forEach((probability) => {
                temp_probas.push(probability);
            });
            this.setState({
                doesProbabilitiesExist: true,
                probabilities: temp_probas
            });
        } catch (e) {
            console.log(e);
        }
    }

    /**
     * * This function sends the images to the backend and executes:
     * -> getSamples()
     * * After 1 second: getSamples() and sets the interval into the state.
     * * Every 10 seconds: getSamples()
     *
     * @param data ---
     */
    dataSendDataToBackend(data) {
        try {
            this.getSamples(20000);

            this.setState({
                isGenerating: data.hasBeenStarted,
                startingProcessInformation: {
                    startTime: data.startTime,
                    batchesPerImg: data.batchesPerImg,
                    prcsStartedPerImg: data.prcsStartedPerImg,
                }
            });
        } catch (error) {
            document.getElementById(ID.generateButtonId).disabled = false;
        }
    }

    /**
     * * This functions disables the generate button.
     *
     * * It uses:
     * -> allCanvasHaveContent()
     */
    disableGenerateButton() {
        const { neuralNetworkHasBeenBuild, isGenerating, sample } = this.state;

        if (!this.allCanvasHaveContent() ||
            neuralNetworkHasBeenBuild ||
            isGenerating ||
            !sample.isSet) { return true; }

        return false;
    }

    /**
     * * This functions disables the sample input.
     *
     * * It uses:
     * -> allCanvasHaveContent()
     */
    disableSampleInput() {
        const { neuralNetworkHasBeenBuild, isGenerating } = this.state;

        if (!this.allCanvasHaveContent() ||
            neuralNetworkHasBeenBuild ||
            isGenerating) { return true; }

        return false;
    }

    // >>> GET - SAMPLE OF THE DATA THAT IS BEING GENERATED
    // -> dataGetSamples()
    getSamples(milSecs) {
        setTimeout(() => {
            FetchService.get('/getSamples', 'GetSamples', this.dataGetSamples);
        }, milSecs);
    }

    // >>> POST - IDENTIFY THE DRAWING
    // -> dataIdentifyCanvasContent()
    identifyCanvasContent() {
        const identificationCanvas = document.getElementById(ID.shapeIdentificationId)
            .getContext('2d')['canvas'].toDataURL('image/png');

        const obj = { 'dataI': identificationCanvas };

        FetchService.post('/identify', obj, 'IdentifyCanvasContent', this.dataIdentifyCanvasContent);
    }

    /**
     * * This function is passed down to the CanvasTemplate to register every interaction and
     * * update the current state with every new interaction.
     *
     * @param canvasName the name of the canvas that the user has been interacting with
     */
    registerCanvasInteractions(canvasName) {
        this.setState(prevState => ({
            canvasNamesWithInteraction: [...prevState.canvasNamesWithInteraction, canvasName],
        }));
    }

    /**
     * * This function is passed down to the CanvasTemplate to register every clear-execution and
     * * remove all occurences of the canvas that has been cleared.
     *
     * @param canvasName the name of the canvas that the user has cleared
     */
    registerClearActivity(canvasName) {
        const { canvasNamesWithInteraction } = this.state;
        const newCanvasNamesWithInteraction = canvasNamesWithInteraction
            .filter(currentCanvasName => currentCanvasName !== canvasName);
        this.setState({ canvasNamesWithInteraction: newCanvasNamesWithInteraction, });
    }

    renderStartingProcessInformation() {
        const { startTime, batchesPerImg, prcsStartedPerImg } = this.state.startingProcessInformation;

        return (
            <React.Fragment>
                <span>Start: <i>{startTime}</i></span>
                <span>Batches per image: <i>{batchesPerImg}</i></span>
                <span>Processes started per image: <i>{prcsStartedPerImg}</i></span>
            </React.Fragment>
        );
    }

    renderFinishingProcessInformation() {
        const { endTime, timeSpent } = this.state.finishingProcessInformation;

        return (
            <React.Fragment>
                <span>End: <i>{endTime}</i></span>
                <span>Time spent: <i>{timeSpent}</i></span>
            </React.Fragment>
        );
    }

    /**
     * * This function resets the state to its intial state
     */
    resetInputCanvasLogic() {
        this.setState({ ...this.initState });
    }

    /**
     * * This function opens a confirmation-dialog.
     * ? If confirmResetOnSampleView
     * * reset the state to intial state
     * -> resetInputCanvasLogic()
     */
    restartConfirmAndResetInputLogic() {
        const confirmResetOnSampleView = window.confirm('Do you want to start over?');
        if (confirmResetOnSampleView) {
            this.resetInputCanvasLogic();
        }
    }

    // >>> POST - DATA TO BACKEND
    sendImagesDataToBackend() {
        document.getElementById(ID.generateButtonId).disabled = true;

        const { sample } = this.state;

        const canvas0 = document.getElementById(ID.shapeOneId)
            .getContext('2d')['canvas'].toDataURL('image/png');
        const canvas1 = document.getElementById(ID.shapeTwoId)
            .getContext('2d')['canvas'].toDataURL('image/png');

        const sampleAmount = parseInt(sample.amount);

        const obj = {'data0': canvas0, 'data1': canvas1, 'sampleAmount': sampleAmount};

        FetchService.post('/sendCanvas', obj, 'SendDataToBackend', this.dataSendDataToBackend);
    }

    /**
     * * This function sets the text of the generate button.
     * -> allCanvasHaveContent()
     * -> disableSampleInput()
     */
    setGenerateButtonText() {
        const { isGenerating, minimumSampleSize, neuralNetworkHasBeenBuild, sample } = this.state;
        if (this.allCanvasHaveContent()) {
            if (isGenerating) {
                return 'Generating samples and Neural Network';
            } else if (neuralNetworkHasBeenBuild) {
                return 'Complete';
            } else if (!this.disableSampleInput() && sample.amount < minimumSampleSize) {
                return 'Need sample amount';
            } else {
                return 'Generate samples';
            }
        } else {
            return 'Please draw your shapes!';
        }
    }

    /**
     * * This function sets the imageData into their canvasses.
     *
     * @param idOfCanvas    the id of the canvas to put the image data in
     * @param image         the image itself
     */
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
                i += 4;
            });
        });
        ctx.putImageData(imageData, 0, 0);
    }

    setLowerHalfText() {
        const { isGenerating, neuralNetworkBuildInformation, neuralNetworkHasBeenBuild } = this.state;

        if (neuralNetworkBuildInformation.hasBeenStarted && neuralNetworkHasBeenBuild === false) {
            return 'Neural network is now building, please wait.';
        } else if ( isGenerating) {
            return 'Please wait until samples have been generated.';
        } else {
            const instructionText = [
                'Draw two simple shapes.',
                'Set the number of samples you want to generate with the drawn shapes.',
                'Generate shapes and wait until this panel disappears and another canvas appears.'];

            const higlightedLine = (line, index) => 
                <p
                    key={index}
                    style={{ display: 'block', width: 'auto' }}
                    >
                    <b style={{ fontSize: '1.6em' }}>{line}</b>
                </p>;

            const regularLine = (line, index) => 
                <p
                    key={index}
                    style={{ display: 'block', width: 'auto', color: 'rgba(0, 0, 0, 0.3)' }}
                    >
                    {line}
                </p>;

            return <div id={ID.lowerHalfTextId}>
                {instructionText.map((line, index) => {
                    if (!this.allCanvasHaveContent()) {
                        if (index === 0) { return higlightedLine(line, index); }
                        else { return regularLine(line, index) };
                    }
                    if (this.allCanvasHaveContent() && this.disableGenerateButton()) {
                        if (index === 1) { return higlightedLine(line, index); }
                        else { return regularLine(line, index) };
                    }
                    if (!this.disableGenerateButton()) {
                        if (index === 2) { return higlightedLine(line, index); }
                        else { return regularLine(line, index); };
                    }
                    return null;
                })}
            </div>;
        }
    }

    // >>> GET - Ask user if he wants to start with an existing NN
    startWithExistingNN() {
        const confirmStart = window.confirm('Do you want to start with an existing NN?');
        if (confirmStart) {
            FetchService.get('/start_with_existing_nn', 'StartWithExistingNN', this.dataStartWithExistingNN);
        }
    }

    render() {
        const dimensions = { h: 400, w: 400 };
        const shapeNumber = {zero: 0, one:1};

        const {
            isGenerating, doesProbabilitiesExist, minimumSampleSize, neuralNetworkHasBeenBuild,
            probabilities, generatedSamples, startingProcessInformation, finishingProcessInformation,
            neuralNetworkBuildInformation
        } = this.state;

        return (
            <div>
                <div className={isGenerating && neuralNetworkBuildInformation.hasBeenStarted === null ? "loading-v app-heading-container": ""}>
                    <h1>ShaVas</h1>
                </div>
                <div>
                    <div className="starting-process-information">
                        {
                            Object.values(startingProcessInformation).some((val) => val !== null) ?
                                this.renderStartingProcessInformation()
                                :
                                null
                        }
                        {
                            Object.values(finishingProcessInformation).some((val) => val !== null) ?
                                <React.Fragment>
                                     ••• 
                                    {this.renderFinishingProcessInformation()}
                                </React.Fragment>
                                :
                                null
                        }
                    </div>
                    <div className="App">
                        <div className={isGenerating && neuralNetworkBuildInformation.hasBeenStarted === null ? "loading-process-sides left-process" : ""}></div>
                        <div className={isGenerating && neuralNetworkBuildInformation.hasBeenStarted === null ? "loading-process-sides right-process" : ""}></div>
                        <SamplesBatchTableBlock
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            samplesList={generatedSamples[shapeNumber.zero]}
                            shapeNumber={shapeNumber.zero}
                        />
                        <CanvasBlock
                            _id={ID.shapeOneId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            registerClearActivity={this.registerClearActivity}
                            shapeNumber={shapeNumber.zero}
                        />
                        <CanvasBlock
                            _id={ID.shapeTwoId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            registerClearActivity={this.registerClearActivity}
                            shapeNumber={shapeNumber.one}
                        />
                        <SamplesBatchTableBlock
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            samplesList={generatedSamples[shapeNumber.one]}
                            shapeNumber={shapeNumber.one}
                        />
                    </div>
                    <div id={ID.generateButtonContainerId}>
                        <div>
                            <p>Number of samples to generate per drawing (min. {minimumSampleSize}): </p>
                            <input
                                className="inputNumberClass"
                                disabled={this.disableSampleInput()}
                                id={ID.sampleAmountInput}
                                min={minimumSampleSize}
                                onChange={this.changeInSampleAmount}
                                type="number"
                                step={1000}
                            />
                        </div>
                        <button
                            id={ID.generateButtonId}
                            disabled={this.disableGenerateButton()}
                            type='button'
                            onClick={this.sendImagesDataToBackend}>
                            {this.setGenerateButtonText()}
                        </button>
                    </div>
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
                        <div className="loading-process instructions">
                            {this.setLowerHalfText()}
                        </div>
                }
            </div >
        );
    }
};
