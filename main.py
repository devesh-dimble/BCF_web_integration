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

from bcf.bcfxml import load
from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import insert

# --- SQLAlchemy Models (keep outside the main class) ---
Base = declarative_base()

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(String, primary_key=True)
    project_id = Column(String)
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
