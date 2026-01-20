import os
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response, send_file
from flask import send_from_directory
from flask_cors import CORS
import jwt
print(jwt.__version__)
from datetime import datetime, timedelta
from functools import wraps
from main import Project, Topic, Comment, Viewpoint, Bitmap, DocumentReference, Document, Base  # your SQLAlchemy Topic model
from main import (ProjectTopicType,
    ProjectTopicStatus,
    ProjectTopicLabel,
    ProjectSnippetType,
    ProjectPriority,
    ProjectUser,
    ProjectStage,
    ProjectProjectAction,
    ProjectTopicAction,
    ProjectCommentAction,)
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
import uuid

load_dotenv()  # Load .env into env vars

#engine = create_engine("postgresql+psycopg2://bcfuser:bcfpass@localhost:5432/bcfdb")
#engine = create_engine("postgresql+psycopg2://bcfuser:bcfpass@db:5432/bcfdb")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://bcfuser:bcfpass@db:5432/bcfdb")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)

#load_dotenv()  # Load .env into env vars

app = Flask(__name__)
CORS(
    app,
    origins=["http://localhost:4200"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

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

DEFAULT_TOPIC_TYPES = ["Information", "Error"]
DEFAULT_TOPIC_STATUS = ["Open", "Closed", "ReOpened"]
DEFAULT_TOPIC_LABELS = ["Architecture", "Structural", "MEP"]
DEFAULT_SNIPPET_TYPES = [".ifc", ".csv"]
DEFAULT_PRIORITIES = ["Low", "Medium", "High"]
DEFAULT_USERS = [
    "Architect@example.com",
    "BIM-Manager@example.com",
    "bob_heater@example.com",
]
DEFAULT_STAGES = [
    "Preliminary Planning End",
    "Construction Start",
    "Construction End",
]
DEFAULT_PROJECT_ACTIONS = ["update", "createTopic", "createDocument"]
DEFAULT_TOPIC_ACTIONS = [
    "update",
    "updateBimSnippet",
    "updateRelatedTopics",
    "updateDocumentReferences",
    "updateFiles",
    "createComment",
    "createViewpoint",
]
DEFAULT_COMMENT_ACTIONS = ["update"]


# --- Projects ---

@app.route("/bcf/3.0/projects", methods=["GET"])
@require_auth
def get_projects():
    """GET /bcf/3.0/projects — return all projects"""
    session = Session()
    projects = session.query(Project).all()
    session.close()

    #actions = ["createTopic", "createDocument"]  # however you compute them
    result = [p.to_bcf_dict() for p in projects]
    
    """
    result = []
    for i, p in enumerate(projects):
        actions = ["createTopic", "createDocument"] if i % 2 == 0 else []
        result.append({
            "project_id": str(p.id),
            "name": p.name,
            "authorization": {
                "project_actions": actions
            }
        })
    """

    #return jsonify([{"projectId": p.id, "name": p.name} for p in projects])
    return jsonify(result), 200


@app.route("/bcf/3.0/projects", methods=["POST"])
@require_auth
def create_project():
    """POST /bcf/3.0/projects — create a new project"""
    data = request.get_json() or {}

    project_id = data.get("project_id")
    project_name = data.get("name")
    project_actions = data.get("project_actions", [])

    if not project_id or not project_name:
        return jsonify({"message": "project_id and name are required"}), 400
    
    session = Session()

    existing = session.get(Project, project_id)
    if existing:
        return jsonify({"message": "Project already exists"}), 409

    new_project = Project(
        id=project_id,
        name=project_name,
        project_actions=project_actions
    )
    session.add(new_project)

    def seed_list(model_cls, values):
            for v in values:
                session.add(model_cls(project_id=project_id, value=v))

    seed_list(ProjectTopicType, DEFAULT_TOPIC_TYPES)
    seed_list(ProjectTopicStatus, DEFAULT_TOPIC_STATUS)
    seed_list(ProjectTopicLabel, DEFAULT_TOPIC_LABELS)
    seed_list(ProjectSnippetType, DEFAULT_SNIPPET_TYPES)
    seed_list(ProjectPriority, DEFAULT_PRIORITIES)
    seed_list(ProjectUser, DEFAULT_USERS)
    seed_list(ProjectStage, DEFAULT_STAGES)
    seed_list(ProjectProjectAction, DEFAULT_PROJECT_ACTIONS)
    seed_list(ProjectTopicAction, DEFAULT_TOPIC_ACTIONS)
    seed_list(ProjectCommentAction, DEFAULT_COMMENT_ACTIONS)
    session.commit()
    
    session.refresh(new_project)
    
    session.close()
    return jsonify(new_project.to_bcf_dict()), 201
    #return jsonify({"projectId": project_id, "name": project_name}), 201
    #return jsonify({"projectId": new_project.id, "name": new_project.name}), 201


@app.route("/bcf/3.0/projects/<project_id>", methods=["GET"])
@require_auth
def get_project(project_id):
    """GET /bcf/3.0/projects/{id} — return a single project"""
    session = Session()
    project = session.query(Project).filter_by(id=project_id).first()
    session.close()

    project = session.get(Project, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    #return jsonify({"projectId": project.id, "name": project.name})
    return jsonify(project.to_bcf_dict()), 200

#####Project Extensions#####
@app.route("/bcf/<version>/projects/<project_id>/extensions", methods=["GET"])
@require_auth
def get_project_extensions(version, project_id):
    session = Session()
    try:
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topic_types = [
            row.value
            for row in session.query(ProjectTopicType).filter_by(project_id=project_id)
        ]
        topic_status = [
            row.value
            for row in session.query(ProjectTopicStatus).filter_by(project_id=project_id)
        ]
        topic_labels = [
            row.value
            for row in session.query(ProjectTopicLabel).filter_by(project_id=project_id)
        ]
        snippet_types = [
            row.value
            for row in session.query(ProjectSnippetType).filter_by(project_id=project_id)
        ]
        priorities = [
            row.value
            for row in session.query(ProjectPriority).filter_by(project_id=project_id)
        ]
        users = [
            row.value
            for row in session.query(ProjectUser).filter_by(project_id=project_id)
        ]
        stages = [
            row.value
            for row in session.query(ProjectStage).filter_by(project_id=project_id)
        ]
        project_actions = [
            row.value
            for row in session.query(ProjectProjectAction).filter_by(project_id=project_id)
        ]
        topic_actions = [
            row.value
            for row in session.query(ProjectTopicAction).filter_by(project_id=project_id)
        ]
        comment_actions = [
            row.value
            for row in session.query(ProjectCommentAction).filter_by(project_id=project_id)
        ]

        extensions = {
            "topic_type": topic_types,
            "topic_status": topic_status,
            "topic_label": topic_labels,
            "snippet_type": snippet_types,
            "priority": priorities,
            "users": users,
            "stage": stages,
            "project_actions": project_actions,
            "topic_actions": topic_actions,
            "comment_actions": comment_actions,
        }

        return jsonify(extensions), 200

    except Exception as e:
        print("Error in get_project_extensions:", e)
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#Get Topics
@app.route("/bcf/<version>/projects/<project_id>/topics", methods=["GET"])
@require_auth
def get_topics(version, project_id):
    """
    GET /bcf/<version>/projects/<project_id>/topics
    List all topics for a project in BCF format.
    """
    session = Session()
    try:
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topics = session.query(Topic).filter_by(project_id=project_id).all()
        result = [t.to_bcf_dict() for t in topics]
        return jsonify(result), 200
    finally:
        session.close()

# GET single Topic
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>", methods=["GET"])
@require_auth
def get_topic(version, project_id, topic_guid):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_guid>
    Retrieve a specific topic in BCF format.
    """
    session = Session()
    try:
        # Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # Find topic belonging to that project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )

        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # Base BCF fields from your model
        body = topic.to_bcf_dict()

        """# Add BCF-style authorization block
        body["authorization"] = {
            "topic_actions": [
                "createComment",
                "createViewpoint"
            ]
        }"""

        return jsonify(body), 200

    finally:
        session.close()


#POST Topic
@app.route("/bcf/<version>/projects/<project_id>/topics", methods=["POST"])
@require_auth
def post_topic(version, project_id):
    """
    POST /bcf/<version>/projects/<project_id>/topics
    Create a new topic for the project (BCF-style).
    """
    data = request.get_json() or {}
    session = Session()

    try:
        # Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topic_type = data.get("topic_type")
        topic_status = data.get("topic_status")
        title = data.get("title")
        priority = data.get("priority")
        labels = data.get("labels", [])
        assigned_to = data.get("assigned_to")
        bim_snippet = data.get("bim_snippet")

        if not title:
            return jsonify({"message": "title is required"}), 400

        topic_guid = str(uuid.uuid4()).upper()
        server_assigned_id = f"ISSUE-{int(datetime.utcnow().timestamp())}"
        creation_author = "Architect@example.com"  # later: read from JWT

        new_topic = Topic(
            guid=topic_guid,
            project_id=project_id,
            server_assigned_id=server_assigned_id,
            creation_author=creation_author,
            creation_date=datetime.utcnow(),
            topic_type=topic_type,
            topic_status=topic_status,
            title=title,
            priority=priority,
            labels=labels,
            assigned_to=assigned_to,
            bim_snippet=bim_snippet,
        )

        session.add(new_topic)
        session.commit()

        return jsonify(new_topic.to_bcf_dict()), 201

    except Exception as e:
        print("Error in post_topic:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()


#PUT update Topic
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>", methods=["PUT"])
@require_auth
def update_topic(version, project_id, topic_guid):
    """
    PUT /bcf/<version>/projects/<project_id>/topics/<topic_guid>
    Modify a specific topic (BCF-style).
    """
    data = request.get_json() or {}
    session = Session()
    try:
        # Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # Find the topic within that project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # Required per example: these are usually present in the body
        if "topic_type" in data:
            topic.topic_type = data["topic_type"]
        if "topic_status" in data:
            topic.topic_status = data["topic_status"]
        if "title" in data:
            topic.title = data["title"]
        if "priority" in data:
            topic.priority = data["priority"]
        if "labels" in data:
            topic.labels = data["labels"]
        if "assigned_to" in data:
            topic.assigned_to = data["assigned_to"]
        if "bim_snippet" in data:
            topic.bim_snippet = data["bim_snippet"]

        # BCF-style modification metadata
        topic.modified_author = "Architect@example.com"  # later derive from JWT
        topic.modified_date = datetime.utcnow()

        session.commit()

        body = topic.to_bcf_dict()
        # Spec example doesn’t require authorization in PUT response,
        # but you *could* add it here if you want later.

        return jsonify(body), 200

    except Exception as e:
        print("Error in update_topic:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#DELETE Topic
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>", methods=["DELETE"])
@require_auth
def delete_topic(version, project_id, topic_guid):
    """
    DELETE /bcf/<version>/projects/<project_id>/topics/<topic_guid>
    Delete a specific topic.
    """
    session = Session()
    try:
        # Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # Find the topic within that project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # If you later add comments with FK to topic, you might need to
        # delete them first or configure cascade="all, delete-orphan".
        session.delete(topic)
        session.commit()

        # BCF spec just says 200 OK, no body required
        return jsonify({"message": "Topic deleted"}), 200

    except Exception as e:
        print("Error in delete_topic:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

# GET Comments
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments", methods=["GET"])
@require_auth
def get_comments(version, project_id, topic_guid):
    session = Session()
    try:
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        comments = (
            session.query(Comment)
            .filter_by(topic_guid=topic_guid)
            .order_by(Comment.date.asc())
            .all()
        )

        result = [c.to_bcf_dict() for c in comments]
        return jsonify(result), 200
    finally:
        session.close()

#GET single Comment
@app.route(
    "/bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>",
    methods=["GET"],
)
@require_auth
def get_comment(version, project_id, topic_guid, comment_guid):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>
    Return a single comment in BCF format.
    """
    session = Session()
    try:
        # 1) Check project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # 2) Check topic exists and belongs to project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 3) Find the comment with given guid and topic_guid
        comment = (
            session.query(Comment)
            .filter_by(guid=comment_guid, topic_guid=topic_guid)
            .first()
        )
        if not comment:
            return jsonify({"message": "Comment not found"}), 404

        # 4) Return BCF-style dict
        return jsonify(comment.to_bcf_dict()), 200
    finally:
        session.close()

# POST Comment
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments", methods=["POST"])
@require_auth
def post_comment(version, project_id, topic_guid):
    data = request.get_json() or {}
    session = Session()
    try:
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        comment_text = data.get("comment")
        viewpoint_guid = data.get("viewpoint_guid")
        custom_guid = data.get("guid")

        if not comment_text and not viewpoint_guid:
            return jsonify({"message": "Either 'comment' or 'viewpoint_guid' is required"}), 400

        if comment_text is not None and not comment_text.strip():
            return jsonify({"message": "comment must not be empty"}), 400

        comment_guid = custom_guid or str(uuid.uuid4()).upper()
        author = "bob.heater@example.com"  # later from JWT

        new_comment = Comment(
            guid=comment_guid,
            topic_guid=topic_guid,
            date=datetime.utcnow(),
            author=author,
            comment=comment_text or "",
        )

        session.add(new_comment)
        session.commit()

        return jsonify(new_comment.to_bcf_dict()), 201

    except Exception as e:
        print("Error in post_comment:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#PUT Comment
@app.route(
    "/bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>",
    methods=["PUT"],
)
@require_auth
def update_comment(version, project_id, topic_guid, comment_guid):
    """
    PUT /bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>
    Update a single comment (BCF-style).
    """
    data = request.get_json() or {}
    session = Session()
    try:
        # 1) Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # 2) Ensure topic exists and belongs to project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 3) Find the comment belonging to that topic
        comment_obj = (
            session.query(Comment)
            .filter_by(guid=comment_guid, topic_guid=topic_guid)
            .first()
        )
        if not comment_obj:
            return jsonify({"message": "Comment not found"}), 404

        # 4) New comment text
        new_text = data.get("comment")
        if new_text is None or not new_text.strip():
            return jsonify({"message": "comment must not be empty"}), 400

        # 5) Update fields
        comment_obj.comment = new_text
        comment_obj.modified_author = comment_obj.author  # or from JWT later
        comment_obj.modified_date = datetime.utcnow()

        session.commit()

        # 6) Return updated comment in BCF format
        return jsonify(comment_obj.to_bcf_dict()), 200

    except Exception as e:
        print("Error in update_comment:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#DELETE Comment
@app.route(
    "/bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>",
    methods=["DELETE"],
)
@require_auth
def delete_comment(version, project_id, topic_guid, comment_guid):
    """
    DELETE /bcf/<version>/projects/<project_id>/topics/<topic_guid>/comments/<comment_guid>
    Delete a single comment.
    """
    session = Session()
    try:
        # 1) Ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # 2) Ensure topic exists and belongs to project
        topic = (
            session.query(Topic)
            .filter_by(project_id=project_id, guid=topic_guid)
            .first()
        )
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 3) Find the comment belonging to that topic
        comment_obj = (
            session.query(Comment)
            .filter_by(guid=comment_guid, topic_guid=topic_guid)
            .first()
        )
        if not comment_obj:
            return jsonify({"message": "Comment not found"}), 404

        # 4) Delete it
        session.delete(comment_obj)
        session.commit()

        # spec just says 200 OK, no body required
        return "", 200

    except Exception as e:
        print("Error in delete_comment:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

"""######Related Topics###### 
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_id>/related_topics", methods=["GET"])
@require_auth
def get_related_topics(version, project_id, topic_id):

    #GET /bcf/<version>/projects/<project_id>/topics/<topic_id>/related_topics
    #For now, returns mock related topics — add real logic later.

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
    return jsonify(result), 200"""

#GET Viewpoints
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints", methods=["GET"])
@require_auth
def get_viewpoints(version, project_id, topic_guid):
    """
    GET /bcf/{version}/projects/{project_id}/topics/{topic_guid}/viewpoints
    Return all viewpoints for a topic in BCF format (array).
    """
    session = Session()
    try:
        # ensure project exists
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        # ensure topic exists and belongs to project
        topic = session.query(Topic).filter_by(project_id=project_id, guid=topic_guid).first()
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # fetch viewpoints (default ordering - by guid)
        viewpoints = session.query(Viewpoint).filter_by(topic_guid=topic_guid).all()
        result = [v.to_bcf_dict() for v in viewpoints]
        return jsonify(result), 200
    finally:
        session.close()

#POST Viewpoints
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints", methods=["POST"])
@require_auth
def post_viewpoint(version, project_id, topic_guid):
    """
    POST /bcf/{version}/projects/{project_id}/topics/{topic_guid}/viewpoints
    Create a viewpoint. Accepts the full BCF viewpoint JSON (see spec).
    """
    data = request.get_json() or {}
    session = Session()
    try:
        # validate project + topic
        project = session.get(Project, project_id)
        if not project:
            return jsonify({"message": "Project not found"}), 404

        topic = session.query(Topic).filter_by(project_id=project_id, guid=topic_guid).first()
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # Required: in spec guid optional. We'll generate if not provided.
        vp_guid = data.get("guid") or str(uuid.uuid4()).upper()
        # index optional
        index = data.get("index")

        # extract fields
        perspective_camera = data.get("perspective_camera")
        lines = data.get("lines", [])
        clipping_planes = data.get("clipping_planes", [])
        components = data.get("components")
        snapshot_in = data.get("snapshot")  # may contain snapshot_type & snapshot_data
        bitmaps_in = data.get("bitmaps", [])

        # Create viewpoint entry (store snapshot metadata only)
        new_vp = Viewpoint(
            guid=vp_guid,
            topic_guid=topic_guid,
            index=index,
            perspective_camera=perspective_camera,
            lines=lines,
            clipping_planes=clipping_planes,
            snapshot=snapshot_in,
            #snapshot={"snapshot_type": snapshot_in.get("snapshot_type")} if snapshot_in else None,
            components=components
        )
        session.add(new_vp)

        # Handle bitmaps: generate guid for each, store bitmap_data (base64) and metadata
        created_bitmaps = []
        for b in bitmaps_in:
            b_guid = str(uuid.uuid4()).upper()
            bitmap_type = b.get("bitmap_type")
            bitmap_data = b.get("bitmap_data")  # base64 string
            location = b.get("location")
            normal = b.get("normal")
            up = b.get("up")
            height = b.get("height")

            new_b = Bitmap(
                guid=b_guid,
                viewpoint_guid=vp_guid,
                bitmap_type=bitmap_type,
                bitmap_data=bitmap_data,
                location=location,
                normal=normal,
                up=up,
                height=height
            )
            session.add(new_b)
            created_bitmaps.append(new_b)

        session.commit()

        # Refresh to include relationship populated
        session.refresh(new_vp)

        response_body = new_vp.to_bcf_dict()
        # The spec response should not include raw bitmap_data or snapshot_data,
        # so to_bcf_dict returns only bitmap metadata (with generated GUIDs)
        return jsonify(response_body), 201

    except Exception as e:
        print("Error in post_viewpoint:", e)
        session.rollback()
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#GET specific Viewpoint Selection
@app.route("/bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/selection", methods=["GET"])
@require_auth
def get_selection(version, project_id, topic_guid, viewpoint_guid):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/selection
    Retrieve a collection of all selected components in a viewpoint (BCF 3.0 spec).
    """
    session = Session()
    try:
        # 1) Check that the topic exists (optional but nice)
        topic = session.get(Topic, topic_guid)
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 2) Load the viewpoint, ensure it belongs to this topic
        vp = session.get(Viewpoint, viewpoint_guid)
        if not vp or vp.topic_guid != topic_guid:
            return jsonify({"message": "Viewpoint not found"}), 404

        # 3) Extract "selection" from components JSON; default to empty list
        components = vp.components or {}
        selection = components.get("selection", [])

        # 4) Return exactly what BCF expects
        return jsonify({"selection": selection}), 200

    finally:
        session.close()


#GET specific Viewpoint Visibility
@app.route(
    "/bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/visibility",
    methods=["GET"],
)
@require_auth
def get_visibility(version, project_id, topic_guid, viewpoint_guid):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/visibility
    Retrieve visibility of components in a viewpoint (BCF 3.0 spec).
    """
    session = Session()
    try:
        # 1) Ensure topic exists (consistent with other endpoints)
        topic = session.get(Topic, topic_guid)
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 2) Load viewpoint and ensure it belongs to this topic
        vp = session.get(Viewpoint, viewpoint_guid)
        if not vp:
            return jsonify({"message": "Viewpoint not found"}), 404

        if vp.topic_guid != topic_guid:
            return jsonify({"message": "Viewpoint does not belong to this topic"}), 400

        # 3) Extract visibility from components JSON
        components = vp.components or {}
        visibility = components.get("visibility") or {}

        # 4) Return in BCF format
        return jsonify({
            "visibility": visibility
        }), 200

    except Exception as e:
        print("Error in get_visibility:", e)
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()


import base64

#GET specific Viewpoint Snapshot
@app.route(
    "/bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/snapshot",
    methods=["GET"],
)
@require_auth
def get_snapshot(version, project_id, topic_guid, viewpoint_guid):
    """
    GET /bcf/<version>/projects/<project_id>/topics/<topic_guid>/viewpoints/<viewpoint_guid>/snapshot
    Return the viewpoint snapshot (png or jpg) as an image file, according to BCF 3.0.
    """
    session = Session()
    try:
        # 1) Ensure topic exists
        topic = session.get(Topic, topic_guid)
        if not topic:
            return jsonify({"message": "Topic not found"}), 404

        # 2) Load viewpoint and ensure it belongs to this topic
        vp = session.get(Viewpoint, viewpoint_guid)
        if not vp:
            return jsonify({"message": "Viewpoint not found"}), 404

        if vp.topic_guid != topic_guid:
            return jsonify({"message": "Viewpoint does not belong to this topic"}), 400

        # 3) Check snapshot JSON
        if not vp.snapshot:
            # Spec: "A viewpoint contains a snapshot if viewpoint.snapshot != null."
            return jsonify({"message": "No snapshot for this viewpoint"}), 404

        snapshot = vp.snapshot or {}
        snapshot_type = (snapshot.get("snapshot_type") or "").lower()
        snapshot_data_b64 = snapshot.get("snapshot_data")

        if not snapshot_data_b64:
            return jsonify({"message": "Snapshot data missing"}), 404

        try:
            image_bytes = base64.b64decode(snapshot_data_b64)
        except Exception:
            return jsonify({"message": "Invalid snapshot data"}), 500

        # 4) Decide MIME type (BCF example uses png/jpg)
        if snapshot_type in ["jpg", "jpeg"]:
            mimetype = "image/jpeg"
        else:
            # default to PNG if type unknown
            mimetype = "image/png"

        # 5) Return raw image
        return Response(image_bytes, mimetype=mimetype)

    except Exception as e:
        print("Error in get_snapshot:", e)
        return jsonify({"message": "Internal server error"}), 500
    finally:
        session.close()

#GET Document References
@app.route('/bcf/<version>/projects/<project_id>/topics/<topic_guid>/document_references', methods=['GET'])
@require_auth
def get_document_references(version, project_id, topic_guid):
    session = Session()

    # Optional: check topic belongs to project
    topic = session.query(Topic).filter_by(guid=topic_guid, project_id=project_id).first()
    if not topic:
        session.close()
        return jsonify({"error": "Topic not found"}), 404

    refs = session.query(DocumentReference).filter_by(topic_guid=topic_guid).all()

    result = []
    for r in refs:
        result.append({
            "guid": r.guid,
            "url": r.url,
            "document_guid": r.document_guid,
            "description": r.description,
        })

    session.close()
    return jsonify(result), 200

#POST Document Reference
@app.route('/bcf/<version>/projects/<project_id>/topics/<topic_guid>/document_references', methods=['POST'])
@require_auth
def post_document_reference(version, project_id, topic_guid):
    session = Session()

    # 1) Check that topic exists and belongs to project
    topic = session.query(Topic).filter_by(guid=topic_guid, project_id=project_id).first()
    if not topic:
        session.close()
        return jsonify({"error": "Topic not found"}), 404

    data = request.get_json() or {}

    # 2) Extract fields from JSON body
    body_guid       = data.get("guid")
    document_guid   = data.get("document_guid")
    url             = data.get("url")
    description     = data.get("description")

    # 3) Enforce internal vs external document rules

    # Internal: document_guid != None, url must be None
    # External: url != None, document_guid must be None
    if document_guid and url:
        session.close()
        return jsonify({
            "error": "Invalid document reference: provide EITHER document_guid (internal) OR url (external), not both."
        }), 400

    if not document_guid and not url:
        session.close()
        return jsonify({
            "error": "Invalid document reference: you must provide either document_guid (internal) OR url (external)."
        }), 400

    # Optional / TODO: if internal, you could check that document_guid exists in a 'documents' table
    #if document_guid:
    #    doc = session.query(Document).filter_by(guid=document_guid, project_id=project_id).first()
    #    if not doc:
    #        session.close()
    #        return jsonify({"error": "Internal document not found for given document_guid"}), 400

    # 4) Generate GUID if not provided
    import uuid
    new_guid = body_guid or str(uuid.uuid4())

    # 5) Create and persist DocumentReference
    new_ref = DocumentReference(
        guid=new_guid,
        topic_guid=topic_guid,
        url=url,
        document_guid=document_guid,
        description=description
    )

    session.add(new_ref)
    session.commit()

    # 6) Build response body (BCF style)
    response_body = {
        "guid": new_ref.guid,
        "description": new_ref.description
    }

    # For external document
    if new_ref.url:
        response_body["url"] = new_ref.url

    # For internal document
    if new_ref.document_guid:
        response_body["document_guid"] = new_ref.document_guid

    session.close()
    return jsonify(response_body), 201

#GET Documents Service
@app.route("/bcf/<version>/projects/<project_id>/documents", methods=["GET"])
@require_auth
def get_documents(version, project_id):
    session = Session() #SessionLocal()

    try:
        # (Optional) check project exists
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            session.close()
            return jsonify({"error": "Project not found"}), 404

        docs = session.query(Document).filter_by(project_id=project_id).all()
        result = [d.to_bcf_dict() for d in docs]

        session.close()
        return jsonify(result), 200

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500

#GET Document Service
@app.route("/bcf/<version>/projects/<project_id>/documents/<doc_guid>", methods=["GET"])
@require_auth
def get_document(version, project_id, doc_guid):
    session = Session() #SessionLocal()

    try:
        doc = (
            session.query(Document)
            .filter_by(project_id=project_id, guid=doc_guid)
            .first()
        )

        if not doc:
            session.close()
            return jsonify({"error": "Document not found"}), 404

        file_path = doc.path

        session.close()

        if not os.path.isfile(file_path):
            return jsonify({"error": "Document file not found on server"}), 404

        # let Flask handle Content-Type based on filename
        return send_file(
            file_path,
            as_attachment=True,
            download_name=doc.filename  # Flask >= 2.0
        )

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500

#POST Document Services
# base directory where you want to store uploaded docs
DOCUMENTS_DIR = "/app/data/documents"  # change this
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
@app.route("/bcf/<version>/projects/<project_id>/documents", methods=["POST"])
@require_auth
def post_document(version, project_id):
    session = Session()

    try:
        # (Optional) verify project exists
        project = session.query(Project).filter_by(id=project_id).first()
        if not project:
            session.close()
            return jsonify({"error": "Project not found"}), 404

        # 1) Get optional guid from query param
        requested_guid = request.args.get("guid")

        if requested_guid:
            # Check if already used
            existing = session.query(Document).filter_by(guid=requested_guid).first()
            if existing:
                session.close()
                return jsonify({"error": "Document guid already exists"}), 409
            doc_guid = requested_guid
        else:
            # generate one
            doc_guid = str(uuid.uuid4())

        # 2) Get file from multipart/form-data
        #    Client should send file field named "file" (you can pick another name if you prefer)
        if "file" not in request.files:
            session.close()
            return jsonify({"error": "No file part in request (expected field 'file')"}), 400

        file = request.files["file"]

        if file.filename == "":
            session.close()
            return jsonify({"error": "No selected file"}), 400

        # 3) Decide filename to store / return
        original_filename = file.filename

        # Save path (e.g. /app/data/documents/<guid>_<filename>)
        safe_filename = f"{doc_guid}_{original_filename}"
        file_path = os.path.join(DOCUMENTS_DIR, safe_filename)

        # 4) Save file to disk
        file.save(file_path)

        # 5) Create DB entry
        new_doc = Document(
            guid=doc_guid,
            project_id=project_id,
            filename=original_filename,
            path=file_path,
        )

        session.add(new_doc)
        session.commit()

        response_body = {
            "guid": doc_guid,
            "filename": original_filename,
        }

        session.close()
        return jsonify(response_body), 201

    except Exception as e:
        session.rollback()
        session.close()
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    #return "<h1>BCF API</h1><p>Use <code>/Authentication/login</code> or other endpoints.</p>"
    return send_from_directory("static", "index.html")



if __name__ == "__main__":
    #app.run(debug=True)
    print("🚀 Starting BCF API Server...")
    print(f"🔗 Database URL: {os.getenv('DATABASE_URL', 'postgresql+psycopg2://bcfuser:bcfpass@db:5432/bcfdb')}")
    print(f"🌐 Server will be available at: http://91.99.113.101:5000")
    #app.run(debug=True, host="0.0.0.0", port=5000)
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
    #gunicorn -w 4 -b 0.0.0.0:5000 server:app

