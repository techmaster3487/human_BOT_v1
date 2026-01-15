from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    ip_address = Column(String)
    user_agent = Column(String)
    device_type = Column(String)
    total_clicks = Column(Integer, default=0)
    status = Column(String, default='active')  # active, completed, failed
    
    events = relationship("Event", back_populates="session")

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # click, page_view, scroll, session_start, etc.
    session_id = Column(String, ForeignKey('sessions.id'))
    ip_address = Column(String)
    data = Column(JSON)  # Flexible storage for event-specific data
    
    session = relationship("Session", back_populates="events")

class IPStats(Base):
    __tablename__ = 'ip_stats'
    
    ip_address = Column(String, primary_key=True)
    proxy_type = Column(String, default='residential')
    country = Column(String, default='US')
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    success_rate = Column(Float, default=1.0)
    reputation_score = Column(Float, default=1.0)
    status = Column(String, default='active')  # active, warning, blocked
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)