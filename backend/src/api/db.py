import os

import sqlmodel
from sqlmodel import Session, SQLModel

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise NotImplementedError("DATABASE_URL is not set")

DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

engine = sqlmodel.create_engine(DATABASE_URL)


# database models
# does not create db migrations
def init_db():
    SQLModel.metadata.create_all(engine)

# api routes
def get_session():
    with Session(engine) as session:
        yield session