function elephantSound(){
	const sound = new Audio("/static/elephant.mp3");
	sound.play();
}


function likeElephant(parent){
	console.log("Pressed Like Button");
	const parent2 = document.getElementById(parent);
	//Button starts in unlike state.
	//button-like is the non-solid heart. When you click it, it should become the button-unlike so its in a state where you can unlike after liking

	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Should increment amount of likes whenever we have that set up...
	let amountOfLikes = parent2.querySelector('#like-counter');

	like.style.display = "none";
	unlike.style.display = "block";
}

function unlikeElephant(parent){
	console.log("Pressed Unlike Button");
	const parent2 = document.getElementById(parent);
	//Button starts in liked state.
	//button-unlike is the solid heart. When you click it, it should become button-like, as you put it into a state where it can be liked again after unliking

	let like = parent2.querySelector('.button-like');
	let unlike = parent2.querySelector('.button-unlike');

	//Should increment amount of likes whenever we have that set up...
	let amountOfLikes = parent2.querySelector('#like-counter');

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
