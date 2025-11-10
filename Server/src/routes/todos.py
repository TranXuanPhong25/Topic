from typing import Optional
from pydantic import BaseModel, Field
from todo_manager import todo_manager

from fastapi import HTTPException
from . import todo_router
# ==================== TODO ENDPOINTS ====================

class TodoCreateRequest(BaseModel):
    """Request model for creating a todo"""
    title: str = Field(..., description="Task title", min_length=1)
    description: str = Field(..., description="Task description", min_length=1)
    priority: Optional[str] = Field("medium", description="Priority: urgent/high/medium/low")
    category: Optional[str] = Field("other", description="Category: todo_routerointment/followup/callback/prescription/admin/other")
    assignee: Optional[str] = Field(None, description="Who should handle this task")
    due_hours: Optional[int] = Field(None, description="Hours from now when task is due")


class TodoUpdateRequest(BaseModel):
    """Request model for updating a todo"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    assignee: Optional[str] = None
    status: Optional[str] = None


@todo_router.post("/todos")
async def create_todo(request: TodoCreateRequest):
    """Create a new todo task"""
    result = todo_manager.create_task(
        title=request.title,
        description=request.description,
        priority=request.priority or "medium",
        category=request.category or "other",
        assignee=request.assignee,
        due_hours=request.due_hours,
    )
    
    if result["success"]:
        return {"message": "Todo created", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to create todo"))


@todo_router.get("/todos")
async def get_todos(
    assignee: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    include_completed: bool = False,
):
    """Get all todos with optional filters"""
    todos = todo_manager.get_tasks(
        assignee=assignee,
        status=status,
        priority=priority,
        category=category,
        include_completed=include_completed,
    )
    
    return {
        "message": "Todos retrieved",
        "count": len(todos),
        "todos": todos,
    }


@todo_router.get("/todos/{todo_id}")
async def get_todo(todo_id: int):
    """Get a specific todo by ID"""
    todo = todo_manager.get_task_by_id(todo_id)
    
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} not found")
    
    return {"message": "Todo retrieved", "todo": todo}


@todo_router.put("/todos/{todo_id}")
async def update_todo(todo_id: int, request: TodoUpdateRequest):
    """Update a todo task"""
    result = todo_manager.update_task(
        todo_id=todo_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        category=request.category,
        assignee=request.assignee,
        status=request.status,
    )
    
    if result["success"]:
        return {"message": "Todo updated", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update todo"))


@todo_router.post("/todos/{todo_id}/complete")
async def complete_todo(todo_id: int):
    """Mark a todo as completed"""
    result = todo_manager.complete_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo completed", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to complete todo"))


@todo_router.post("/todos/{todo_id}/cancel")
async def cancel_todo(todo_id: int):
    """Mark a todo as cancelled"""
    result = todo_manager.cancel_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo cancelled", "todo": result["todo"]}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to cancel todo"))


@todo_router.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    """Delete a todo task"""
    result = todo_manager.delete_task(todo_id)
    
    if result["success"]:
        return {"message": "Todo deleted"}
    else:
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete todo"))


@todo_router.get("/todos/overdue")
async def get_overdue_todos(assignee: Optional[str] = None):
    """Get all overdue todos"""
    todos = todo_manager.get_overdue_tasks(assignee=assignee)
    
    return {
        "message": "Overdue todos retrieved",
        "count": len(todos),
        "todos": todos,
    }

