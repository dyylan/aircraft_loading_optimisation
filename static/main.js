// Fuselage object
class Fuselage {
    constructor(maxLength, maxWeight) {
        this.length = 0;
        this.maxLength = maxLength;
        this.blocks = [];
        this.maxWeight = maxWeight;
        this.weight = 0;
    }
    push(block) {
        this.length += block[0];
        this.weight += block[1];
        if (this.length > this.maxLength) {
            return -1;
        }
        else if (this.weight > this.maxWeight) {
            return -2;
        }
        else {
            this.blocks.push(block);
            return 1;
        }
    }
    pop() {
        poppedBlock = this.blocks.pop();
        this.weight -= poppedBlock[1];
        return poppedBlock;
    }
}


// Block objects
class Block {
    constructor(size, mass) {
        this.size = size;
        this.mass = mass;
        this.density = this.mass / this.size;
    }
}


// Globals
var fuselageLength = 9;
var maxWeight = 10;


function generateBlocks(divElement, blocksList) {
    for (let i=0; i<blocksList.length; i++) {
        let blockDiv = document.createElement("div");
        let blockObj = blocksList[i];              
        switch (blockObj.size) {
            case 1: 
                blockDiv.className = "block type1";
                break;
            case 0.5:
                blockDiv.className = "block type2";
                break;
            case 2:
                blockDiv.className = "block type3";
        };
        blockDiv.innerHTML = "<font style='font-weight: bold;'>" + blockObj['long_name']+"</font><br>"+ blockObj['mass'] +"kg";
        divElement.appendChild(blockDiv);
    };
}


fetch('/blocks')
    .then(function(response) {
        return response.json();
    })
    .then(function(blocks) {
        let blocksDiv = document.getElementById("available-blocks") 
        generateBlocks(blocksDiv, blocks)
    });

fetch('/optimisation')
    .then(function(response) {
        return response.json();
    })
    .then(function(optimisation) {
        let parameters = optimisation[0];
        let parametersDiv = document.getElementById("solution-parameters");
        parametersDiv.innerHTML = "<font style='font-weight: bold;'>Cargo mass: </font>" + parameters['cargo_mass'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Max load: </font>" + parameters['max_load'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Fuselage length: </font>" + parameters['fuselage_length'] + "<br>";
        parametersDiv.innerHTML += "<font style='font-weight: bold;'>Solution status: </font>" + parameters['status'] + "<br>";
        let blocks = optimisation[2];
        let blocksDiv = document.getElementById("solution-blocks");
        // List of cargo variables
        generateBlocks(blocksDiv, blocks)   
    });