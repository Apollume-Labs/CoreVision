from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.infrastructure.database import Base


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    triton_model_name = Column(String, nullable=False)
    triton_model_version = Column(String, default="1", nullable=False)

    task = Column(String, default="detector", nullable=False)
    labels_file = Column(String, nullable=True)
    input_shape = Column(String, nullable=True)
    parser_type = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Model(id={self.id}, name='{self.name}', triton_model='{self.triton_model_name}')>"
