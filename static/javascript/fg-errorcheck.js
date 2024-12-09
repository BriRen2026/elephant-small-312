let backgroundImg;
let bckgrndSrc;
let spriteIcons=new Map(); //maps sprites to icon index
let iconSprites=new Map(); //maps icon indices (as strings) to sprites
let currSprite;
let iconCol=document.getElementById("item-list"); //all sidebar icons for fashion items
let spriteCount=1;

// for (let [spriteo,coords] of sprites) {
//     let sprite=new Sprite(sprites.get(spriteo)[0],sprites.get(spriteo)[1]);
//     sprite.img=spriteo.img;
//     sprite.position=createVector(sprites.get(spriteo)[0],sprites.get(spriteo)[1]);
//     sprite.drag=10;
//     sprite.collider="kinematic";
//     sprites.set(sprite,[sprites.get(spriteo)[0],sprites.get(spriteo)[1]]);
// }
let one, two, three, four, five, six, seven, eight;
let currBckg;
function preload() {
    one=loadImage("static/images/elephant.png");
    two=loadImage("static/images/old-elephant.jpg");
    three=loadImage("static/images/phanpy.png");
}
four=null;
five=null;
six=null;
seven=null;
eight=null;

//make canvas droppable
function allowDrop(ev) {
  ev.preventDefault();
}

//set current sprite to smaller icon form of fashion item for correct sizing
//this is a manual override for failed p5play sprite scaling functionality
function drag(ev, id) {
    ev.dataTransfer.setData("text", ev.currentTarget.id);
    currSprite=document.getElementById(document.getElementById(id).id+"-icon");
    // console.log(currSprite);
}

//drops a sprite on canvas if count of fashion items (10) has not been exceeded
//maps highest available icon slot for item deletion
//alerts user when they have added too many fashion items
function canvasDrop() {
    // console.log("!!!! "+spriteCount);
    if (spriteCount<=10) {
        // console.log("why are we here");
        //  console.log("X="+mouse.x);
        // console.log("Y="+mouse.y);
        let sprite=new Sprite(150,150);
        sprite.img=loadImage(currSprite.src);
        // console.log("SPRITE IMG "+sprite.img);
        sprite.position=createVector(150,150);
        sprite.drag=10;
        sprite.collider="kinematic";
        spriteCount++;
        let i=0;
        for (let icon of iconCol.children) {
            if (icon.childNodes[0].src.includes("ele")) {
                icon.childNodes[0].src=currSprite.src;
                spriteIcons.set(sprite,i);
                iconSprites.set(icon.childNodes[0].id,sprite);
                break;
            }
            i++;
        }
    } else {
        alert("Your elephant is too fashionable!");
    }
}

//drop action for item; invokes actual canvasDrop function
function drop(ev) {
  ev.preventDefault();
  const data = ev.dataTransfer.getData("text");
  // console.log("data!");
  // console.log(data);
  canvasDrop();
}

//after canvas tag is created on page load, allow drop & dragover
function makeCanvasDroppable() {
    let canvas=document.getElementById("q5Canvas0");
    canvas.setAttribute("ondrop","drop(event)");
    canvas.setAttribute("ondragover","allowDrop(event)");
}

//set background image for canvas based on elephant that has been selected
function setBackground(el) {
    // //console.log(document.getElementById("elephant-pic-src"));
    // let bckgrnd=document.getElementById("elephant-pic-src").childNodes[0];
    // // console.log("bckgrnd "+bckgrnd);
    // bckgrndSrc=bckgrnd.src;
    // backgroundImg=loadImage(bckgrndSrc);
    // return backgroundImg;
    // console.log(el);
    // console.log(el.src);
    let es=el.src;
    if (es.includes("/e")) {
        currBckg=one;
        // console.log(currBckg);
    } else if (es.includes("/o")) {
        currBckg=two;
        // console.log(currBckg);
    } else if (es.includes("/ph")) {
        currBckg=three;
        // console.log(currBckg);
    }
}

//build canvas and place in correct column on elephant maker page
//invokes makeCanvasDroppable so that canvasDrop works
function setup() {
    // console.log(one.get());
    // console.log(two.get());
    // console.log(three.get());
    // console.log("^");
    createCanvas(350,350);
    frameRate(60);
    noLoop();
    let canvLocation=document.getElementById("forCanvas");
    let canvas=document.getElementById("q5Canvas0");
    canvLocation.append(canvas);
    makeCanvasDroppable();
    rectMode(CENTER);
    allSprites.rotationLock=true;
    one.resize(350,350);
    two.resize(350,350);
    three.resize(350,350);
    currBckg=one;
    startLoop();
    // console.log("setup happens");
    // console.log(allSprites);
}

// function restoreCanvas() {
//     //console.log("restore");
//     //console.log(sprites);
//     background(setBackground());
//     for (let [key,coords] of sprites) {
//         let sprite=new Sprite(coords[0],coords[1]);
//         sprite.img=loadImage(currSprite.src);
//         sprite.position=createVector(coords[0],coords[1]);
//         sprite.drag=10;
//         sprite.collider="kinematic";
//     }
// }

//active game canvas functionality; set background (allows updates) and move sprites
//checks for move out of bounds and updates maps accordingly
function draw() {
    background(currBckg);
    // console.log(allSprites);
    for (let sprite of allSprites) {
        // console.log("hello sprite");
        sprite.update();
        sprite.draw();
        // console.log("for");
        //console.log(sprite);
        if (sprite.mouseIsPressed) {
            // console.log("SPRITE IS BEING DRAGGED!!!");
            sprite.moveTowards(mouse.x+sprite.mouse.x,mouse.y+sprite.mouse.y,1);
            sprite.update();
        } else {
            sprite.velocity.x=0;
            sprite.velocity.y=0;
        }
        if (sprite.x>350 || sprite.y>350) {
            // console.log("out of bounds");
            iconCol.children.item(spriteIcons.get(sprite)).childNodes[0].src="/static/images/elephant-small.jpg";
            iconSprites.delete(spriteIcons.get(sprite).toString());
            spriteIcons.delete(sprite);
            spriteCount--;
            // console.log("!!!! "+spriteCount);
        }
    }
}

function custLoop() {
    draw();
    requestAnimationFrame(custLoop);
}

function startLoop() {
    custLoop();
}


//when corresponding sidebar icon is clicked, delete the sprite from the canvas and open new sidebar slot
function deleteViaIcon(element) {
    //console.log("deleteviaicon happens");
    element.src="/static/images/elephant-small.jpg";
    let removedSprite=iconSprites.get(element.id);
    // console.log(removedSprite);
    // console.log(iconSprites);
    spriteIcons.delete(removedSprite);
    removedSprite.remove();
    iconSprites.delete(element.id);
    spriteCount--;
}

//this does work but not what I'm looking for
// function lameSave() {
//     let c=document.getElementById("q5Canvas0");
//     let data=c.toDataURL();
//     let ael=document.createElement("a");
//     ael.href=data;
//     ael.download="testimg.png";
//     ael.click();
// }

//also works but doesn't do what I want it to
// function betterSave() {
//     console.log("in better save");
//     let dataURI=document.getElementById("q5Canvas0").toDataURL();
//     let check=document.getElementById("checkCanvas");
//     check.src=dataURI;
// }

//this was so tragically close to working thank you JS blob security
// function bestSave() {
//     let finalBlob=uriToBlob();
//     let url=URL.createObjectURL(finalBlob);
//     // let canvas2=document.getElementById("checkCanvas");
//     // canvas2.src=url;
//     // console.log(canvas2.src);
//     localStorage.setItem("blobURL",url);
//     document.getElementById("elephantImg").setAttribute("value",localStorage.getItem("blobURL"));
// }
//
// function uriToBlob() {
//     let uri=document.getElementById("q5Canvas0").toDataURL();
//     let byteStr=atob(uri.split(',')[1]);
//     let mimeStr=uri.split(',')[0].split(':')[1].split(';')[0];
//     let arrayBuf=new ArrayBuffer(byteStr.length);
//     let intArr=new Uint8Array(arrayBuf);
//     for (let i=0; i<byteStr.length; i++) {
//         intArr[i]=byteStr.charCodeAt(i);
//     }
//     // console.log("blob! "+blob);
//     return new Blob([arrayBuf], {type: mimeStr});
// }

//saves canvas to dataURL and sets value of file in submit POST form (name="file")
// *backend eventually converts to byte array for file writing/stored path in sql
function saveCanvasToImage() {
    let c=document.getElementById("q5Canvas0");
    let cd=c.toDataURL('image/png');
    // console.log(cd);
    let ec=document.getElementById("elephantImg");
    ec.setAttribute("value",cd);
    // console.log("*** "+localStorage.getItem("cimg"));
    // console.log(ec.value);
}