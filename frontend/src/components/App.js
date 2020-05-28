import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";
import IdentifcationCanvasBlock from "./IdentificationCanvasBlock";
import * as ID from "../shared/constants/IDGlobal";
import { FetchService } from "../shared/rest/Fetcher";

export default class App extends Component {
    constructor(props) {
        super(props);
        this.initState = {
            canvasNamesWithInteraction: [],
            doesProbabilitiesExist: false,
            getSampleArray: [],
            isGenerating: false,
            isSampleViewOn: false,
            minimumSampleSize: 10000,
            neuralNetworkHasBeenBuild: false,
            probabilities: [],
            sample: {
                isSet: false,
                amount: 0,
                dimension: 75,
            },
            sampleCount: 0,
        };
        this.state = { ...this.initState }

        // Simple bindings
        this.changeInSampleAmount = this.changeInSampleAmount.bind(this);
        this.getSamples = this.getSamples.bind(this);
        this.identifyCanvasContent = this.identifyCanvasContent.bind(this);
        this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
        this.registerClearActivity = this.registerClearActivity.bind(this);
        this.renderLiWithArray = this.renderLiWithArray.bind(this);
        this.resetInputCanvasLogic = this.resetInputCanvasLogic.bind(this);
        this.restartConfirmAndResetInputLogic = this.restartConfirmAndResetInputLogic.bind(this);
        this.sendImagesDataToBackend = this.sendImagesDataToBackend.bind(this);
        this.setGenerateButtonText = this.setGenerateButtonText.bind(this);

        // * Reference to canvas
        this.sampleCanvasRef = React.createRef();

        // Data functions - used in requests
        this.dataClearDataLists = this.dataClearDataLists.bind(this);
        this.dataGetSample = this.dataGetSample.bind(this);
        this.dataIdentifyCanvasContent = this.dataIdentifyCanvasContent.bind(this);
        this.dataSendDataToBackend = this.dataSendDataToBackend.bind(this);
        this.dataStartWithExistingNN = this.dataStartWithExistingNN.bind(this);
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

    /**
     * * This method checks wether the input value is >= 100 or less.
     * ? If it's >= 100
     * * the amount is set into the state property and the isSet-variable to true.
     * ? Else
     * * the default value is used.
     *
     * @param event the event which holds the value from the Input
     */
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

    /**
     * * Executes:
     * -> clearDataLists()
     */
    componentDidMount() { this.clearDataLists(); }

    // >>> GET - Clear lists in backend when starting application or refreshing
    // -> dataClearDataLists()
    clearDataLists() {
        FetchService.get('/clear_datalist', 'ClearDataLists', this.dataClearDataLists);
    }

    /**
     * * Prints all clear-actions from the backend into the frontend console.
     *
     * @param data an object which holds a string-like text with all clear-actions from the backend
     */
    dataClearDataLists(data) {
        Object.keys(data).forEach(key => {
            console.log(key + ' ' + data[key]);
        });
    }

    /**
     * ? If all data-samples have not been created:
     * * First, the currentDataSamples-Array is formed by slicing the data-object by the current
     * * sampleCount.
     * * Secondly, the nextSampleCount is formed by the current sampleCount and the length of the 
     * * sliced data-object.
     * * Third, a new array is formed by joining the current getSampleArray with the currentDataSamples.
     * * Now the state is updated with the joinedSampleArray and nextSampleCount.
     * ? Else
     * * The state is told that the neural network has been build and the isGenerating-property is set
     * * back to false.
     * * Afterwards, clear the interval that keeps this function going.
     *
     * @param data 
     */
    dataGetSample(data) {
        if (!data['samples_created']) {
            const { getSampleArray, sampleCount } = this.state;
            this.getSamples();
            console.log('data:', data);

            // const currentDataSamples = data['sample_list'].slice(sampleCount);
            // const nextSampleCount = sampleCount + currentDataSamples.length;

            // let joinedSampleArray;
            // if (!(currentDataSamples.length <= 0)) {
            //     joinedSampleArray = [...getSampleArray, ...currentDataSamples]
            //     this.setState({
            //         sampleCount: nextSampleCount,
            //         getSampleArray: joinedSampleArray,
            //     })
            // }
        } else {
            console.log('data:', data);

            this.setState({
                neuralNetworkHasBeenBuild: true,
                isGenerating: false,
            });
        }
    }

    /**
     * ? Try
     * * It read the array of the first data-property and pushed its values into temp_probas.
     * * Afterwards, the state is updated by telling it that probabilities exist and setting the
     * * temp_probas to its corresponding state-property.
     * ? Catch
     * * Pass
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
        console.log('OK - /send_canvas \n', data, new Date().toLocaleTimeString());

        this.getSamples();
    }

    /**
     * * This function uses the data-object to set the images into their canvasses and
     * * update the state with an already generated sample-list and set the
     * * neuralNetworkHasBeenBuild-variable to true.
     *
     * @param data the data-object which contains the images and a already generated sample-list
     */
    dataStartWithExistingNN(data) {
        this.setImageIntoDrawingCanvas(ID.shapeOneId, data.shape_one_image);
        this.setImageIntoDrawingCanvas(ID.shapeTwoId, data.shape_two_image);
        this.setState({
            getSampleArray: [...data.sample_list],
            neuralNetworkHasBeenBuild: true
        });
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
    // -> dataGetSample()
    getSamples() {
        setTimeout(() => {
            console.log('Getting samples... - ', new Date().toLocaleTimeString())
            FetchService.get('/getSamples', 'GetSamples', this.dataGetSample);
        }, 5000);
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

    /**
     * ! Needs to be reworked.
     * * This function renders every li-element in the sample-overlay.
     * -> selectSample(image)
     * ? Try
     * * Map every image and index to a li-element and return it.
     * ? Catch
     * * Pass
     */
    renderLiWithArray() {
        const { getSampleArray } = this.state;

        try {
            return getSampleArray.map((image, index) => {
                return <li className="sample-li" onClick={() => this.selectSample(image)} key={index}>
                    Shape #{index}
                </li>;
            })
        } catch (err) { }
    }

    /**
     * ! Needs to be reworked.
     * * This function renders the sample-overlay.
     * -> restartConfirmAndResetInputLogic()
     * -> turnOnOffSampleOverlay()
     * -> renderLiWithArray()
     * ? If isGenerating || neuralNetworkHasBeenBuild
     * * return the whole overlay-html
     * ? Else
     * * return nothing
     */
    renderSampleOverlay() {
        const { getSampleArray, isGenerating, neuralNetworkHasBeenBuild, isSampleViewOn, sample } = this.state;

        if (isGenerating || neuralNetworkHasBeenBuild) {
            return <React.Fragment>
                <div id={ID.sampleButtonGroup}>
                    <button
                        className="sample-button"
                        onClick={() => this.restartConfirmAndResetInputLogic()}
                    >
                        Restart
                    </button>
                    <button className="sample-button" onClick={() => this.turnOnOffSampleOverlay()}>
                        {isSampleViewOn ? 'Show' : 'Hide'} Sample-View
                    </button>
                </div>
                <div
                    id={ID.appSampleOverlayId}
                    className={neuralNetworkHasBeenBuild ? 'finished' : 'loading'}
                >
                    <h2>Sample View</h2>
                    <h4>{neuralNetworkHasBeenBuild ?
                        'Finished creating Samples and NN'
                        :
                        'Currently generated samples: ' + getSampleArray.length + '/' + sample.amount * 2
                    }</h4>
                    <div id={ID.appSampleContentId}>
                        <div id={ID.sampleContainerVerticalWrapper}>
                            <div id={ID.sampleContainerHorizontalWrapper}>
                                <canvas
                                    height={sample.dimension}
                                    ref={this.sampleCanvasRef}
                                    width={sample.dimension}
                                />
                            </div>
                        </div>
                        <div id={ID.sampleList} >
                            <h3 className="select-shape-h3">Select a shape</h3>
                            <ul className="sample-list">
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

    /**
     * * This function resets the state to its intial state and clears the generated data in the backend.
     * -> clearDataLists()
     */
    resetInputCanvasLogic() {
        this.setState({ ...this.initState });

        this.clearDataLists();
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

    /**
     * * This function uses the image-parameter to fill the Canvas-context with the image.data.
     * 
     * @param image the image that should be displayed
     */
    selectSample(image) {
        const { sample } = this.state;
        const ctx = this.sampleCanvasRef.current.getContext("2d");
        const imageData = ctx.createImageData(sample.dimension, sample.dimension);
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

    // >>> POST - DATA TO BACKEND
    sendImagesDataToBackend() {
        const { sample } = this.state;

        const canvas0 = document.getElementById(ID.shapeOneId)
            .getContext('2d')['canvas'].toDataURL('image/png');
        const canvas1 = document.getElementById(ID.shapeTwoId)
            .getContext('2d')['canvas'].toDataURL('image/png');

        const sampleAmount = parseInt(sample.amount);

        this.setState({ isGenerating: true });

        const obj = {'data0': canvas0, 'data1': canvas1, 'sampleAmount': sampleAmount};

        FetchService.post('/send_canvas', obj, 'SendDataToBackend', this.dataSendDataToBackend);
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
        const { isGenerating } = this.state;

        if (isGenerating) {
            return 'Please wait until samples have been generated and the neural network has been build.';
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

    /**
     * ! Needs to be reworked.
     * * This function toggles the sample-overlay.
     */
    turnOnOffSampleOverlay() {
        this.setState(prevState => ({
            isSampleViewOn: !prevState.isSampleViewOn,
        }));

        document.getElementById(ID.appSampleOverlayId).classList.toggle("onOff");
    }


    render() {
        const dimensions = { h: 400, w: 400 };

        const {isGenerating, doesProbabilitiesExist, minimumSampleSize, neuralNetworkHasBeenBuild, probabilities } = this.state;

        return (
            <div>
                <div id={ID.appHeadingContainerId}>
                    <h1>ShaVas</h1>
                </div>
                <div>
                    {/* ! Needs to be reworked. */}
                    {this.renderSampleOverlay()}
                    <div className="App">
                        <CanvasBlock
                            _id={ID.shapeOneId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            registerClearActivity={this.registerClearActivity}
                            shapeNumber={0}
                        />
                        <CanvasBlock
                            _id={ID.shapeTwoId}
                            canvasDimensions={dimensions}
                            isGenerating={isGenerating}
                            neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
                            registerCanvasInteractions={this.registerCanvasInteractions}
                            resetInputCanvasLogic={this.resetInputCanvasLogic}
                            registerClearActivity={this.registerClearActivity}
                            shapeNumber={1}
                        />
                    </div>
                    <div id={ID.generateButtonId}>
                        <div>
                            <p>Number of samples to generate per drawing (min. {minimumSampleSize}): </p>
                            <input
                                className="inputNumberClass"
                                disabled={this.disableSampleInput()}
                                id={ID.sampleAmountInput}
                                placeholder={minimumSampleSize}
                                min={minimumSampleSize}
                                onChange={this.changeInSampleAmount}
                                type="number"
                            />
                        </div>
                        <button
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
                        <div id={ID.currentProcessId}>
                            {this.setLowerHalfText()}
                        </div>
                }
            </div >
        );
    }
};
