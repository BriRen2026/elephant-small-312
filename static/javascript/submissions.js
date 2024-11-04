
//Submission stuff
const shadow = document.getElementById("shadow");
const submitDialog = document.getElementById("dialog-submit");
const saveDialog = document.getElementById("dialog-save");
//Opens dialog boxes for form submissions

//Opens submit elephant dialog box
function openDialog(){
	submitDialog.style.display = "block";
	saveDialog.style.display = "none";
	shadow.style.display = "block";
	shadow.style.visibility = "visible";
}

//Closes submit elephant dialog box
function closeDialog(){
	submitDialog.style.display = "none";
	shadow.style.display = "none;"
	shadow.style.visibility = "hidden";
}

//Opens save elephant dialog box
function openDialog2(){
	saveDialog.style.display = "block";
	submitDialog.style.display = "none";
	shadow.style.display = "block";
	shadow.style.visibility = "visible";
}

//Closes save elephant dialog box
function closeDialog2(){
	saveDialog.style.display = "none";
	shadow.style.display = "none;"
	shadow.style.visibility = "hidden";
}

//Elephant filter stuff

const elephants = document.getElementById("elephant-selector")
const headacc = document.getElementById("head-selector")

function elephantSelector(){
	console.log("Show elephants");
	elephants.style.display = "block";
	headacc.style.display = "none";
}

function headSelector(){
	console.log("Show heads");
	elephants.style.display = "none";
	headacc.style.display = "block";
}


//Actually choosing an elephant to dress up
function selectElephant(div){
	//Change the img source for our elephant-pic img
	const elephantpic = document.getElementById("elephant-pic");
	const submitForm = document.forms["elephant-submit-form"]
	const saveForm = document.forms["elephant-save-form"]

	//Changes the Big Selected elephant image to whatever a user selects
	const changeYourElephantPic = elephantpic.childNodes[0]
	const changeToThis = div.childNodes[0]

	//Change Your Elephant source to whatever the user selected
	changeYourElephantPic.src = changeToThis.src;

	//Change form's file value to the img u want to upload
	submitForm.elements["file"].setAttribute("value",decodeURIComponent(changeToThis.src));
	saveForm.elements["file"].setAttribute("value",decodeURIComponent(changeToThis.src));
}