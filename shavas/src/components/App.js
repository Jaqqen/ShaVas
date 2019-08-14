import React, { Component } from "react";
import "./../static/App.css";
import CanvasBlock from "./CanvasBlock";

export default class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      trainDrawings: [],
      identifyerDrawing: null,
      disableGenerateButton: false,
      identifyerCanvas: false,
      myInterval: null,
    };
    this.appendDrawingToState = this.appendDrawingToState.bind(this);
    this.fetchIfNeuralNetwork = this.fetchIfNeuralNetwork.bind(this);
    this.sendDataToBackend = this.sendDataToBackend.bind(this);
    this.setIdentifyerDrawing = this.setIdentifyerDrawing.bind(this);
  }

  appendDrawingToState(canvasDataURL) {
    this.setState(prevState => ({
      trainDrawings: [...prevState.trainDrawings, canvasDataURL]
    }));
  }

  componentDidMount() {
    this.fetchClearDatalist();
    this.fetchIfNeuralNetwork();
  }

  componentDidUpdate() {
    console.log('trainDrawings', this.state);
  }

  componentWillUnmount() {
    console.log('App has unmounted');
  }

  // GET
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

  // GET
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

  // POST
  async sendDataToBackend() {
    if (!(this.state.trainDrawings.length > 1)) {
      alert('Please set both drawings before generating data!')
    }

    const obj = {
      'data0': this.state.trainDrawings[0],
      'data1': this.state.trainDrawings[1],
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
      .catch(error => console.log('ERROR', error))
  }

  // GET
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

  render() {
    const { disableGenerateButton, trainDrawings, identifyerCanvas } = this.state;

    return (
      <div>
        <h1>ShaVas</h1>
        <hr />
        {identifyerCanvas === false ?
          <React.Fragment>
            <div className="App">
              <CanvasBlock
                appendDrawingToState={this.appendDrawingToState}
                identifyer={false}
                idNumber={0}
              />
              <CanvasBlock
                appendDrawingToState={this.appendDrawingToState}
                identifyer={false}
                idNumber={1}
              />
            </div>
            <div id="generateButton">
              <button disabled={disableGenerateButton} type='button' onClick={this.sendDataToBackend}>
                {disableGenerateButton === false ?
                  trainDrawings.length === 2 ? 'Generate and train data!' : 'Please set drawings!'
                  :
                  identifyerCanvas === false ? 'Generating, calculating...' : 'Computing complete'
                }
              </button>
            </div>
            <hr />
          </React.Fragment>
          :
          <React.Fragment></React.Fragment>
        }
        {trainDrawings.length > 1 && identifyerCanvas ?
          <div id="identifyer-container">
            <CanvasBlock setIdentifyerDrawing={this.setIdentifyerDrawing} idNumber={2} identifyer={true}></CanvasBlock>
          </div>
          :
          <h2>Please set both drawings before identification.</h2>
        }
      </div>
    );
  }
};
