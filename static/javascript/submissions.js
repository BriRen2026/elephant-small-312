
//Submission stuff
const shadow = document.getElementById("shadow");
const submitDialog = document.getElementById("dialog-submit");
//Opens dialog boxes for form submissions

//Opens submit elephant dialog box
function openDialog(){
	submitDialog.style.display = "block";
	shadow.style.display = "block";
	shadow.style.visibility = "visible";
}

//Closes submit elephant dialog box
function closeDialog(){
	submitDialog.style.display = "none";
	shadow.style.display = "none;"
	shadow.style.visibility = "hidden";
}

//Elephant filter stuff

const elephants = document.getElementById("elephant-selector");
const headacc = document.getElementById("head-selector");
const trunkacc=document.getElementById("trunk-selector");
const bodyacc=document.getElementById("body-selector");
const shoeacc=document.getElementById("shoe-selector");
const accacc=document.getElementById("accessory-selector");

function elephantSelector(){
	console.log("Show elephants");
	elephants.style.display = "block";
	headacc.style.display = "none";
	trunkacc.style.display = "none";
	bodyacc.style.display = "none";
	shoeacc.style.display = "none";
	accacc.style.display = "none";
}

function headSelector(){
	console.log("Show heads");
	elephants.style.display = "none";
	headacc.style.display = "block";
	trunkacc.style.display = "none";
	bodyacc.style.display = "none";
	shoeacc.style.display = "none";
	accacc.style.display = "none";
}

function trunkSelector(){
	console.log("Show trunk");
	elephants.style.display = "none";
	headacc.style.display = "none";
	trunkacc.style.display = "block";
	bodyacc.style.display = "none";
	shoeacc.style.display = "none";
	accacc.style.display = "none";
}

function bodySelector(){
	console.log("Show body");
	elephants.style.display = "none";
	headacc.style.display = "none";
	trunkacc.style.display = "none";
	bodyacc.style.display = "block";
	shoeacc.style.display = "none";
	accacc.style.display = "none";
}

function shoeSelector(){
	console.log("Show shoes");
	elephants.style.display = "none";
	headacc.style.display = "none";
	trunkacc.style.display = "none";
	bodyacc.style.display = "none";
	shoeacc.style.display = "block";
	accacc.style.display = "none";
}

function accessorySelector(){
	console.log("Show accessories");
	elephants.style.display = "none";
	headacc.style.display = "none";
	trunkacc.style.display = "none";
	bodyacc.style.display = "none";
	shoeacc.style.display = "none";
	accacc.style.display = "block";
}

//Actually choosing an elephant to dress up
function selectElephant(img){
	//Change the img source for our elephant-pic img
	// const elephantpic = document.getElementById("elephant-pic-src");
	// const submitForm = document.forms["elephant-submit-form"]
	// const saveForm = document.forms["elephant-save-form"]
	//
	// //Changes the Big Selected elephant image to whatever a user selects
	// const changeYourElephantPic = elephantpic.childNodes[0]
	// const changeToThis = div.childNodes[0]
	//
	// //Change Your Elephant source to whatever the user selected
	// changeYourElephantPic.src = changeToThis.src;

	//Change form's file value to the img u want to upload
	// submitForm.elements["file"].setAttribute("value",decodeURIComponent(changeToThis.src));
	// saveForm.elements["file"].setAttribute("value",decodeURIComponent(changeToThis.src));
	let ep=document.getElementById("ep-img-src");
	ep.src=img.src;
}

// Ignore this code: following Jesse's method for homeworks (no need and ws has different structure)
// let socket = io();
//
// function leaveComment() {
// 	const commentBox = document.getElementById("form-comment-message");
// 	const comment = commentBox.value;
// 	const username = document.getElementById("header-user").textContent;
// 	socket.on("message", function() {
//
// 	})
// }

//delay form submission so it has time to set new data url value of form
// let form=document.getElementById("elephant-submit-form");
// form.addEventListener('submit',submissionHandler);
// let timer;
//
// function submissionHandler(ev) {
// 	console.log("timer?");
// 	ev.preventDefault();
// 	timer=setTimeout(() => {
// 		this.submit();
// 		console.log("delayed submission");
// 	}, 1000);
// }

function customForm() {
	let form=document.getElementById("elephant-submit-form");
	form.addEventListener('submit',function(event) {
		event.preventDefault();
		let formObj=new FormData();
		let title=document.getElementById('title').value;
		let desc=document.getElementById("description").value;
		let user=document.getElementById("username").value;
		formObj.append('title',title);
		formObj.append('description',desc);
		formObj.append('username',user);
		fetch('/submit-elephant', {
			method: "POST",
			body: "formObj"
		});
	});
}
