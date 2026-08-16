"""SQLAlchemy models mirroring db/schema.sql.
Run schema.sql directly against Postgres for the pgvector setup;
these models are for querying/inserting from the app layer.
"""
import uuid
from datetime import datetime
 
from sqlalchemy import (
    Column, String, Text, ForeignKey, DateTime, Numeric, Integer,
    ARRAY, Boolean, Date
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
 
Base = declarative_base()
 
 
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    profiles = relationship("Profile", back_populates="user")
 
 
class Profile(Base):
    __tablename__ = "profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    northstar = Column(Text, nullable=False)
    final_idea = Column(Text)
    timeframe = Column(String)
    stage = Column(String)
    priorities = Column(ARRAY(String))
    skills = Column(Text)
    dealbreakers = Column(Text)
    location_pref = Column(String)
    target_types = Column(ARRAY(String))
    is_current = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    user = relationship("User", back_populates="profiles")
 
 
class Listing(Base):
    __tablename__ = "listings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String, nullable=False)
    external_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    org = Column(String, nullable=False)
    type = Column(String, nullable=False)
    location = Column(String)
    description = Column(Text)
    tags = Column(ARRAY(String))
    deadline = Column(Date)
    apply_url = Column(String, nullable=False)
    fetched_at = Column(DateTime, default=datetime.utcnow)
 
 
class MatchScore(Base):
    __tablename__ = "match_scores"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"))
    profile_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id"))
    score_pct = Column(Numeric(5, 2), nullable=False)
    goal_match_tags = Column(ARRAY(String))
    skill_match_tags = Column(ARRAY(String))
    rationale = Column(Text)
    scan_cycle = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
 
class Outcome(Base):
    __tablename__ = "outcomes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"))
    status = Column(String, nullable=False)  # applied/interview/rejected/ghosted/offer
    updated_at = Column(DateTime, default=datetime.utcnow)
 
 
class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text)
    target_stage = Column(Integer, nullable=False)
    status = Column(String, default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)
 
 
class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    listing_id = Column(UUID(as_uuid=True), ForeignKey("listings.id", ondelete="CASCADE"))
    draft_content = Column(Text)
    confidence_pct = Column(Numeric(5, 2))
    status = Column(String, default="pending_review")
    sendable_at = Column(DateTime)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
