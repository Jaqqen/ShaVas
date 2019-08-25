import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";
import MyCanvas from "./MyCanvas";

export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      canvasNamesWithInteraction: [],
      disableGenerateButton: false,
      identifyerCanvas: false,
      identifyerDrawing: null,
      interactionCounter: 0,
      myInterval: null,
      trainDrawings: [],
    };
    this.fetchIfNeuralNetwork = this.fetchIfNeuralNetwork.bind(this);
    // this.sendDataToBackend = this.sendDataToBackend.bind(this);
    this.registerCanvasInteractions = this.registerCanvasInteractions.bind(this);
    this.setIdentifyerDrawing = this.setIdentifyerDrawing.bind(this);
  }

  componentDidMount() {
    this.fetchClearDatalist();
    this.fetchIfNeuralNetwork();
  }

  componentDidUpdate() {
    // console.log('=============');
    // console.log('CURRENT STATE --- APP.JS', this.state);
    // console.log('=============');
  }

  componentWillUnmount() {
    console.log('App has unmounted');
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
        for (let i = 0; i < data.length; i++) {
          console.log('OK', data[i]);
        }
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
            disableGenerateButton: false,
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


    const obj = {
      'data0': canvas0,
      'data1': canvas1,
      'shape0': 'Shape 0',
      'shape1': 'Shape 1'
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
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        console.log('OK', data);
        this.setState({
          disableGenerateButton: true,
        });
        // this.getSample();
        this.generate();
      })
      .catch(error => console.log('ERROR', error));

  }

  // GET - GENERATE MORE DATA AND RECEIVE CONFIRMATION THAT SAMPLES
  // HAVE BEEN CREATED
  async generate() {
    await fetch('/generate')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        console.log('OK', data);
        const myInterval = setInterval(() => {
          this.getSample();
        }, 10000)
        this.setState({
          myInterval: myInterval
        });
      })
      .catch(error => console.log('ERROR', error))
  }

  // GET - SAMPLE OF THE DATA THAT IS BEING GENERATED
  async getSample() {
    await fetch('/getSample')
      .then(response => {
        if (response.ok) {
          return response.json();
        } else {
          throw new Error('Something went wrong ...');
        }
      })
      .then(data => {
        if (!data[0].samples_created) {
          console.log('OK - FALSE: ', data);

        } else {
          console.log('OK - TRUE: ', data);
          this.setState({
            identifyerCanvas: true,
          });
          clearInterval(this.state.myInterval);
        }
      })
      .catch(error => console.log('ERROR', error))
  }

  // POST - IDENTIFY THE DRAWING
  async identifyCanvasContent() {

    const obj = { 'dataI': this.state.identifyerDrawing }

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
        console.log(data);
        console.log('IDENTIFIED')
      })
      .catch(error => console.log('ERROR', error))
  }

  setIdentifyerDrawing(drawing) {
    this.setState({
      identifyerDrawing: drawing,
    }, () => this.identifyCanvasContent());
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

  render() {
    const { trainDrawings, identifyerCanvas } = this.state;
    const dimensions = { h: 300, w: 400 };

    return (
      <div>
        <h1>ShaVas</h1>
        <hr />
        <div>
          <div className="App">
            <CanvasBlock
              canvasDimensions={dimensions}
              idNumber={0}
              isIdentifyBlock={false}
              registerCanvasInteractions={this.registerCanvasInteractions}

            />
            <CanvasBlock
              canvasDimensions={dimensions}
              idNumber={1}
              isIdentifyBlock={false}
              registerCanvasInteractions={this.registerCanvasInteractions}
            />
          </div>
          <div id="generateButton">
            <button disabled={!this.allCanvasHaveContent()} type='button' onClick={this.sendDataToBackend}>
              {this.allCanvasHaveContent() ? 'Generate samples' : 'Please draw your shapes!'}
            </button>
          </div>
          <hr />
        </div>
        {trainDrawings.length > 1 && identifyerCanvas ?
          <div id="identifyer-container">
            <CanvasBlock setIdentifyerDrawing={this.setIdentifyerDrawing} idNumber={2} isIdentifyBlock={true}></CanvasBlock>
          </div>
          :
          <h2>Please draw in both fields identification.</h2>
        }
      </div>
    );
  }
};
