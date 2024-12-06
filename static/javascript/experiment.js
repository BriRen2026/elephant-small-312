// let bgi;
// let changedTo;
// let changed;
// let all=new Map();
// let e;
// let o;
//
// function preload() {
//     bgi=loadImage("/static/images/sleek-mammoth.jpeg");
//     e=loadImage("/static/images/elephant.png");
//     o=loadImage("/static/images/old-elephant.jpg");
//     all.set("http://localhost:8080/static/images/elephant.png",e);
//     all.set("http://localhost:8080/static/images/old-elephant.jpg",o);
// }
//
// function setup() {
//     createCanvas(350,350);
//     let ca=document.getElementById("q5Canvas0");
//     let lca=document.getElementById("target");
//     lca.append(ca);
//     background(bgi);
//     changed=false;
// }
//
// function selectElephant(img) {
//     let d=document.getElementById("grab");
//     d.src=img.src;
// }
//
// function draw() {
//     if (changed) {
//         background(bgi);
//         changed=false;
//     }
//     console.log("Draw :(");
//     // setBackground();
// }
//
// function setBackground(img) {
//     bgi=all.get(img.src);
//     changed=true;
// }
//

let i;
let e;
let o;
let changed;
let allBckgrnds=new Map();


function preload() {
    i=loadImage("/static/images/sleek-mammoth.jpeg");
    e=loadImage("/static/images/elephant.png");
    allBckgrnds.set("static/images/elephant.png",e);
    o=loadImage("/static/images/old-elephant.jpg");
    allBckgrnds.set("static/images/old-elephant.jpg",o);
}

function setup() {
    createCanvas(350,350);
}

function draw() {
    console.log("draw happens");
    // clear();
    if (changed) {
        changed=false;
        image(i,0,0);
    }
    setBackground();
}

function setBackground() {
    let bckgrnd=document.getElementById("grab");
    let fragments=bckgrnd.src.split("http://localhost:8080/");
    i=allBckgrnds.get(fragments[1]);
    changed=true;
}

function change(ixx) {
    document.getElementById("grab").src=ixx.src;
}
