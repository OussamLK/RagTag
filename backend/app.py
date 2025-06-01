import models
import schemata
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Base64Str, Base64Bytes
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("sqlite+pysqlite:///:memory:",
                       echo=True, connect_args={"check_same_thread": False}, poolclass=StaticPool)

models.Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class Embedding(BaseModel):
    pass


app = FastAPI()


@app.post('/documents')
def post_document(file: schemata.CreateDocument, db: Session = Depends(get_session)):
    '''Think of adding pagination to this API, do this right this time.'''
    document = models.Document(**file.model_dump())
    db.add(document)
    db.commit()
    return dict(file_name=file.file_name)


@app.get('/documents')
def get_documents(db: Session = Depends(get_session)):
    documents = db.query(models.Document).all()
    return {"documents": documents}
