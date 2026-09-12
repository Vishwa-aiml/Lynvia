from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func, Table, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)  # e.g., "logo", "branding", "web-design"
    price = Column(Integer, nullable=False)  # in minor units (paise)
    delivery_days = Column(Integer, nullable=True)  # estimated delivery
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)

    # relationship to designer profile
    designer = relationship("DesignerProfile", back_populates="services")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # designers who have this skill
    designers = relationship("DesignerProfile", secondary="designer_skills", back_populates="skills")


# Association table for designer skills (many-to-many)
designer_skills = Table(
    "designer_skills",
    Base.metadata,
    Column("designer_id", Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
)


class Specialization(Base):
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # e.g., "Tech Startups", "Fashion Brands"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    designer = relationship("DesignerProfile", back_populates="specializations")


class Availability(Base):
    __tablename__ = "availability"

    id = Column(Integer, primary_key=True, index=True)
    designer_id = Column(Integer, ForeignKey("designer_profiles.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    is_available = Column(Boolean, default=True, nullable=False)
    hours_per_day = Column(Integer, nullable=True)  # max hours willing to work
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)

    designer = relationship("DesignerProfile", back_populates="availability")
