import React, { Component } from 'react'
import { BasicButton } from "./BasicButton";


export default class CanvasButtonGrp extends Component {
  constructor(props) {
    super(props);
    this.state = {
      disabledState: false
    }
    this.disableButtonWhenSetting = this.disableButtonWhenSetting.bind(this);
  }

  disableButtonWhenSetting(setDrawingFunction) {
    setDrawingFunction();
    this.setState({
      disabledState: true,
    });
  }


  render() {
    const { setDrawingFunction, clearFunction } = this.props;

    return (
      <React.Fragment>
        <BasicButton
          buttonName={this.state.disabledState ? "Drawing has been set" : "Set drawing"}
          buttonType={"button"}
          disabledState={this.state.disabledState}
          onClick={() => this.disableButtonWhenSetting(setDrawingFunction)}
        />
        <BasicButton
          buttonName={this.state.disabledState ? "Clear disabled" : "Clear"}
          buttonType={"button"}
          disabledState={this.state.disabledState}
          onClick={clearFunction}
        />
      </React.Fragment>
    )
  }
}
