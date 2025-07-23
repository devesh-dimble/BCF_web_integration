# BCF API — Manual

This is the current working documentation for your `server.py` implementation, including example `curl` commands for testing each endpoint.

---

## 📁 Authentication

### `POST /Authentication/login`

**Description:** Generates a JWT token for a user.

**Request:**

```bash
curl -X POST http://localhost:5000/Authentication/login \
  -H "Content-Type: application/json" \
  -d '{
    "userName": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
  }'
```

**Response:**

```json
{
  "token": "<JWT_TOKEN>"
}
```

---

## 🗂️ Projects

### `GET /Projects`

**Description:** Returns all distinct project IDs.

**Request:**

```bash
curl -X GET http://localhost:5000/Projects \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `GET /Projects/<project_id>/projectExtensionsCustom`

**Description:** Returns dummy project extension data (mock).

**Request:**

```bash
curl -X GET http://localhost:5000/Projects/123/projectExtensionsCustom \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 🗂️ Topics

### `GET /bcf/<version>/projects/<project_id>/topics`

**Description:** Returns all topics for a project, including nested comments.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `POST /bcf/<version>/projects/<project_id>/topics`

**Description:** Creates a new topic.

**Request:**

```bash
curl -X POST http://localhost:5000/bcf/3.0/projects/123/topics \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Issue Title",
    "status": "Open",
    "creation_author": "Author Name"
  }'
```

---

### `PUT /bcf/<version>/projects/<project_id>/topics/<topic_id>`

**Description:** Updates an existing topic.

**Request:**

```bash
curl -X PUT http://localhost:5000/bcf/3.0/projects/123/topics/abc123 \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "status": "In Progress",
    "modified_author": "Modifier Name"
  }'
```

---

### `DELETE /bcf/<version>/projects/<project_id>/topics/<topic_id>`

**Description:** Deletes an existing topic.

**Request:**

```bash
curl -X DELETE http://localhost:5000/bcf/3.0/projects/123/topics/abc123 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/related_topics`

**Description:** Returns dummy related topics.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/related_topics \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 💬 Comments

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/comments`

**Description:** Returns all comments for a topic.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/comments \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/comments`

**Description:** Adds a new comment.

**Request:**

```bash
curl -X POST http://localhost:5000/bcf/3.0/projects/123/topics/abc123/comments \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "author": "Name",
    "comment": "Text"
  }'
```

---

### `DELETE /bcf/<version>/projects/<project_id>/topics/<topic_id>/comments/<comment_id>`

**Description:** Deletes a comment.

**Request:**

```bash
curl -X DELETE http://localhost:5000/bcf/3.0/projects/123/topics/abc123/comments/54aa3fd4-3454-42c0-aaa8-ecf5f4e8734a \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 🎥 Viewpoints

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints`

**Description:** Returns dummy list of viewpoints.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/viewpoints \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints`

**Description:** Creates a dummy viewpoint.

**Request:**

```bash
curl -X POST http://localhost:5000/bcf/3.0/projects/123/topics/abc123/viewpoints \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Viewpoint"
  }'
```

---

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/selection`

**Description:** Returns dummy selection data.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/viewpoints/vp-456/selection \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/visibility`

**Description:** Returns dummy visibility settings.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/viewpoints/vp-456/visibility \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/snapshot`

**Description:** Returns dummy base64 snapshot string.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/viewpoints/vp-456/snapshot \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 📎 Documents

### `GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references`

**Description:** Returns dummy document references.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/topics/abc123/document_references \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references`

**Description:** Adds a dummy document reference.

**Request:**

```bash
curl -X POST http://localhost:5000/bcf/3.0/projects/123/topics/abc123/document_references \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "doc-789"
  }'
```

---

### `GET /bcf/<version>/projects/<project_id>/documents/<doc_id>`

**Description:** Returns dummy document metadata.

**Request:**

```bash
curl -X GET http://localhost:5000/bcf/3.0/projects/123/documents/doc-123 \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### `POST /bcf/<version>/projects/<project_id>/documents`

**Description:** Accepts a file upload and returns a dummy ID.

**Request:**

```bash
curl -X POST http://localhost:5000/bcf/3.0/projects/123/documents \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@/path/to/your/file.pdf"
```

---

## ⚙️ Important Note

> **This API currently uses dummy/mock data for:**
>
> - **Viewpoints**
> - **Document storage**
>
> These should be connected to real database tables and file storage in the future.

---

## ✅ Authentication Required

All routes except `/Authentication/login` require the `Authorization` header:

```
Authorization: Bearer <JWT_TOKEN>
```

