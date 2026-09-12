from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio_items"

    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    project_reference = Column(String(255), nullable=True)  # optional project info/title
    is_public = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    media = relationship("PortfolioMedia", back_populates="portfolio_item", cascade="all, delete-orphan")
    designer = relationship("DesignerProfile", back_populates="portfolio_items")


class PortfolioMedia(Base):
    __tablename__ = "portfolio_media"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolio_items.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    url = Column(String(2000), nullable=False)
    mime_type = Column(String(100), nullable=True)
    sort_order = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    portfolio_item = relationship("PortfolioItem", back_populates="media")
