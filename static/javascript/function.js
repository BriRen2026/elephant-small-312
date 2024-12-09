//Submission stuff
const shadow2 = document.getElementById("shadow");
const submitDialog2 = document.getElementById("dialog-submit");
//Opens dialog boxes for form submissions

//Opens submit elephant dialog box
function openDialog2(){
	submitDialog2.style.display = "block";
	shadow2.style.display = "block";
	shadow2.style.visibility = "visible";
}

//saves canvas to dataURL and sets value of file in submit POST form (name="file")
// *backend eventually converts to byte array for file writing/stored path in sql
function saveCanvasToImage2() {
    let c=document.getElementById("defaultCanvas0");
    let cd=c.toDataURL('image/png');
    // console.log(cd);
    let ec=document.getElementById("elephantImg");
    ec.setAttribute("value",cd);
    // console.log("*** "+localStorage.getItem("cimg"));
    // console.log(ec.value);
}


function elephantSound(){
	const sound = new Audio("/static/elephant.mp3");
	sound.play();
}


function likeElephant(parent) {
	const parent2 = document.getElementById(parent);
	// console.log(parent)
	// console.log(parent2)
	//Button starts in unliked state.
	//button-like is the non-solid heart. When you click it, it should become the button-unlike so its in a state where you can unlike after liking
	let id = parent2.querySelector("#post_id").value
	// console.log(id)
	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Visually Increment the amount of likes
	let amountOfLikes = parent2.querySelector('#like-counter'); //Shows "<Num> Likes"
	let likes = amountOfLikes.innerHTML;
	// console.log("Likes:",likes);
	let likesArray = likes.split(" "); //Split on the space -> ["", "<Num>" "Likes"]
  	// console.log("Array: ",likesArray);
	let likeNum = likesArray[0];
	// console.log("Got Num: ",likeNum); // "<Num>"
	likeNum = parseInt(likeNum) + 1; //<Num> + 1
	// console.log("New LikeNum: ",likeNum);
  	amountOfLikes.innerHTML = likeNum+" Likes"; //Update javascript on front end

	//Get username of the liker and postID of the post liked
	let username = document.getElementById('header-user');
	const data = {"username": username.innerText, "id": id}; //id : id added by zane, sends the post ID
	const request = new XMLHttpRequest();
	request.open("POST", "like");
	request.send(JSON.stringify(data));

	//Change if heart is shown as liked or unliked
	like.style.display = "none";
	unlike.style.display = "block";
}

function unlikeElephant(parent){
	// console.log("Pressed Unlike Button");
	const parent2 = document.getElementById(parent);
	let id = parent2.querySelector("#post_id").value
	//Button starts in liked state.
	//button-unlike is the solid heart. When you click it, it should become button-like, as you put it into a state where it can be liked again after unliking

	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Decrement the amount of likes
	let amountOfLikes = parent2.querySelector('#like-counter');
	let likes = amountOfLikes.innerHTML;
	// console.log("Likes:",likes);
	//To string innerHTML
	let likesArray = likes.split(" "); //Split on the space -> ["", "<Num>" "Likes"]
  	// console.log("Array: ",likesArray);
	let likeNum = likesArray[0];
	// console.log("Got Num: ",likeNum); // "<Num>"
	likeNum = parseInt(likeNum) - 1; //<Num> + 1
	// console.log("New LikeNum: ",likeNum);
  	amountOfLikes.innerHTML = likeNum+" Likes"; //Update javascript on front end

	//Should remove the username from who has liked it
	let username = document.getElementById('header-user');
	const data = {"username": username.innerText, "id": id};
	const request = new XMLHttpRequest();
	request.open("POST", "unlike");
	request.send(JSON.stringify(data));

	//Change from liked state to unliked state
	like.style.display = "block";
	unlike.style.display = "none";
}


var count = 0;

function openDesc(parent){
	// console.log("Open Description: ",count);
	const parent2 = document.getElementById(parent);
	let hide = parent2.querySelector('#view-description');
	let description = parent2.querySelector('#description');

	//Show description of current elephant post
	description.style.display = "block";

	//Change button text to Close Description and consider cases where a desc has already closed & count will be 0
	if (hide.innerHTML === "Close Description"){
		count++;
	}
	hide.innerHTML = 'Close Description';

	//If it's clicked on again, set it back to normal
	hide.addEventListener("click", function(){
		if (hide.innerHTML === "Close Description"){
			if (count >= 1) {
				// console.log("Close Description: ",count);
				description.style.display = "none";
				hide.innerHTML = 'View Description';
				count=0;
			}
		}
	});

}

function iconHoverOver(element) {
	if (!element.src.includes("ele")) {
		element.setAttribute("style","opacity: 0.2");
	}
}

function iconHoverOff(element) {
	element.removeAttribute("style");
}

var commentsCount = 0;

function openComments(parent){
	// console.log("Open Comments: ",commentsCount);
	const parent2 = document.getElementById(parent);
	let hide = parent2.querySelector('#view-comments');
	let comments = parent2.querySelector('#comments');

	//Show comments of current elephant post
	comments.style.display = "block";

	//Change button text to Close Comments and consider cases where a desc has already closed & commentsCount will be 0
	if (hide.innerHTML === "Close Comments"){
		commentsCount++;
	}
	hide.innerHTML = 'Close Comments';

	//If it's clicked on again, set it back to normal
	hide.addEventListener("click", function(){
		if (hide.innerHTML === "Close Comments"){
			if (commentsCount >= 1) {
				// console.log("Close Comments: ",commentsCount);
				comments.style.display = "none";
				hide.innerHTML = 'View Comments';
				commentsCount=0;
			}
		}
	});

	// IMPORTANT (issue with this solution): requires duplicate ws connections on each tab opened
	// Connect to websocket and send live comment data to server-side
	// const socket = io({autoConnect: false});
	// let post = parent2.querySelector('#comment-button');
	// let idContainer = parent2.querySelector("#post_id")
	// let commentContainer = parent2.querySelector("#form-comment-message");
	//
	// post.addEventListener("click", function() {
	// 	let username = document.getElementById("header-user").textContent;
	// 	let postID = idContainer.value;
	// 	let comment = commentContainer.value;
	//
	// 	console.log("User " + username + " commented: " + comment);
	//
	// 	let commentData = {"username": username, "post_id": postID, "comment": comment};
	//
	// 	socket.connect();
	//
	// 	// Sends data in real time to 'commentData' socket route in app.py
	// 	socket.emit('commentData', JSON.stringify(commentData));
	// });
}

//sleep: Sleeper function to pause execution.
const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

//socketCreate: Creates socket connection when user enters lobby.
function socketCreate(){

	//Connect to server through web socket, sending username.
	const socket = io();
	let username = document.getElementById("header-user").innerText;
	socket.connect();
	socket.emit("create", JSON.stringify(username));

	//Show lobby screen and hide enter lobby button.
	document.getElementById("room").style.display = "block";
	document.getElementById("readyButton").style.display = "inline-block";
	document.getElementById("competeButton").style.display = "none";

	//Socket listens for "send user" -> update lobby.
	socket.on("sendUser", function(input) {

		let newUserList = JSON.parse(input["users"]);
		let allState = "READY"
		let count = 0

		let newUL = document.createElement("ul")
		let ul = document.getElementById("allUsers");

		for (let user in newUserList) {
			let state = newUserList[user];
			count = count + 1;

			if (state === "NOT READY"){
				allState = "NOT READY";
			}

			let li = document.createElement("li");
			li.appendChild(document.createTextNode(user + " is " + state));
			li.id = user;
			newUL.appendChild(li);
			newUL.id = "allUsers";
			ul.replaceWith(newUL);
			}

		ul.replaceWith(newUL);

		//If all players are ready and there are at least two players, start countdown timer to start party.
		if (allState === "READY" && count >= 2){
			socket.emit("startTimer");
		}

	})

	//Countdown Lobby Timer.
	socket.on("countdown", function(input){
		let timeElement = document.getElementById("timer");
		timeElement.innerText = JSON.parse(input);
	})

	//Countdown Dressing Timer.
	socket.on("countdownCompetition", function(input){
		let timeElement = document.getElementById("competitionTimer");
		timeElement.innerText = JSON.parse(input);
	})

	//Display Dressing Room.
	socket.on("sendFashionMaker", function(input){
		document.getElementById("maker").style.display = "flex";
		document.getElementById("room").style.display = "none";
		document.getElementById("timer").style.display = "none";
		document.getElementById("competitionTimer").style.display = "block";
		document.getElementById("readyButton").style.display = "none";
		socket.emit("startCompetition")
	})

	//Listens for the readyButton to be clicked. When clicked, it updates the lobby for all users.
	document.getElementById("readyButton").addEventListener("click", function() {
		state = document.getElementById("readyButton").innerText;

		if (state === "READY") {
		socket.emit("userReady", username, "READY");
	}
		document.getElementById("readyButton").className = "unready-button";
		document.getElementById("readyButton").innerText = "WAITING"
	})

	//Ends dressing and forces user to update description and submit to feed. After, client sends an indication of finish to server.
	socket.on("submitForCompetition", function(input){
		 openDialog2();
		 saveCanvasToImage2();
		 document.getElementById("outfit-button-submit").addEventListener("click", function (){
			 // console.log("submit")
			 socket.emit("collectUsers")
		 })

	})

	//If there is a party game in progress, a user is forced to wait until it is over.
	socket.on("wait", async function(){
		document.getElementById("readyButton").className = "unready-button";
		document.getElementById("readyButton").innerText = "Please Wait! Game in progress!"
		await sleep(2000)
		document.getElementById("readyButton").className = "ready-button";
		document.getElementById("readyButton").innerText = "READY"
	})

}