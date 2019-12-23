/**
 * * This is used when an error is thrown while fetching.
 * * It contains the error Message and the function name of the current fetch process.
 * 
 * @param errorMessage 
 * @param fetchFunctionName 
 */
export const catchErrorOnFetch = (errorMessage, fetchFunctionName) => {
    console.log('Error - ' + fetchFunctionName, errorMessage);
};

/**
 * * This checks the response and if it has an 'ok' property than the response is fine and can be
 * * returned for further use-cases.
 * * Else and error is thrown with the current function name in it.
 * 
 * @param response          the response that is being passed from the request
 * @param fetchFunctionName just a name to be recorded in the error message
 */
export const checkStatus = (response, fetchFunctionName) => {
    if (response['ok']) { return response.json(); }
    else {
        const error = new Error(fetchFunctionName + ': ', response.statusText);
        error.response = response;
        throw error;
    }
};

/**
 * * This Service is a template for rest requests in this application.
 * * The get-property sends a GET-request and returns data by only using the path.
 * * The post-property sends a POST-request and returns data by using the path and an object.
 * 
 * @param path              the path to use for the corresponding request
 * @param fetchFunctionName a simple name for the checkStatus-function
 * @param dataFunction      the function to use when the data-object is being resceived
 * @param obj               the object that than is transfered to the postSettings-function and then
 *                          is used in the POST-request
 */
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

/**
 * * This builds an json-type Object with the bodyOfObject-prop as its body-content.
 * 
 * @param bodyOfObject an Object of any size or type
 */
export const postSettings = bodyOfObject => {
    return {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(bodyOfObject)
    }
}