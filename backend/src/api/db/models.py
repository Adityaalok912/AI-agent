from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Project(Base):
    __tablename__ = "projects"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    user_prompt = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    outputs = relationship("AgentOutput", back_populates="project", cascade="all, delete-orphan")


class AgentOutput(Base):
    __tablename__ = "agent_outputs"


    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_name = Column(String(128), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    project = relationship("Project", back_populates="outputs")