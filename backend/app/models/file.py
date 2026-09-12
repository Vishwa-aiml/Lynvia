from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    uploader_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    filename = Column(String(255), nullable=False)
    storage_key = Column(String(1024), nullable=True) # E.g., for S3 path
    file_url = Column(String(2048), nullable=False)   # E.g., CDN link or signed URL
    mime_type = Column(String(128), nullable=True)
    file_size = Column(BigInteger, nullable=True)     # In bytes
    
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    # Relationships
    project = relationship("Project", back_populates="files")
    uploader = relationship("User")
