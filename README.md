### How to install the code:

1. Create a virtual environment (RUN THIS ONLY ONCE AFTER CLONING)

`python3 -m venv venv`

2. Activate the virtual environment

`venv\Scripts\activate.bat`

You should see '(venv)' at the start of the command prompt

3. Install the libraries (just once, skip if done before)

`python3 -m pip install -r requirements.txt`

4. Apply migrations to db.

`python3 manage.py migrate`

5. Create admin user

`python3 manage.py createsuperuser`

follow the instructions to create an admin user (email and password don't need to be real)
The setup should be complete.

### How to run the code:

`python3 manage.py runserver`

Server is now running!

You can go to the admin panel using `http://127.0.0.1:8000/admin/`
or use the api at `http://127.0.0.1:8000/api`.
