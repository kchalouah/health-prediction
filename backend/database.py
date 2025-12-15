from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = "sqlite:///./endpoint.db"

Base = declarative_base()

class EndpointMetric(Base):
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # System Metrics
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    disk_read = Column(Float)
    disk_write = Column(Float)
    net_sent = Column(Float)
    net_recv = Column(Float)
    gpu_usage = Column(Float, default=0.0)
    process_count = Column(Integer)
    
    # Raw JSON backup
    raw_data = Column(JSON)

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    endpoint_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String) # file, process, network
    details = Column(String)
    severity = Column(String)

# Setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
