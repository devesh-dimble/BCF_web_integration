**Server API Documentation**

---

## 1. Overview

This document describes the Flask REST API implemented in `server.py`. It explains all routes, request/response formats, authentication, and includes **real cURL examples** to test each endpoint directly.

---

## 2. Setup

- **Run server:** `python server.py`
- **Environment:** `.env` with `JWT_SECRET`, `API_USER`, `API_PASS`

---

## 3. Authentication

### Login

**Endpoint:** `POST /Authentication/login`

**Request:**

```json
{
  "userName": "<username>",
  "password": "<password>"
}
```

**Response:**

```json
{
  "token": "<JWT>"
}
```

**Example:**

```bash
curl -X POST http://localhost:5000/Authentication/login \
     -H "Content-Type: application/json" \
     -d '{ "userName": "admin", "password": "secret" }'
```

---

## 4. Projects

### List Projects

**Endpoint:** `GET /Projects`

**Example:**

```bash
curl -X GET http://localhost:5000/Projects \
     -H "Authorization: Bearer <JWT>"
```

**Response:**

```json
[
  { "projectId": "123", "name": "Project 123" }
]
```

---

## 5. Topics

### List Topics

**Endpoint:** `GET /bcf/<version>/projects/<project_id>/topics`

**Example:**

```bash
curl -X GET http://localhost:5000/bcf/1.0/projects/123/topics \
     -H "Authorization: Bearer <JWT>"
```

### Create Topic

**Endpoint:** `POST /bcf/<version>/projects/<project_id>/topics`

**Body:**

```json
{
  "title": "New Issue",
  "status": "Open",
  "creation_author": "alice"
}
```

**Example:**

```bash
curl -X POST http://localhost:5000/bcf/1.0/projects/123/topics \
     -H "Authorization: Bearer <JWT>" \
     -H "Content-Type: application/json" \
     -d '{ "title": "Fix Bug", "status": "Open", "creation_author": "alice" }'
```

### Update Topic

**Endpoint:** `PUT /bcf/<version>/projects/<project_id>/topics/<topic_id>`

**Example:**

```bash
curl -X PUT http://localhost:5000/bcf/1.0/projects/123/topics/abc123 \
     -H "Authorization: Bearer <JWT>" \
     -H "Content-Type: application/json" \
     -d '{ "title": "Updated Title", "status": "Closed", "modified_author": "bob" }'
```

### Delete Topic

**Endpoint:** `DELETE /bcf/<version>/projects/<project_id>/topics/<topic_id>`

**Example:**

```bash
curl -X DELETE http://localhost:5000/bcf/1.0/projects/123/topics/abc123 \
     -H "Authorization: Bearer <JWT>"
```

---

## 6. Comments

### Create Comment

**Endpoint:** `POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/comments`

**Body:**

```json
{
  "author": "bob",
  "comment": "This needs more detail"
}
```

**Example:**

```bash
curl -X POST http://localhost:5000/bcf/1.0/projects/123/topics/abc123/comments \
     -H "Authorization: Bearer <JWT>" \
     -H "Content-Type: application/json" \
     -d '{ "author": "bob", "comment": "Please review." }'
```

### Delete Comment

**Endpoint:** `DELETE /bcf/<version>/projects/<project_id>/topics/<topic_id>/comments/<comment_id>`

**Example:**

```bash
curl -X DELETE http://localhost:5000/bcf/1.0/projects/123/topics/abc123/comments/c456 \
     -H "Authorization: Bearer <JWT>"
```

