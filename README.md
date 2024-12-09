# PROJECT PART 3 OBJECTIVE 2
# Description:
Implementation of IP Rate Limiting using the flask-gatekeeper library. 
# Testing Procedure:
1. Go to any page and refresh a bunch :-)
2. When calculating the amount of refreshes needed to reach the 50req/10sec limit, ensure that you are only looking at the requests to elephantsmall.com and not the total requests made. For example, certain requests like bootstrap, fontawesome icons, or google fonts are made to external sites and wouldn't count towards the request limit for elephantsmall.com

# PROJECT PART 3 OBJECTIVE 3
# Description:
This feature incorporates a drag-and-drop elephant dress-up game (created using an HTML canvas and the p5.js library). As opposed to simply uploading pictures of elephants, you can now style them before submitting! After you select an elephant image, you can navigate to five different fashion item menus to drag/drop them onto your elephant! Fashionable elephants can then be uploaded to the elephant feed for other users to like/comment on.
# Testing Procedure:
1. Start your server using docker compose up
2. Open a browser (Firefox or Chrome) and navigate to http://localhost:8080/
3. At the top right of the home page, click "Register" to make a new account. Enter a valid username and password (both must non-empty strings and username must be different from any other previously used usernames). When your registration is validated, you will be automatically logged in.
4. Click the "View Your Closet" button under the "Design an Elephant!" section of the home page.
5. Click one of four elephant images to choose which elephant you want to dress up.
6. Navigate to any of the five menus (Head, Face, Pets, Shoes, Accessories). Choose one of the fashion items; drag and drop it onto the image of your chosen elephant.
     * 6a. After the fashion item has been dropped on the elephant, drag it to your desired location on the canvas.
     * 6b. Repeat steps 6 and 6a as many times as desired. If 10 items are placed on the elephant, attempt to drag an 11th item onto the elephant, and confirm that an alert pops up instead of dropping the element.
7. Find the sidebar of fashion item icon boxes to the left of the elephant. Click one of the icon boxes, and confirm that the corresponding fashion item on the elephant disappears.
     * 7a. Repeat deleting as many icon boxes as desired, with the constraint that at least one fashion item must remain on the elephant at the end of this step.
8. After your elephant has been fully dressed up, click the "Submit Elephant (Post Feature)" button.
9. Give your fashionable elephant a title and a description if desired! Then click "Submit Outfit".
10. If you are not redirected to the "Submitted Fashionable Elephants" page, click "View Posted Elephants" at the top of the page.
11. Confirm that the most recently posted elephant is dressed up to the expected extent (based on steps 6 and 7). Confirm that the username you registered an account with appears at the top right of the elephant post.
