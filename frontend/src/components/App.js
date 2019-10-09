import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";
import IdentifcationCanvasBlock from "./IdentificationBlock";
import { shapeOneId, shapeTwoId, shapeIdentificationId, identifyerContainerId, generateButtonId } from "../shared/constants/IDGlobal";

export default class App extends Component {
  constructor(props) {
    super(props);
    this.initState = {
      canvasNamesWithInteraction: [],
      neuralNetworkHasBeenBuild: false,
      isGenerating: false,
      myInterval: null,
      doesProbabilitiesExist: false,
    };
    this.state = { ...this.initState }
    this.fetchIfNeuralNetwork = this.fetchIfNeuralNetwork.bind(this);
    this.getSample = this.getSample.bind(this);
    this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
    this.resetInputCanvasLogic = this.resetInputCanvasLogic.bind(this);
    this.sendDataToBackend = this.sendDataToBackend.bind(this);
    this.identifyCanvasContent = this.identifyCanvasContent.bind(this);
  }

  componentDidMount() {
    this.fetchClearDatalist();
    this.fetchIfNeuralNetwork();
  }

  // GET - CLEAR LIST VARIABLES IN BACKEND
  async fetchClearDatalist() {
    await fetch('/clear_datalist')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        Object.keys(data).forEach(key => {
          console.log(key + ' ' + data[key]);
        });
      })
      .catch(error => console.log('Error', error))
  }

  // GET - FETCH THE NEURAL NETWORK MODEL
  async fetchIfNeuralNetwork() {
    await fetch('/if_neural_network')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        console.log('OK - fetchIfNeuralNetwork', data);
        if (data === true) {
          this.setState({
            neuralNetworkHasBeenBuild: false,
          });
        }
      })
      .catch(error => console.log('Error', error))
  }

  // POST - DATA TO BACKEND
  async sendDataToBackend() {
    const canvas0 = document.getElementById(shapeOneId).getContext('2d')['canvas'].toDataURL('image/png');
    const canvas1 = document.getElementById(shapeTwoId).getContext('2d')['canvas'].toDataURL('image/png');

    this.setState({ isGenerating: true });

    const obj = {
      'data0': canvas0,
      'data1': canvas1,
    };

    await fetch('/send_canvas', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(obj)
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong in /send_canvas...');
        }
      })
      .then(data => {
        console.log('OK - /send_canvas \n', data);
        const myInterval = setInterval(() => {
          this.getSample();
        }, 1000)
        this.setState({
          myInterval: myInterval
        });
      })
      .catch(error => console.log('ERROR - Catch: /send_canvas ', error));

  }

  // GET - SAMPLE OF THE DATA THAT IS BEING GENERATED
  async getSample() {
    await fetch('/getSample')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong in /getSample...');
        }
      })
      .then(data => {
        if (!data.samples_created) {
          console.log('OK - FALSE - /getSample: ', data);
        } else {
          console.log('OK - TRUE - /getSample: ', data);
          this.setState({
            neuralNetworkHasBeenBuild: true,
            isGenerating: false,
          });
          clearInterval(this.state.myInterval);
        }
      })
      .catch(error => console.log('ERROR', error))
  }

  // POST - IDENTIFY THE DRAWING
  async identifyCanvasContent() {
    const identificationCanvas = document
      .getElementById(shapeIdentificationId).getContext('2d')['canvas'].toDataURL('image/png');

    const obj = { 'dataI': identificationCanvas }

    await fetch('/identify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(obj)
    })
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        try {
          this.setState({
            doesProbabilitiesExist: true,
          })
          console.log('>> IDENTIFIED', data);
        } catch (e) {
          console.log('<< NOT IDENTIFED', e);
        }
      })
      .catch(error => console.log('ERROR', error))
  }

  registerCanvasInteractions(canvasName) {
    this.setState(prevState => ({
      canvasNamesWithInteraction: [...prevState.canvasNamesWithInteraction, canvasName],
    }));
  }

  allCanvasHaveContent() {
    const { canvasNamesWithInteraction } = this.state;
    if (canvasNamesWithInteraction.includes(shapeOneId) && canvasNamesWithInteraction.includes(shapeTwoId)) {
      return true;
    }
    return false;
  }

  async resetInputCanvasLogic() {
    this.setState({ ...this.initState })

    this.fetchClearDatalist();
  }

  disableGenerateButton() {
    const { neuralNetworkHasBeenBuild, isGenerating } = this.state;
    if (!this.allCanvasHaveContent() || neuralNetworkHasBeenBuild || isGenerating) {
      return true
    }
    return false;
  }

  render() {
    const dimensions = { h: 300, w: 400 };

    const { neuralNetworkHasBeenBuild, isGenerating, doesProbabilitiesExist } = this.state;

    return (
      <div>
        <h1>ShaVas</h1>
        <hr />
        <div>
          <div className="App">
            <CanvasBlock
              canvasDimensions={dimensions}
              neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
              shapeNumber={0}
              _id={shapeOneId}
              isGenerating={isGenerating}
              registerCanvasInteractions={this.registerCanvasInteractions}
              resetInputCanvasLogic={this.resetInputCanvasLogic}
            />
            <CanvasBlock
              canvasDimensions={dimensions}
              neuralNetworkHasBeenBuild={neuralNetworkHasBeenBuild}
              shapeNumber={1}
              _id={shapeTwoId}
              isGenerating={isGenerating}
              registerCanvasInteractions={this.registerCanvasInteractions}
              resetInputCanvasLogic={this.resetInputCanvasLogic}
            />
          </div>
          <div id={generateButtonId}>
            <button
              disabled={this.disableGenerateButton()}
              type='button'
              onClick={this.sendDataToBackend}>
              {this.allCanvasHaveContent() ?
                isGenerating ?
                  'Generating samples and Neural Network'
                  :
                  neuralNetworkHasBeenBuild ?
                    'Complete'
                    :
                    'Generate samples'
                :
                'Please draw your shapes!'}
            </button>
          </div>
          <hr />
        </div>
        {neuralNetworkHasBeenBuild ?
          <div id={identifyerContainerId}>
            <IdentifcationCanvasBlock
              _id={shapeIdentificationId}
              canvasDimensions={dimensions}
              doesProbabilitiesExist={doesProbabilitiesExist}
              identifyCanvasContent={this.identifyCanvasContent}
            />
          </div>
          :
          <h2>Please draw in both fields identification.</h2>
        }
      </div>
    );
  }
};
