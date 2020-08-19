import React from 'react';

export const instructionsWrapper = (instructionsClassName, _text) => {
    return (
        <div className={instructionsClassName}>
            <div className="strikIn-instructions">
                <p className="instructions-text">
                    <b style={{ fontSize: '1.6em' }}>{_text}</b>
                </p>
            </div>
    </div>
)};

export const getHighlightedText = (text) => {
    return instructionsWrapper('instructions', text);
}

export const getFinishingHighlightedText = (text) => {
    return instructionsWrapper('instructions-finish', text);
}

export const getLoadingHighlightedText = (text) => {
    return instructionsWrapper('loading-process instructions-loading', text);
}