function staticJS() {
    document.getElementById("section-header").innerHTML += "<br/>(this text is a JS placeholder for the static page)";
}

function elephantSound(){
	const sound = new Audio("../elephant.mp3");
	sound.play();
}
