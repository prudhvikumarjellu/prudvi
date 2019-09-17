from sqlalchemy import Column, String, BigInteger, Text, Integer, ForeignKey, Float
from sqlalchemy.orm import validates

from app.models import BaseModel

# Base model contains primar key,created at, updated at and deleted at keys
class DownloadData(BaseModel):
    __tablename__ = "download_data"
    file_name = Column(String(500), nullable=True)
    file_length = Column(BigInteger, nullable=True)
    start_time = Column(Float, nullable=True)