Social Media Backend API (FastAPI)

A backend REST API built using FastAPI that enables users to communicate through posts and interact with content through likes.
This project is developed by following a comprehensive FastAPI tutorial and focuses on real-world backend development concepts such as CRUD operations, relational data modeling, and scalable API design.

The backend forms the foundation of a social media platform where users can create posts, like posts created by other users, and view engagement on posts.

Features

1.Create posts for communication

2.Retrieve all posts or a specific post

3.Update and delete posts

4.Like posts created by other users

5.View which users liked a particular post

6.View which posts are liked by a user

7.RESTful API design

8.Request and response validation using Pydantic

9.Automatic API documentation (Swagger UI)

10.Modular and scalable backend structure

Tech Stack

⦁	Language: Python

⦁	Framework: FastAPI

⦁	Server: Uvicorn

⦁	Database: Postgresql

⦁	ORM: SQLAlchemy

⦁	Validation: Pydantic


Installation and Setup

1.Clone the repository

git clone <your-repository-link>
cd social_backend


2.Create and activate virtual environment

python -m venv venv
source venv/bin/activate


(Windows: venv\Scripts\activate)

3.Install dependencies

pip install -r requirements.txt


4.Run the application

uvicorn app.main:app --reload

5.API Documentation

After running the server, open:

http://127.0.0.1:8000/docs


or

http://127.0.0.1:8000/redoc

6.API Endpoints

Posts

GET /posts
Fetch all posts

GET /posts/{id}
Fetch a post by ID

POST /posts
Create a new post

PUT /posts/{id}
Update an existing post

DELETE /posts/{id}
Delete a post

Likes

POST /posts/{id}/like
Like or unlike a post

GET /posts/{id}/likes
View all users who liked a post

GET /users/{id}/likes
View all posts liked by a user

Concepts Learned

1.	FastAPI routing and dependency injection

2.	REST API design principles

3.	Relational database modeling

4.	Many-to-many relationships (posts and users via likes)

5.	CRUD operations with SQLAlchemy

6.	Request validation using Pydantic

7.	Clean backend project structuring

8.	Future Enhancements

9.	User authentication using JWT

10.	Comments system

11.	Follow and unfollow users

12.	PostgreSQL integration

13.	Pagination and filtering

Author

Priyamvada Singh
Backend Developer | Python | FastAPI
