# Catalog App

Catalog app using **Flask** as a framework and libraries such as **JQuery** for JS and **Materialize** for CSS. 
It's been use an sql lite as a Database engine with sqlalchemy python libraries.


# Credentials

You should load you own credentials from google cloud. For creating a new one visit [create credentials](https://support.google.com/cloud/answer/6158849). If you have one, just download the file as a json an rename it as **client_secret.json** and store it into the root project.


# Get Started

To run the project, exec the command line:
	
	``python application.py``
And visit ``http://localhost:5000/``

Make sure you have the necessary python libraries.


# Troubleshooting

If any problem with the database delete the categories.db and exec:

``python models.py``

It will create a new database with the necessary tables