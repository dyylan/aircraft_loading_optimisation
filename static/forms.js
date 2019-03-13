function sendForm(idForm, requestURL) {
    return new Promise(resolve => {
        let form = document.getElementById(idForm);
        let request = new XMLHttpRequest();
        request.open("POST", requestURL);
        request.onload = function () {
            if (this.status >= 200 && this.status < 300) {
                resolve(request.response);
            } else {
                reject({
                    status: this.status,
                    statusText: request.statusText
                });
            }
        }
        request.onerror = function () {
            reject({
                status: this.status,
                statusText: request.statusText
            }); 
        }
        request.send(new FormData(form));
    })
}

function resetMessages() {
    return fetch("/messages-reset")
}

function reloadMessages() {
    fetch("/messages")
    .then(function(response) {
        return response.json();
    })
    .then(function(messages) {            
        let ul = document.getElementById("flashed-messages");
        ul.innerHTML = "";
        for (let i=0; i<messages.length; i++) {
            let messageLi = document.createElement("li");
            messageLi.className = "flashed-message";
            messageText = document.createTextNode(messages[i]);
            messageLi.appendChild(messageText);
            ul.appendChild(messageLi);
        }
    })
}

function resetBlocks() {
    let stepOneBlocksDiv = document.getElementById("step-one-blocks");
    stepOneBlocksDiv.innerHTML = "";

    // Blocks in the correct order
    let stepTwoBlocksDiv = document.getElementById("step-two-blocks");
    stepTwoBlocksDiv.innerHTML = "";

    // Fuselage blocks row
    let fuselageDiv = document.getElementById("fuselage");
    fuselageDiv.innerHTML = "";
    
    // Fuselage numbering row
    let fuselageNumberingDiv = document.getElementById("fuselage-numbering");
    fuselageNumberingDiv.innerHTML = "";
}


async function validateForms() {
    await resetMessages();
    await sendForm("samples-form", "/forms/samples");
    await sendForm("cargo-form", "/forms/add-cargo");
    await sendForm("remove-form", "/forms/remove-cargo");
    await sendForm("params-form", "/forms/params");
    reloadMessages();
    resetBlocks()
    loadBlocks();
}