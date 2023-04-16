from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class TODO(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)


engine = create_engine("postgresql://postgres:postgres@localhost:5432/todo")
Base.metadata.create_all(bind=engine)
session = Session(bind=engine)


app = FastAPI()



app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Don't do this in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your todo list."}


@app.get("/todo", tags=["todos"])
async def get_todos() -> dict:
    todos = session.query(TODO).order_by(TODO.id).all()

    return { "data": todos }


@app.post("/todo", tags=["todos"])
async def add_todo(todo: dict) -> dict:
    new_todo = TODO(item=todo["item"])
    session.add(new_todo)
    session.commit()

    return {
        "data": { "Todo added." }
    }


@app.put("/todo/{id}", tags=["todos"])
async def update_todo(id: int, body: dict) -> dict:
    todo = session.query(TODO).get(id)

    if not todo:
        return {
            "data": f"Todo with id {id} not found."
        }

    todo.item = body["item"]
    session.commit()

    return {
        "data": f"Todo with id {id} has been updated."
    }


@app.delete("/todo/{id}", tags=["todos"])
async def delete_todo(id: int) -> dict:
    session.query(TODO).filter(TODO.id == id).delete()
    session.commit()

    return {
        "data": f"Todo with id {id} not found."
    }
