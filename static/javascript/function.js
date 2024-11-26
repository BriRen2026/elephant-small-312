

function elephantSound(){
	const sound = new Audio("/static/elephant.mp3");
	sound.play();
}


function likeElephant(parent) {
	const parent2 = document.getElementById(parent);
	console.log(parent)
	console.log(parent2)
	//Button starts in unlike state.
	//button-like is the non-solid heart. When you click it, it should become the button-unlike so its in a state where you can unlike after liking
	let id = parent2.querySelector("#post_id").value
	console.log(id)
	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Visually Increment the amount of likes
	let amountOfLikes = parent2.querySelector('#like-counter'); //Shows "<Num> Likes"
	let likes = amountOfLikes.innerHTML;
	console.log("Likes: ",likes);
	let likesArray = likes.split(" "); //Split on the space -> ["", "<Num>" "Likes"]
  	console.log("Array: ",likesArray);
	let likeNum = likesArray[0];
	console.log("Got Num: ",likeNum); // "<Num>"
	likeNum = parseInt(likeNum) + 1; //<Num> + 1
	console.log("New LikeNum: ",likeNum);
  	amountOfLikes.innerHTML = likeNum+" Likes"; //Update javascript on front end

	//Keep track of who has liked posts
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
	console.log("Pressed Unlike Button");
	const parent2 = document.getElementById(parent);
	let id = parent2.querySelector("#post_id").value
	//Button starts in liked state.
	//button-unlike is the solid heart. When you click it, it should become button-like, as you put it into a state where it can be liked again after unliking

	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Decrement the amount of likes
	let amountOfLikes = parent2.querySelector('#like-counter');
	let likes = amountOfLikes.innerHTML;
	console.log("Likes: ",likes);
	//To string innerHTML
	let likesArray = likes.split(" "); //Split on the space -> ["", "<Num>" "Likes"]
  	console.log("Array: ",likesArray);
	let likeNum = likesArray[0];
	console.log("Got Num: ",likeNum); // "<Num>"
	likeNum = parseInt(likeNum) - 1; //<Num> + 1
	console.log("New LikeNum: ",likeNum);
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
	console.log("Open Description: ",count);
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
				console.log("Close Description: ",count);
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
	console.log("Open Comments: ",commentsCount);
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
				console.log("Close Comments: ",commentsCount);
				comments.style.display = "none";
				hide.innerHTML = 'View Comments';
				commentsCount=0;
			}
		}
	});

}
