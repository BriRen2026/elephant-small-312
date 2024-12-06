let bckgrndImgs=[];

function preload() {
    bckgrndImgs.push(loadImage("static/images/baby-elephant.jpg"));
    bckgrndImgs.push(loadImage("static/images/cute-elephant.jpg"));
    bckgrndImgs.push(loadImage("static/images/elephant.png"));
    bckgrndImgs.push(loadImage("static/images/old-elephant.jpg"));
    bckgrndImgs.push(loadImage("static/images/phanpy.png"));
    bckgrndImgs.push(loadImage("static/images/playful-elephant.jpg"));
    bckgrndImgs.push(loadImage("static/images/scrungly-elephant.jpg"));
    bckgrndImgs.push(loadImage("static/images/sleek-mammoth.jpeg"));
}

preload();

console.log("in file"+bckgrndImgs);

function setup() {
    noLoop();
}