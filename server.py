import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import jwt
print(jwt.__version__)
from datetime import datetime, timedelta
from functools import wraps
from main import Topic  # your SQLAlchemy Topic model
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
import uuid
from main import Comment  # make sure you import Comment!

engine = create_engine("postgresql+psycopg2://bcfuser:bcfpass@localhost:5432/bcfdb")
Session = sessionmaker(bind=engine)

load_dotenv()  # Load .env into env vars

app = Flask(__name__)
app.config["JWT_SECRET"] = os.environ["JWT_SECRET"]

@app.route("/Authentication/login", methods=["POST"])
def login():
    data = request.get_json()
    user = data.get("userName")
    pw   = data.get("password")

    # Check against your .env values
    if user != os.environ["API_USER"] or pw != os.environ["API_PASS"]:
        return jsonify({"msg": "Invalid credentials"}), 401

    exp = datetime.utcnow() + timedelta(hours=2)
    token = jwt.encode({"sub": user, "exp": exp}, app.config["JWT_SECRET"], algorithm="HS256")

    return jsonify({"token": token})

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization","")
        if not auth.startswith("Bearer "):
            return jsonify({"msg":"Missing token"}), 401
        token = auth.split(None,1)[1]
        try:
            jwt.decode(token, app.config["JWT_SECRET"], algorithms=["HS256"])
        except Exception:
            return jsonify({"msg":"Invalid or expired token"}), 401
        return f(*args, **kwargs)
    return decorated

# --- Projects ---
@app.route("/Projects")
@require_auth
def get_projects():
    """GET /Projects — return all distinct project IDs"""
    session = Session()
    project_ids = session.query(Topic.project_id).distinct().all()
    session.close()
    projects = [{"projectId": pid[0], "name": f"Project {pid[0]}"} for pid in project_ids]
    #return jsonify([{"projectId": "123", "name": "Demo Project"}])
    return jsonify(projects)

#Get Topics
@app.route("/bcf/<version>/projects/<project_id>/topics")
@require_auth
def get_topics(version, project_id):
    """GET /bcf/v/projects/{pid}/topics — list topics + nested comments"""
    session = Session()
    topics = session.query(Topic).filter_by(project_id=project_id).all()
    result = []
    for t in topics:
        result.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "creation_author": t.creation_author,
            "comments": [
                {
                    "id": c.id,
                    "author": c.author,
                    "comment": c.comment
                } for c in t.comments
            ]
        })
    session.close()
    return jsonify(result)

#POST Topic
@app.route("/bcf/<version>/projects/<project_id>/topics", methods=["POST"])
@require_auth
def post_topic(version, project_id):
    """POST /bcf/v/projects/{pid}/topics — create a new topic"""
    data = request.get_json()
    session = Session()

    new_id = str(uuid.uuid4())
    new_topic = Topic(
        id=new_id,
        project_id=project_id,
        title=data.get("title"),
        status=data.get("status"),
        creation_author=data.get("creation_author")
    )

    session.add(new_topic)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        session.close()
        return jsonify({"msg": f"Topic with id {new_id} already exists"}), 409
    response = jsonify({"msg": "Topic created", "id": new_topic.id})
    session.close()
    return response, 201

#POST Comment
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/comments", methods=["POST"])
@require_auth
def post_comment(version, project_id, topic_id):
    data = request.get_json()
    session = Session()

    new_comment = Comment(
        id=str(uuid.uuid4()),
        topic_id=topic_id,
        author=data["author"],
        comment=data["comment"]
    )

    session.add(new_comment)
    session.commit()
    new_id = new_comment.id
    session.close()

    return jsonify({"msg": "Comment created", "id": new_id}), 201

#PUT update Topic
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>", methods=["PUT"])
@require_auth
def put_topic(version, project_id, topic_id):
    data = request.get_json()
    session = Session()

    topic = session.query(Topic).filter_by(id=topic_id, project_id=project_id).first()
    if not topic:
        session.close()
        return jsonify({"msg": "Topic not found"}), 404

    topic.title = data.get("title", topic.title)
    topic.status = data.get("status", topic.status)
    topic.modified_author = data.get("modified_author", topic.creation_author)
    topic.modified_date = datetime.utcnow()

    session.commit()
    session.close()

    return jsonify({"msg": "Topic updated", "id": topic_id}), 200

#DELETE Topic
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>", methods=["DELETE"])
@require_auth
def delete_topic(version, project_id, topic_id):
    session = Session()

    topic = session.query(Topic).filter_by(id=topic_id, project_id=project_id).first()
    if not topic:
        session.close()
        return jsonify({"msg": "Topic not found"}), 404

    # OPTION 1: Really delete
    session.delete(topic)

    # OPTION 2: Or mark as deleted instead (soft delete)
    # topic.status = "Deleted"
    # Or topic.deleted = True (if you add a deleted column)

    session.commit()
    session.close()

    return jsonify({"msg": f"Topic {topic_id} deleted"}), 200

#DELETE Comment
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/comments/<comment_id>", methods=["DELETE"])
@require_auth
def delete_comment(version, project_id, topic_id, comment_id):
    session = Session()

    comment = session.query(Comment).filter_by(id=comment_id, topic_id=topic_id).first()
    if not comment:
        session.close()
        return jsonify({"msg": "Comment not found"}), 404

    # OPTION 1: Really delete
    session.delete(comment)

    # OPTION 2: Or mark deleted (if you add a `deleted` flag)
    # comment.deleted = True

    session.commit()
    session.close()

    return jsonify({"msg": f"Comment {comment_id} deleted"}), 200

# GET Comments
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/comments", methods=["GET"])
@require_auth
def get_comments(version, project_id, topic_id):
    session = Session()
    comments = session.query(Comment).filter_by(topic_id=topic_id).all()
    result = []
    for c in comments:
        result.append({
            "id": c.id,
            "author": c.author,
            "comment": c.comment
        })
    session.close()
    return jsonify(result), 200

@app.route("/Projects/<project_id>/projectExtensionsCustom", methods=["GET"])
@require_auth
def get_extensions(project_id):
    """
    GET /Projects/<project_id>/projectExtensionsCustom
    For now, returns a mock object — replace with real logic.
    """
    # TODO: Replace this with real extensions data from your DB if you have it.
    extensions = {
        "projectId": project_id,
        "customField1": "Example value",
        "customField2": True,
        "customField3": ["OptionA", "OptionB"]
    }
    return jsonify(extensions), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/related_topics", methods=["GET"])
@require_auth
def get_related_topics(version, project_id, topic_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/related_topics
    For now, returns mock related topics — add real logic later.
    """
    session = Session()
    # For now: Just return 2 other topics from the same project (example logic)
    related = session.query(Topic).filter(
        Topic.project_id == project_id,
        Topic.id != topic_id
    ).limit(2).all()

    result = []
    for t in related:
        result.append({
            "id": t.id,
            "title": t.title,
            "status": t.status
        })

    session.close()
    return jsonify(result), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints", methods=["GET"])
@require_auth
def get_viewpoints(version, project_id, topic_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints
    For now, returns a mock list — wire to DB or file later.
    """
    # Example dummy data — adjust as needed
    viewpoints = [
        {
            "id": "vp-123",
            "name": "Main View",
            "snapshot_url": "/some/path/to/snapshot.jpg"
        },
        {
            "id": "vp-456",
            "name": "Side View",
            "snapshot_url": "/some/path/to/snapshot2.jpg"
        }
    ]
    return jsonify(viewpoints), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints", methods=["POST"])
@require_auth
def post_viewpoint(version, project_id, topic_id):
    """
    POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints
    Accepts a viewpoint payload, returns a dummy ID.
    """
    data = request.get_json()

    # TODO: Save to DB later if needed
    new_viewpoint_id = str(uuid.uuid4())

    response = {
        "msg": "Viewpoint created",
        "id": new_viewpoint_id,
        "name": data.get("name", "Unnamed Viewpoint")
    }

    return jsonify(response), 201

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/selection", methods=["GET"])
@require_auth
def get_selection(version, project_id, topic_id, viewpoint_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/selection
    Returns mock selection data for now.
    """
    selection = {
        "viewpoint_id": viewpoint_id,
        "selected_components": [
            {"guid": "element-1"},
            {"guid": "element-2"}
        ]
    }
    return jsonify(selection), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/visibility", methods=["GET"])
@require_auth
def get_visibility(version, project_id, topic_id, viewpoint_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/visibility
    Returns mock visibility data.
    """
    visibility = {
        "viewpoint_id": viewpoint_id,
        "default_visibility": True,
        "exceptions": [
            {"guid": "element-1", "visible": False},
            {"guid": "element-2", "visible": True}
        ]
    }
    return jsonify(visibility), 200

import base64

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/snapshot", methods=["GET"])
@require_auth
def get_snapshot(version, project_id, topic_id, viewpoint_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/viewpoints/<viewpoint_id>/snapshot
    Returns a mock base64 snapshot string.
    """
    # Example: Just use a simple text as fake image
    fake_image_bytes = b"FakeImageContent"
    fake_image_b64 = base64.b64encode(fake_image_bytes).decode("utf-8")

    snapshot = {
        "viewpoint_id": viewpoint_id,
        "snapshot": fake_image_b64
    }

    return jsonify(snapshot), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references", methods=["GET"])
@require_auth
def get_document_references(version, project_id, topic_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references
    Returns mock document references for now.
    """
    references = [
        {"doc_id": "doc-123", "name": "Specs.pdf"},
        {"doc_id": "doc-456", "name": "Detail.png"}
    ]
    return jsonify(references), 200

@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references", methods=["POST"])
@require_auth
def post_document_reference(version, project_id, topic_id):
    """
    POST /bcf/<version>/projects/<project_id>/topics/<topic_id>/document_references
    Accepts a doc ID payload and stores the reference — mock only for now.
    """
    data = request.get_json()
    doc_id = data.get("doc_id")

    if not doc_id:
        return jsonify({"msg": "Missing doc_id"}), 400

    # TODO: Save to DB if you track doc references

    response = {
        "msg": f"Document reference {doc_id} added to topic {topic_id}"
    }

    return jsonify(response), 201

@app.route("/bcf/<version>/projects/<project_id>/documents/<doc_id>", methods=["GET"])
@require_auth
def get_document(version, project_id, doc_id):
    """
    GET /bcf/<version>/projects/<project_id>/documents/<doc_id>
    Returns mock document info — replace with real file serving later.
    """
    document = {
        "doc_id": doc_id,
        "name": "example.pdf",
        "size": "1.2MB",
        "url": f"/files/{doc_id}"
    }
    return jsonify(document), 200

from flask import send_file  # You may already have this

@app.route("/bcf/<version>/projects/<project_id>/documents", methods=["POST"])
@require_auth
def post_document(version, project_id):
    """
    POST /bcf/<version>/projects/<project_id>/documents
    Accepts a file upload and stores it — mock only for now.
    """
    if 'file' not in request.files:
        return jsonify({"msg": "No file part in request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No selected file"}), 400

    # For now, don’t actually save — just fake an ID.
    new_doc_id = str(uuid.uuid4())
    filename = file.filename

    response = {
        "msg": "Document uploaded",
        "doc_id": new_doc_id,
        "filename": filename
    }

    return jsonify(response), 201


if __name__ == "__main__":
    app.run(debug=True)