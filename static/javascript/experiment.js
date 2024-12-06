let bgi;
let changedTo;
let changed;
let all=new Map();
let e;
let o;

function preload() {
    bgi=loadImage("/static/images/sleek-mammoth.jpeg");
    e=loadImage("/static/images/elephant.png");
    o=loadImage("/static/images/old-elephant.jpg");
    all.set("http://localhost:8080/static/images/elephant.png",e);
    all.set("http://localhost:8080/static/images/old-elephant.jpg",o);
}

function setup() {
    createCanvas(350,350);
    let ca=document.getElementById("q5Canvas0");
    let lca=document.getElementById("target");
    lca.append(ca);
    background(bgi);
    changed=false;
}

function selectElephant(img) {
    let d=document.getElementById("grab");
    d.src=img.src;
}

function draw() {
    if (changed) {
        background(bgi);
        changed=false;
    }
    console.log("Draw :(");
    // setBackground();
}

function setBackground(img) {
    bgi=all.get(img.src);
    changed=true;
}

/*
so apparently the functionality of choosing images breaks everything whyyyyyyyyyyyyyyyyyy that doesn't make any senseeeeeeeeeeeeeeeeeee
appending to the div worked in the most basic form before i incorporated changing backgrounds
 */