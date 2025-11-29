"""

from bcf.bcfxml import load
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

# SQLAlchemy setup
Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(String, primary_key=True)
    title = Column(String)
    status = Column(String)
    creation_author = Column(String)
    creation_date = Column(DateTime)
    modified_author = Column(String)
    modified_date = Column(DateTime)
    comments = relationship("Comment", back_populates="topic")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(String, primary_key=True)
    topic_id = Column(String, ForeignKey('topics.id'))
    author = Column(String)
    date = Column(DateTime)
    comment = Column(String)
    topic = relationship("Topic", back_populates="comments")

# Database connection
engine = create_engine("postgresql+psycopg2://bcfuser:bcfpass@localhost:5432/bcfdb")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

#session.query(Comment).delete()
#session.query(Topic).delete()


# Load BCF
with load("DesiteExportBcf_Pillar to big.bcf") as bcfxml:
    for topic_guid, handler in bcfxml.topics.items():
        topic = handler.topic
        print(f"Importing topic: {topic.title}")

        stmt = insert(Topic).values(
            id=topic.guid or str(uuid.uuid4()),
            title=topic.title,
            status=topic.topic_status,
            creation_author=topic.creation_author,
            creation_date=topic.creation_date.to_datetime() if topic.creation_date else None,
            modified_author=topic.modified_author,
            modified_date=topic.modified_date.to_datetime() if topic.modified_date else None
        ).on_conflict_do_update(
            index_elements=['id'],
            set_={
                "title": topic.title,
                "status": topic.topic_status,
                "creation_author": topic.creation_author,
                "creation_date": topic.creation_date.to_datetime() if topic.creation_date else None,
                "modified_author": topic.modified_author,
                "modified_date": topic.modified_date.to_datetime() if topic.modified_date else None
            }
        )
        session.execute(stmt)

        for c in handler.comments:
            # 🗝️ UPSERT for Comment
            stmt = insert(Comment).values(
                id=c.guid or str(uuid.uuid4()),
                topic_id=topic.guid,
                author=c.author,
                date=c.date.to_datetime() if c.date else None,
                comment=c.comment
            ).on_conflict_do_update(
                index_elements=['id'],
                set_={
                    "topic_id": topic.guid,
                    "author": c.author,
                    "date": c.date.to_datetime() if c.date else None,
                    "comment": c.comment
                }
            )
            session.execute(stmt)

session.commit()
print("✅ All topics and comments inserted.")


session.close()
"""

#from bcf.bcfxml import load

from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, JSON, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

# --- SQLAlchemy Models (keep outside the main class) ---
Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(String, primary_key=True)  # projectId
    name = Column(String)
    created_at = Column(DateTime)

    topics = relationship("Topic", backref="project")
    project_actions = Column(JSON, nullable=False, default=list)
    topic_types = relationship("ProjectTopicType", backref="project")
    topic_statuses = relationship("ProjectTopicStatus", backref="project")
    topic_labels = relationship("ProjectTopicLabel", backref="project")
    snippet_types = relationship("ProjectSnippetType", backref="project")
    priorities = relationship("ProjectPriority", backref="project")
    users = relationship("ProjectUser", backref="project")
    stages = relationship("ProjectStage", backref="project")
    project_actions_rel = relationship("ProjectProjectAction", backref="project")
    topic_actions = relationship("ProjectTopicAction", backref="project")
    comment_actions = relationship("ProjectCommentAction", backref="project")
    #extensions = Column(JSON, nullable=True)

    def to_bcf_dict(self, actions=None):
        return {
            "project_id": str(self.id),
            "name": self.name,
            "authorization": {
                "project_actions": self.project_actions or []
            }
        }


class Topic(Base):
    __tablename__ = 'topics'
    guid = Column(String, primary_key=True)  # topic guid
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)

    # core BCF fields
    server_assigned_id = Column(String, nullable=True)
    creation_author = Column(String, nullable=True)
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    topic_type = Column(String, nullable=True)
    topic_status = Column(String, nullable=True)
    title = Column(String, nullable=False)
    priority = Column(String, nullable=True)
    assigned_to = Column(String, nullable=True)

    # JSON fields
    labels = Column(JSON, nullable=False, default=list)       # array of strings
    bim_snippet = Column(JSON, nullable=True)                 # arbitrary JSON
    modified_author = Column(String)
    modified_date = Column(DateTime)
    comments = relationship("Comment", back_populates="topic")
    viewpoints = relationship("Viewpoint", back_populates="topic")

    def to_bcf_dict(self):
        return {
            "guid": self.guid,
            "server_assigned_id": self.server_assigned_id,
            "creation_author": self.creation_author,
            "creation_date": self.creation_date.isoformat() + "Z" if self.creation_date else None,
            "topic_type": self.topic_type,
            "topic_status": self.topic_status,
            "title": self.title,
            "priority": self.priority,
            "labels": self.labels or [],
            "assigned_to": self.assigned_to,
            "bim_snippet": self.bim_snippet,
            "modified_author": self.modified_author,
            "modified_date": self.modified_date.isoformat() + "Z" if self.modified_date else None,
            #"comments": [c.to_bcf_dict() for c in self.comments]
        }


class Comment(Base):
    __tablename__ = "comments"

    guid = Column(String, primary_key=True)  # BCF comment GUID
    topic_guid = Column(
        String,
        ForeignKey("topics.guid"),
        nullable=False
    )

    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    author = Column(String, nullable=False)
    comment = Column(String, nullable=False)

    # NEW:
    modified_author = Column(String, nullable=True)
    modified_date = Column(DateTime, nullable=True)

    topic = relationship("Topic", back_populates="comments")

    def to_bcf_dict(self):
        return {
            "guid": self.guid,
            "date": self.date.isoformat() + "Z" if self.date else None,
            "author": self.author,
            "modified_date": self.modified_date.isoformat() + "Z"
            if self.modified_date
            else None,
            "modified_author": self.modified_author,
            "comment": self.comment,
            "topic_guid": self.topic_guid,
        }

class Viewpoint(Base):
    __tablename__ = "viewpoints"

    guid = Column(String, primary_key=True)            # BCF GUID for viewpoint
    topic_guid = Column(String, ForeignKey("topics.guid"), nullable=False)
    index = Column(Integer, nullable=True)

    perspective_camera = Column(JSON, nullable=True)
    lines = Column(JSON, nullable=True)
    clipping_planes = Column(JSON, nullable=True)

    # snapshot metadata (store type); snapshot_data (base64) optionally saved in DB in bitmaps table or omitted
    snapshot = Column(JSON, nullable=True)   # e.g. {"snapshot_type": "png"}

    # components (selection/coloring/visibility) stored as JSON
    components = Column(JSON, nullable=True)

    # relationship
    topic = relationship("Topic", back_populates="viewpoints")
    bitmaps = relationship("Bitmap", back_populates="viewpoint", cascade="all, delete-orphan")

    def to_bcf_dict(self):
        # bitmaps in response should include guid and meta (no bitmap_data)
        bm_list = []
        for b in (self.bitmaps or []):
            bm_list.append({
                "guid": b.guid,
                "bitmap_type": b.bitmap_type,
                "location": b.location or None,
                "normal": b.normal or None,
                "up": b.up or None,
                "height": b.height
            })

        return {
            "guid": self.guid,
            "index": self.index,
            "perspective_camera": self.perspective_camera,
            "lines": self.lines or [],
            "clipping_planes": self.clipping_planes or [],
            "bitmaps": bm_list,
            "snapshot": {"snapshot_type": (self.snapshot or {}).get("snapshot_type")} if self.snapshot else None,
            # components intentionally omitted from response in example, but we can include if needed
        }


class Bitmap(Base):
    __tablename__ = "bitmaps"

    guid = Column(String, primary_key=True)
    viewpoint_guid = Column(String, ForeignKey("viewpoints.guid"), nullable=False)

    bitmap_type = Column(String, nullable=True)
    # store base64 data as TEXT (simple). For large data consider bytea or external storage.
    bitmap_data = Column(Text, nullable=True)

    # meta as JSON for location/normal/up
    location = Column(JSON, nullable=True)
    normal = Column(JSON, nullable=True)
    up = Column(JSON, nullable=True)
    height = Column(Integer, nullable=True)

    viewpoint = relationship("Viewpoint", back_populates="bitmaps")

class DocumentReference(Base):
    __tablename__ = 'document_references'

    guid = Column(String, primary_key=True)
    topic_guid = Column(String, ForeignKey('topics.guid'))
    url = Column(String)
    document_guid = Column(String)
    description = Column(String)

class Document(Base):
    __tablename__ = "documents"

    guid = Column(String, primary_key=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    filename = Column(String, nullable=False)      # e.g. "LegalRequirements.pdf"
    path = Column(String, nullable=False)          # filesystem path in container/host
    description = Column(String, nullable=True)    # optional

    def to_bcf_dict(self):
        return {
            "guid": self.guid,
            "filename": self.filename,
        }

from sqlalchemy import Integer

class ProjectTopicType(Base):
    __tablename__ = "project_topic_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectTopicStatus(Base):
    __tablename__ = "project_topic_statuses"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectTopicLabel(Base):
    __tablename__ = "project_topic_labels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectSnippetType(Base):
    __tablename__ = "project_snippet_types"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectPriority(Base):
    __tablename__ = "project_priorities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectUser(Base):
    __tablename__ = "project_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectStage(Base):
    __tablename__ = "project_stages"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectProjectAction(Base):
    __tablename__ = "project_project_actions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectTopicAction(Base):
    __tablename__ = "project_topic_actions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)


class ProjectCommentAction(Base):
    __tablename__ = "project_comment_actions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    value = Column(String, nullable=False)

'''# --- Database Connection Setup ---


# --- Main Application Class ---
class BCFImporter:
    def __init__(self, db_url, bcf_path):
        self.db_url = db_url
        self.bcf_path = bcf_path
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def run(self):
        session = self.Session()
        with load(self.bcf_path) as bcfxml:
            for topic_guid, handler in bcfxml.topics.items():
                topic = handler.topic
                print(f"Importing topic: {topic.title}")

        stmt = insert(Topic).values(
            id=topic.guid or str(uuid.uuid4()),
            project_id="123",  # Assuming a static project_id for simplicity ✅ Or get it dynamically if you have it
            title=topic.title,
            status=topic.topic_status,
            creation_author=topic.creation_author,
            creation_date=topic.creation_date.to_datetime() if topic.creation_date else None,
            modified_author=topic.modified_author,
            modified_date=topic.modified_date.to_datetime() if topic.modified_date else None
        ).on_conflict_do_update(
            index_elements=['id'],
            set_={
                "title": topic.title,
                "status": topic.topic_status,
                "creation_author": topic.creation_author,
                "creation_date": topic.creation_date.to_datetime() if topic.creation_date else None,
                "modified_author": topic.modified_author,
                "modified_date": topic.modified_date.to_datetime() if topic.modified_date else None
            }
        )
        session.execute(stmt)

        for c in handler.comments:
            # 🗝️ UPSERT for Comment
            stmt = insert(Comment).values(
                id=c.guid or str(uuid.uuid4()),
                topic_id=topic.guid,
                author=c.author,
                date=c.date.to_datetime() if c.date else None,
                comment=c.comment
            ).on_conflict_do_update(
                index_elements=['id'],
                set_={
                    "topic_id": topic.guid,
                    "author": c.author,
                    "date": c.date.to_datetime() if c.date else None,
                    "comment": c.comment
                }
            )
            session.execute(stmt)

        session.commit()
        print("✅ All topics and comments inserted.")
        session.close()

# --- Entry point ---
if __name__ == "__main__":
    importer = BCFImporter(
        db_url="postgresql+psycopg2://bcfuser:bcfpass@localhost:5432/bcfdb",
        bcf_path="DesiteExportBcf_Pillar to big.bcf"
    )
    importer.run()
'''