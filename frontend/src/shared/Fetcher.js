export const catchErrorOnFetch = (errorMessage, fetchFunctionName) => {
    console.log('Error - ' + fetchFunctionName, errorMessage);
};

export const checkStatus = (response, fetchFunctionName) => {
    if (response['ok']) { return response.json(); }
    else {
        const error = new Error(fetchFunctionName + ': ', response.statusText);
        error.response = response;
        throw error;
    }
};

export const FetchService = {
    get: async (path, fetchFunctionName, dataFunction) => {
        await fetch(path)
            .then(response => checkStatus(response, fetchFunctionName))
            .then(data => dataFunction(data))
            .catch(error => catchErrorOnFetch(error, fetchFunctionName));
    },
    post: async (path, obj, fetchFunctionName, dataFunction) => {
        await fetch(path, postSettings(obj))
            .then(response => checkStatus(response, fetchFunctionName))
            .then(data => dataFunction(data))
            .catch(error => catchErrorOnFetch(error, fetchFunctionName));
    },
}

export const postSettings = bodyObject => {
    return {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(bodyObject)
    }
}