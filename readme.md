# CSE 499 Senior Design Project - Codename METSYS

## ToDo
---
### Database
+ ~~Create *tag* models~~
    - ~~index, tag~~
+ ~~Create *requests* model (bangla and english)~~
    - ~~index, request message, tag foreign~~
+ ~~Create *response* model (bangla and english)~~
    - ~~index, response message, tag foreign~~
+ ~~Create *context* model~~
    - ~~index, context~~
+ ~~Create *complaints* model~~
    - ~~request message, response message, time-stamp, index~~
    - ~~complaint will be deleted, when it has been resolved and request is
    added with existing intents with tag, response and context~~
    - ~~have to check if a complaint exists before resolving it, because two
    admins may try to resolve it at the same time~~
+ ~~Create *moderator* model~~
    - ~~use default User model of Django~~
    - ~~create moderator group~~
    - ~~create three users~~
    - ~~add the users to the moderators group~~

+ ~~Create *feedback* model~~
    - ~~index, name(optional), comment~~

### Frontend
+ ~~Add a small red empty crosshair icon beside every bot message~~
    - ~~When clicked, icon will be filled~~
    - ~~The message and the request message before it will be passed to websocket~~
    - ~~The message and the request message before it will be saved in database~~
    - ~~Before saving check if those already exists in database~~
    - ~~If complaint already exists, fill icon and log error in console~~
    - ~~The message and the request message before it can be deleted from database~~

+ ~~Design Admin panel with login for complaints~~
    - ~~Design Login Page~~

+ ~~Feedback Option~~
    - ~~Make a popup with animation for feedback~~

+ Help Option
    - ~~Make a popup with animation for instructions about using the chatbot web
    app~~
    - Add instructions

### Backend
+ ~~Complaints operations~~
    - ~~Save complaint from chat window~~
    - ~~Delete complaint from chat window~~
    - ~~Implement rest api~~
+ ~~Show complaints to admins~~
    - ~~Must add tags or choose existing one~~
    - ~~Must add response, if new tag~~
    - ~~can delete complaint~~
+ ~~A option to generate new `intents.json`~~
    - ~~Option to download that file~~
+ ~~Feedback option~~
    - ~~Add rest api for feedbacks~~
    - ~~Give users option to make comments about the chatbot or web app~~
    - ~~User can give info, if he/she chooses to~~
