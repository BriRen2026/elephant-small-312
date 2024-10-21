
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
