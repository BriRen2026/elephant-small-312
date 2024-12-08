# PROJECT PART 2 GRADING PROCEDURE CLARIFICATIONS
# Objective 1
> [!NOTE]
> TESTING ON CHROME: Currently, you cannot dress up an elephant in chrome the same way a firefox user can (We are going to fix this!!!). However, you can follow this procedure to fulfill the multimedia objective:
* To test multimedia on Chrome, you can still go to "Visit Your Closet (Post Feature Here)" on the home page. Trying to put clothes on the elephant will not work, so just press the "Submit Elephant" button and fill in any information if desired.
* Submitting an Elephant results in a multimedia upload being posted. This post contains the title, description, which event a user is submitting for (text), and the actual elephant a user dressed up (image), which in the chrome case, is currently just a black image.
* Clicking on "View Posted Elephants" in the navigation bar will show you the uploaded black image, which is still technically an image! Here you can also view the dressed up elephants that a firefox user made.
* Once you've uploaded the black image "elephant", if you're still not conviced of multimedia, you can click your profile picture (red circle in the header) and select a .jpg, .png, or .gif to be your new profile picture.
* Going back to "View Posted Elephants" will show your new profile picture on your previous black image post!

> [!NOTE]
> TESTING ON FIREFOX: No problems with dressing up elephants :)
* Post feature/functionality found via the "Visit Your Closet (Post Feature Here)" button under "Design an Elephant!"
* Dress up an elephant by dragging the clothes onto it. Then, submit it!!
* Submitting an Elephant results in a multimedia upload being posted. This post contains the title, description, which event a user is submitting for (text), and the actual elephant a user dressed up (image).
* Other users can consume these multimedia posts by clicking "View Elephant Posts" in the navigation bar.
# Objective 2
* Users can interact with Websockets by clicking on "View Elephant Posts" in the navigation bar.
* Websocket interaction occurs in the comment section of each post. Click on "View Comments" to see comments posted by other users in real time!
* Currently, when a user posts a comment, it closes that comment box for all other users. However, they are not actually disconnected from the websocket connection. This can be verified by opening the Network tab.
# Objective 3
* Visit "elephantsmall.com" to view our deployed website.
* Just like objective 2, go to "View Elephant Posts" to watch Websocket Interactions occur securely via wss :)
* When creating an elephant post to comment on, if the submission results in a "413 Entity Too Large" error, please go back and submit a new elephant with a different elephant base image!

# PROJECT PART 3 OBJECTIVE 3
# Description:
This creative feature incorporates a drag-and-drop elephant dress-up game (created using an HTML canvas and the p5.js library). After you select an elephant, you can navigate to five different fashion item menus to drag/drop them onto your elephant!
# Testing Procedure:
1. Start your server using docker compose up
2. At the top right of the home page, click "Register" to make a new account. When your registration is validated, you will be automatically logged in.
3. Click the "View Your Closet" button under the "Design an Elephant!" section of the home page.
4. Click one of four elephant images to choose which elephant you want to dress up.
5. Navigate to any of the five menus (Head, Face, Pets, Shoes, Accessories). Choose one of the fashion items; drag and drop it onto the image of your chosen elephant.
    5a. After the fashion item has been dropped on the elephant, drag it to your desired position.
    5b. Repeat steps 5 and 5a as many times as desired. If 10 items are placed on the elephant, attempt to drag an 11th item onto the elephant, and confirm that an alert pops up instead of dropping the element.
6. Find the sidebar of fashion item icon boxes to the left of the elephant. Click one of the icon boxes, and confirm that the corresponding fashion item on the elephant disappears.
    6a. Repeat with as many icon boxes as desired, with the constraint that at least one fashion item must remain on the elephant at the end of this step.
7. After your elephant has been fully dressed up, click the "Submit Elephant (Post Feature)" button.
8. Give your fashionable elephant a title and a description if desired! Then click "Submit Outfit".
9. If you are not redirected to the "Submitted Fashionable Elephants" page, click "View Posted Elephants" at the top of the page.
10. Confirm that the most recently posted elephant is dressed up to the expected extent (based on steps 5 and 6).
