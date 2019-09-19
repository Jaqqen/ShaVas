import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";

export default class App extends Component {
  constructor(props) {
    super(props);
    this.initState = {
      canvasNamesWithInteraction: [],
      identifyerCanvas: false,
      isGenerating: false,
      myInterval: null,
    };
    this.state = { ...this.initState }
    this.fetchIfNeuralNetwork = this.fetchIfNeuralNetwork.bind(this);
    this.getSample = this.getSample.bind(this);
    this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
    this.resetInputLogic = this.resetInputLogic.bind(this);
    this.sendDataToBackend = this.sendDataToBackend.bind(this);
    this.getRootStateWhenMyCanvasUnmount = this.getRootStateWhenMyCanvasUnmount.bind(this);
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
            identifyerCanvas: false,
          });
        }
      })
      .catch(error => console.log('Error', error))
  }

  // POST - DATA TO BACKEND
  async sendDataToBackend() {
    const canvas0 = document.getElementById('my-canvas0').getContext('2d')['canvas'].toDataURL('image/png');
    const canvas1 = document.getElementById('my-canvas1').getContext('2d')['canvas'].toDataURL('image/png');

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
            identifyerCanvas: true,
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
      .getElementById('my-canvas2').getContext('2d')['canvas'].toDataURL('image/png');

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
          console.log('>> IDENTIFIED - 0-0 ', data[0][0]);
        } catch (e) {
          console.log('<< NOT IDENTIFED - 0');
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
    if (canvasNamesWithInteraction.includes('Canvas0') && canvasNamesWithInteraction.includes('Canvas1')) {
      return true;
    } else {
      return false;
    }
  }

  resetInputLogic() {
    this.setState({ ...this.initState })
  }

  getRootStateWhenMyCanvasUnmount() {
    console.log(this.state);
  }

  render() {
    const dimensions = { h: 300, w: 400 };

    const { identifyerCanvas, isGenerating } = this.state;

    return (
      <div>
        <h1>ShaVas</h1>
        <hr />
        <div>
          <div className="App">
            <CanvasBlock
              canvasDimensions={dimensions}
              constructionCompleted={identifyerCanvas}
              idNumber={0}
              isGenerating={isGenerating}
              isIdentifyBlock={false}
              registerCanvasInteractions={this.registerCanvasInteractions}
              resetInputLogic={this.resetInputLogic}

            />
            <CanvasBlock
              canvasDimensions={dimensions}
              constructionCompleted={identifyerCanvas}
              idNumber={1}
              isGenerating={isGenerating}
              isIdentifyBlock={false}
              registerCanvasInteractions={this.registerCanvasInteractions}
              resetInputLogic={this.resetInputLogic}
            />
          </div>
          <div id="generateButton">
            <button
              disabled={!this.allCanvasHaveContent() || identifyerCanvas || isGenerating}
              type='button'
              onClick={this.sendDataToBackend}>
              {this.allCanvasHaveContent() ?
                isGenerating ?
                  'Generating samples and Neural Network'
                  :
                  identifyerCanvas ?
                    'Complete'
                    :
                    'Generate samples'
                :
                'Please draw your shapes!'}
            </button>
          </div>
          <hr />
        </div>
        {identifyerCanvas ?
          <div id="identifyer-container">
            <CanvasBlock
              canvasDimensions={dimensions}
              getRootStateWhenMyCanvasUnmount={this.getRootStateWhenMyCanvasUnmount}
              idNumber={2}
              isIdentifyBlock={true}
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
