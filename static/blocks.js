function blockClassType(blockSize) {
    switch (blockSize) {    
        case 1.0: 
            className = "block type1";
            break;
        case 0.5:
            className = "block type2";
            break;
        case 2.0:
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


function generateFuselage(fuselageDiv, fuselageNumberingDiv, blocks, fuselageLength) {
    for (let section=0; section<fuselageLength; section++) {
        
        // Fuselage section for blocks
        let sectionDiv = document.createElement("td");
        sectionDiv.className = "fuselage-section";
        sectionDiv.id = "section-" + section
        fuselageDiv.appendChild(sectionDiv);
        
        // Section numbering      
        let sectionNumberingDiv = document.createElement("td");        
        sectionNumberingDiv.className = "fuselage-section-numbering";
        sectionNumberingDiv.innerHTML = String(section + 1);
        fuselageNumberingDiv.appendChild(sectionNumberingDiv);
        
        // Add blocks to the fuselage sections
        for (let i=0; i<blocks.length; i++) {
            let blockObj = blocks[i];
            if (blockObj.position == section && blockObj.size != 2.0) {        

                // Place the corresponding block in the fuselage
                let blockDiv = document.createElement("div");
                blockDiv.className = blockClassType(blockObj.size);
                blockDiv.className += " in-fuselage"
                blockDiv.innerHTML = "<font style='font-weight: bold;'>" + blockObj['long_name']+"</font><br>"+ blockObj['mass'] +"kg";
                blockDiv.style.cssFloat = "none"
                sectionDiv.appendChild(blockDiv); 
            }
            if (blockObj.position == section-1 && blockObj.size == 2.0) {

                // Place the previous section and delete the current section
                let blockDiv = document.createElement("div");
                blockDiv.className = blockClassType(blockObj.size);
                blockDiv.className += " in-fuselage"
                blockDiv.innerHTML = "<font style='font-weight: bold;'>" + blockObj['long_name']+"</font><br>"+ blockObj['mass'] +"kg";
                sectionDiv.remove(); 
                let prevSectionDiv = document.getElementById("section-"+(section-1));
                prevSectionDiv.colSpan = 2;
                prevSectionDiv.appendChild(blockDiv); 
            }
        }
    }
}


function loadBlocks() {
    let blocksDiv = document.getElementById("available-blocks");
    blocksDiv.innerHTML = "";
    fetch('/step-one/blocks')
    .then(function(response) {
        return response.json();
    })
    .then(function(blocks) {
        generateBlocks(blocksDiv, blocks);
    });
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
        blocksDiv.innerHTML = "";
        
        // List of cargo variables
        generateBlocks(blocksDiv, blocks);
        let calculatingDiv = document.getElementById("calculating-message-loading");
        calculatingDiv.innerHTML = "";
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
        
        // Blocks in the correct order
        let blocksDiv = document.getElementById("step-two-blocks");
        blocksDiv.innerHTML = "";
        generateBlocks(blocksDiv, blocks);

        // Fuselage blocks row
        let fuselageDiv = document.getElementById("fuselage");
        fuselageDiv.innerHTML = "";
        
        // Fuselage numbering row
        let fuselageNumberingDiv = document.getElementById("fuselage-numbering");
        fuselageNumberingDiv.innerHTML = "";
        
        // Fuselage section
        generateFuselage(fuselageDiv, fuselageNumberingDiv, blocks, parameters['fuselage_length']);
        
        // Remove calculating message 
        let calculatingDiv = document.getElementById("calculating-message-ordering");
        calculatingDiv.innerHTML = "";
    });
}


function optimiseForLoadedCargo() {
    let calculatingDiv = document.getElementById("calculating-message-loading");
    calculatingDiv.innerHTML = "Please wait whilst cargo selection is optimised for maximum load...";
    stepOne();
}


function optimiseForCargoOrder() {
    let calculatingDiv = document.getElementById("calculating-message-ordering");
    calculatingDiv.innerHTML = "Please wait whilst order is optimised for minimum turning effect around centre...";
    stepTwo();
}


loadBlocks();
