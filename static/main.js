function blockClassType(blockSize) {
    switch (blockSize) {    
        case 1: 
            className = "block type1";
            break;
        case 0.5:
            className = "block type2";
            break;
        case 2:
            className = "block type3";
    }
    return className
}


function generateBlocks(divElement, blocksList) {
    for (let i=0; i<blocksList.length; i++) {
        let blockDiv = document.createElement("div");
        let blockObj = blocksList[i];              
        blockDiv.className = blockClassType(blockObj.size)
        blockDiv.innerHTML = "<font style='font-weight: bold;'>" + blockObj['long_name']+"</font><br>"+ blockObj['mass'] +"kg";
        divElement.appendChild(blockDiv);
    }
}


function generateFuselage(divElement, blocks, fuselageLength) {
    for (let section=0; section<fuselageLength; section++) {
        let sectionDiv = document.createElement("div");
        sectionDiv.className = "fuselage-section";
        divElement.appendChild(sectionDiv);
        for (let i=0; i<blocks.length; i++) {
            let blockObj = blocks[i];
            if (blockObj.position == section) {
                let blockDiv = document.createElement("div");
                blockDiv.className = blockClassType(blockObj.size);
                blockDiv.innerHTML = "<font style='font-weight: bold;'>" + blockObj['long_name']+"</font><br>"+ blockObj['mass'] +"kg";
                sectionDiv.appendChild(blockDiv);
            }
        }
    }
}


function stepOne() {
   fetch('/step-one/optimisation')
    .then(function(response) {
        return response.json();
    })
    .then(function(optimisation) {
        let parameters = optimisation[0];
        let parametersDiv = document.getElementById("step-one-parameters");
        parametersDiv.innerHTML = "<font style='font-weight: bold;'>Cargo mass: </font>" + parameters['cargo_mass'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Max load: </font>" + parameters['max_load'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Fuselage length: </font>" + parameters['fuselage_length'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Solution status: </font>" + parameters['status'] + "<br>";
        let blocks = optimisation[2];
        let blocksDiv = document.getElementById("step-one-blocks");
        // List of cargo variables
        generateBlocks(blocksDiv, blocks);
    }); 
}


function stepTwo() {
    fetch('/step-two/optimisation')
    .then(function(response) {
        return response.json();
    })
    .then(function(optimisation) {
        let parameters = optimisation[0];
        let parametersDiv = document.getElementById("step-two-parameters");
        parametersDiv.innerHTML = "<font style='font-weight: bold;'>Turning effect: </font>" + parameters['turning_effect'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Max load: </font>" + parameters['max_load'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Fuselage length: </font>" + parameters['fuselage_length'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Solution status: </font>" + parameters['status'] + "<br>";
        let blocks = optimisation[3];
        let blocksDiv = document.getElementById("step-two-blocks");
        let fuselageDiv = document.getElementById("fuselage");
        // List of cargo variables
        generateBlocks(blocksDiv, blocks);
        generateFuselage(fuselageDiv, blocks, parameters['fuselage_length']);
        let calculatingDiv = document.getElementById("calculating-message");
        calculatingDiv.innerHTML = "";
    });
}


function optimiseForLoadedCargo() {
    stepOne();
}

function optimiseForCargoOrder() {
    let calculatingDiv = document.getElementById("calculating-message");
    calculatingDiv.innerHTML = "Please wait whilst order is optimised for minimum turning effect around centre...";
    stepTwo();
}


fetch('/step-one/blocks')
    .then(function(response) {
        return response.json();
    })
    .then(function(blocks) {
        let blocksDiv = document.getElementById("available-blocks") 
        generateBlocks(blocksDiv, blocks)
    });


