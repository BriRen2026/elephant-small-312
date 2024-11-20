let backgroundImg;
let bckgrndSrc;
let partyHatImage;
let partyhat;

function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
  ev.preventDefault();
  const data = ev.dataTransfer.getData("text");
  console.log(data);
}

function makeCanvasDroppable() {
    let canvas=document.getElementById("q5Canvas0");
    canvas.setAttribute("ondrop","drop(event)");
    canvas.setAttribute("ondragover","allowDrop(event)");
}

//establish all fashion images
//TBD: csv file of all fashion item names, script for processing into corresponding vars
function preload() {
    partyHatImage=loadImage("static/images/fashion/partyhat2.png");
}

function setBackground() {
    let bckgrnd=document.getElementById("elephant-pic").childNodes[0];
    bckgrndSrc=bckgrnd.src;
    backgroundImg=loadImage(bckgrndSrc);
    return backgroundImg;
}

//build canvas and establish sprites/vectors
function setup() {
    new Canvas(350,350);
    makeCanvasDroppable();
    rectMode(CENTER);
    allSprites.rotationLock=true;

    partyhat=new Sprite();
    partyhat.img=partyHatImage;
    partyhat.position=createVector(100,100);
    partyhat.drag=10;

}

//active game canvas functionality; set background and move sprites
function draw() {
    background(setBackground());

    if (partyhat.mouse.dragging()) {
        partyhat.moveTowards(mouse.x+partyhat.mouse.x,mouse.y+partyhat.mouse.y,1);
    }
}

