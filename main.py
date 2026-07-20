from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="In-Memory To-Do List API",
    description="A simple, lightning-fast CRUD API utilizing an in-memory database.",
    version="1.0.0"
)

# --- 1. IN-MEMORY DATABASE SCHEMA ---
# A global Python list serves as our live data store.
# Data clears automatically whenever the server process restarts.
TODO_DATABASE: List[dict] = []
id_counter = 1


# --- 2. PYDANTIC SCHEMAS (DATA VALIDATION) ---
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="The headline of your task.")
    description: Optional[str] = Field(None, max_length=500, description="Detailed context for the task.")
    completed: bool = Field(default=False, description="Status indicating task resolution.")

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int


# --- 3. API ENDPOINTS (CRUD OPERATIONS) ---

@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate):
    """Create a brand new task inside the database storage array."""
    global id_counter
    
    new_todo = todo.model_dump()
    new_todo["id"] = id_counter
    
    TODO_DATABASE.append(new_todo)
    id_counter += 1
    return new_todo


@app.get("/todos", response_model=List[TodoResponse])
def get_all_todos(completed: Optional[bool] = None):
    """Retrieve all stored tasks, with optional server-side filtering by state."""
    if completed is not None:
        return [t for t in TODO_DATABASE if t["completed"] == completed]
    return TODO_DATABASE


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo_by_id(todo_id: int):
    """Retrieve a explicit standalone task from the index array matching the specified ID."""
    for todo in TODO_DATABASE:
        if todo["id"] == todo_id:
            return todo
    raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} was not found.")


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updated_data: TodoUpdate):
    """Locate and update matching item properties with partial/patch request bodies."""
    for todo in TODO_DATABASE:
        if todo["id"] == todo_id:
            update_dict = updated_data.model_dump(exclude_unset=True)
            todo.update(update_dict)
            return todo
            
    raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} was not found.")


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    """Purge target resource indexes completely from the main runtime thread."""
    global TODO_DATABASE
    for index, todo in enumerate(TODO_DATABASE):
        if todo["id"] == todo_id:
            TODO_DATABASE.pop(index)
            return
            
    raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} was not found.")


