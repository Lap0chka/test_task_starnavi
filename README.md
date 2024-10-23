Test Task Starnavi

First of all, I would like to explain why I chose Django. 
The main reason is that I don't have experience with FastAPI. 
Additionally, I don't use Django Ninja for the same reason. I used DRF

Overview

This project implements a user registration and authentication system, as well as an API for managing posts and comments. 
Additionally, it includes profanity checking, automatic responses to comments, and analytics of comments posted over a specific period.

Key Features:
User Registration: Allows users to register and create accounts.
User Login: Enables users to authenticate and access the application.
Post Management API: Provides endpoints for creating, reading, updating, and deleting posts.
Comment Management API: Enables CRUD operations on comments associated with posts.
Profanity Filter: Automatically checks posts and comments for inappropriate language during creation and blocks content that contains profanity.
Comment Analytics: API for analyzing the number of comments added to posts over a specific time range.
Example endpoint: /api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15.
Returns the daily breakdown of comments, including counts of blocked and non-blocked comments.
Automatic Comment Response: Allows users to enable automatic responses to comments on their posts with a customizable delay. The response is contextually relevant to the comment and the post.
Tech Stack

Backend: Django, Django REST Framework
Task Queue: Celery
Message Broker/Cache: Redis
Containerization: Docker, Docker Compose
Database: sqlite
Testing: rest_framework.test,  mypy for type checking, 
flake8 for linting, black and isort for formatting 
