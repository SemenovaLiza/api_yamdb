# Api Yamdb
### *Description*
The project allows you to create multimedia content and leave reviews for it, as well as comment on the reviews.

### *Technologies*
- Python 3.7
- Django 3.2.16
- django rest framework 3.12.4
- django rest framework-simplejwt 4.7.2
###### *The rest of the technologies can be found in the requirements.txt file*

### *Project features*
- Registration and authorization of users by Simple JWT token.
- Getting, creating, updating user's accounts.
- Getting, creating, updating, deleting content, genres, categories.
- Getting, creating, updating, deleting comments and reviews.

[Project documentation](http://127.0.0.1:8000/redoc/)
###### *Documentation will open after the project is deployed.*
### *How to launch a project*
Using terminal change the current working directory to the location where you want the cloned directory.

Clone the repository and go to it:
```
git clone git@github.com:SemenovaLiza/api_yamdb.git
```
```
cd api_yamdb
```
Install and activate the virtual environment:
```
python3 -m venv venv
```
```
source venv/bin/activate
```
Install dependencies from the file requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```
Go to the yatube_api app:
```
cd api_yamdb
```
Perform migrations:
```
python3 manage.py migrate
```
Launсh the project:
```
python3 manage.py runserver
```
A token is required to use some methods in the in Api Yamdb project. To get it, you need to sign up using your email and username.
#### POST /api/v1/auth/signup/
```
{
    "username": "string",
    "email": "string"
} 
```
Next, you will receive a confirmation code to your email.
#### POST /api/v1/auth/token/
```
{
    "username": "string",
    "confirmation_code": "string"
} 
```
Then you will receive a access token that will be passed in the header of each request, in the "Authorization" field. 

Example:
```
Bearer #########
```
You can also change your account details.
#### PATCH /api/v1/users/me/
```
{
    "bio": "string"
}
```
### Title requests
#### POST request api/v1/titles/
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```
#### GET request api/v1/titles/{titles_id}/
```
{
  "id": 0,
  "name": "string",
  "year": 0,
  "rating": 0,
  "description": "string",
  "genre": [
    {
      "name": "string",
      "slug": "string"
    }
  ],
  "category": {
    "name": "string",
    "slug": "string"
  }
}
```
### Genres request
#### GET request api/v1/genres/
```
{
  "count": 0,
  "next": "string",
  "previous": "string",
  "results": [
    {
      "name": "string",
      "slug": "string"
    }
  ]
}
```
### Reviews requests
#### POST api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
{
  "text": "string"
}
```
#### GET api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```
### Review's comments requests
#### POST http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```
{
  "text": "string"
}
```
#### GET api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```
#### PATCH api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/
```
{
  "text": "string"
}
```
### *Project developers:*

User authorization - teamlead Semenova Elizaveta([Github](https://github.com/SemenovaLiza))

Multimedia, genres and categories - Zakharov Vladimir([Github](https://github.com/zakharovvladimir))

Comments and reviews - Vladimir Dolgih([Github](https://github.com/Waffe1n))
