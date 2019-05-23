# flask_book_plus_auth
------------
This app is started from the command line but with:
python app.py
-----------
Transferred templates folder over

modified
C:\Users\lfernandez\Documents\GitHub\flask_book_plus_auth\venv\Lib\site-packages\flask_user\templates\flask_user_layout.html
(e.g. added nav to it)

modified
base.html
(changed it so it was similar to flask_user_layout but inserted some blocks from base into block content)

consolidated admin urls onto new page
-----------
creating callable functions from jinja2 temmplates:
https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2

-----------
TODO: get role and hide admin function when appropriate (can probably do with sql)
consolidate databases
add form to add other admins
consolidate flask_user_layout and base.html  (can probably just have base extend flask_user_layout)
format forms better
move signup stuff to right
separate stuff out into db file, app file and route file
