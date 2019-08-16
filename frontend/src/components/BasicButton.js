import React from "react";

export const BasicButton = (props) => {
  const { buttonName, buttonType, disabledState, onClick } = props;

  return (
    <React.Fragment>
      <button disabled={disabledState} type={buttonType} onClick={onClick}>
        {buttonName}
      </button>
    </React.Fragment>
  );
}
