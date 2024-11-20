let backgroundSM;
let partyHatImage;
let partyhat;

//establish images
function preload() {
    //let bckgrndSrc=document.getElementById("")
    backgroundSM=loadImage("static/images/sleek-mammoth.jpeg");
    partyHatImage=loadImage("static/images/fashion/partyhat.jpg");
}

//build canvas and establish sprites/vectors
function setup() {
    new Canvas(350,350);
    rectMode(CENTER);
    allSprites.rotationLock=true;

    partyhat=new Sprite();
    partyhat.img=partyHatImage;
    partyhat.position=createVector(100,100);
    partyhat.drag=10;

}


//active game canvas functionality; set background and move sprites
function draw() {
    background(backgroundSM);

    if (partyhat.mouse.dragging()) {
        partyhat.moveTowards(mouse.x+partyhat.mouse.x,mouse.y+partyhat.mouse.y,1);
    }
}

