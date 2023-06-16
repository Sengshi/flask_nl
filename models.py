from atexit import register

from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USER = 'postgres'
DB_PASSWORD = 'django'
DB_ADDRESS = 'localhost'
DB_PORT = 5432
DB_NAME = 'nl_flask'
# DB_DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"
DB_DSN = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ADDRESS}:{DB_PORT}/{DB_NAME}"

# Flask
# engine = create_engine(DB_DSN)
# register(engine.dispose)
# Session = sessionmaker(bind=engine)
# session = Session()
# Base = declarative_base()

# AIOHTTP
engine = create_async_engine(DB_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    author = Column(String(50), nullable=False)
    create_date = Column(DateTime, server_default=func.now())

    # def to_json(self):
    #     return {
    #         'id': self.id,
    #         'title': self.title,
    #         'description': self.description,
    #         'author': self.author,
    #         'create_date': self.create_date
    #     }


# Base.metadata.create_all(bind=engine)
