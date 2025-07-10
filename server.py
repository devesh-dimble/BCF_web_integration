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



if __name__ == "__main__":
    app.run(debug=True)