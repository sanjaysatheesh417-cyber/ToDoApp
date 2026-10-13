from fastapi import FastAPI

app = FastAPI(
    title = "ToDoApp",
    description = "an app built to store your to do"
)

from db import Base, engine
import models

Base.metadata.create_all(bind=engine)