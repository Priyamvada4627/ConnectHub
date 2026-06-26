# ConnectHub

A full-stack social networking platform built with FastAPI and PostgreSQL, featuring real-time messaging, voice messages, image sharing, notifications, follows, likes, comments, and live online presence.

---

## Features

### Authentication
- JWT Authentication
- Secure password hashing with bcrypt
- User registration and login

### Social Features
- Create, edit and delete posts
- Like and unlike posts
- Comment system
- Follow and unfollow users
- Personalized feed
- User profiles

### Real-Time Chat
- One-to-one messaging
- WebSocket-based communication
- Typing indicators
- Read receipts
- Online/offline presence
- Image/Audio sharing

### Notifications
- Follow notifications
- Like notifications
- Comment notifications
- Read/Unread status

### Media Upload
- Cloudinary integration
- Image optimization
- Voice message uploads

---

## Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication
- WebSockets

### Frontend
- HTML
- CSS
- JavaScript

### Cloud
- Cloudinary

---

## Architecture

```
Frontend
     │
 REST API / WebSocket
     │
FastAPI
     │
Routers
     │
Service Layer
     │
SQLAlchemy ORM
     │
PostgreSQL
```

The backend follows a layered architecture:

- Routers handle HTTP requests.
- Services contain business logic.
- Models define database entities.
- Schemas validate request/response data.

---

## Project Structure

```
app/
│
├── routers/
├── services/
├── websocket/
├── models.py
├── schemas.py
├── oauth2.py
├── database.py
└── main.py

frontend/
│
├── css/
├── js/
└── *.html
```

---

## Database

- PostgreSQL
- Alembic migrations
- SQLAlchemy ORM

---

## Installation

### Clone

```bash
git clone <repository-url>
cd ConnectHub
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

### Install

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file:

```env
DATABASE_HOSTNAME=
DATABASE_PORT=
DATABASE_NAME=
DATABASE_USERNAME=
DATABASE_PASSWORD=

SECRET_KEY=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

ALLOWED_ORIGINS=["http://localhost:5500"]
```

### Apply Migrations

```bash
alembic upgrade head
```

### Run

```bash
uvicorn app.main:app --reload
```

---

## API Documentation

Swagger UI

```
http://127.0.0.1:8000/docs
```

ReDoc

```
http://127.0.0.1:8000/redoc
```

---

## Future Improvements

- Docker support
- CI/CD
- Redis caching
- Group chat
- Push notifications

---

## Author

**Priyamvada Singh**

