# elephant-small-312
NEW FILE STRUCTURE: overarching changes required by Flask
* all HTML templates in the templates folder
* all static content in respective directories in static folder
* all paths in app.py (only home implemented as of 10/14/24)
* removed public directory
* removed Docker directory; Docker and docker-compose in root

GENERAL FLASK CONCEPTS
* syntax for creating paths is quite simple--see app.py for structure
* see home.html for syntax of src and href tags when accessing file paths: first arg of url_for should always be 'static,' specify static directory in second arg if relevant (images, css, javascript)
* for quick testing, instead of docker compose up, you can run app.py and it will open the localhost link. upon any errors, you can give app.run() a first argument of debug=True which will show you every error encountered

unexplained behaviors that shouldn't(?) work but do
* upon invoking docker compose up, two links appear with 127.#.#.# IP addresses. only one works. instead of accessing either, just navigate to http://localhost:8080/ in browser
* for some reason HTMl placeholder vars denoted by {{ }} cannot start with a capital letter and must be all one word
* in app.py, even if it shows a message that it cannot find the template home.html, ignore it (the template renders) (hoping this is true for other templates as well)