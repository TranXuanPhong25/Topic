"""Todo Management System for Medical Clinic"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import and_, or_
from knowledges.database import get_db_context
from models.todo import Todo


class TodoManager:
    """
    Manages todo tasks for clinic staff.
    
    Todos are used for:
    - Appointment reminders
    - Follow-up calls
    - Prescription refills
    - Patient callbacks
    - General clinic tasks
    """
    
    # Priority levels
    PRIORITY_URGENT = "urgent"      # Needs immediate attention
    PRIORITY_HIGH = "high"          # Important, do today
    PRIORITY_MEDIUM = "medium"      # Do soon
    PRIORITY_LOW = "low"            # Can wait
    
    # Task categories
    CATEGORY_APPOINTMENT = "appointment"
    CATEGORY_FOLLOWUP = "followup"
    CATEGORY_CALLBACK = "callback"
    CATEGORY_PRESCRIPTION = "prescription"
    CATEGORY_ADMIN = "admin"
    CATEGORY_OTHER = "other"
    
    # Task statuses
    STATUS_PENDING = "pending"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    
    def create_task(
        self,
        title: str,
        description: str,
        priority: str = PRIORITY_MEDIUM,
        category: str = CATEGORY_OTHER,
        assignee: Optional[str] = None,
        due_hours: Optional[int] = None,
        due_date: Optional[datetime] = None,
        appointment_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new todo task.
        
        Args:
            title: Short task title
            description: Detailed description
            priority: urgent/high/medium/low
            category: appointment/followup/callback/prescription/admin/other
            assignee: Staff member assigned (e.g., "nurse", "receptionist", "Dr. Smith")
            due_hours: Hours from now when task is due (alternative to due_date)
            due_date: Specific due date/time
            appointment_id: Related appointment ID (if applicable)
            session_id: Related chat session ID (if applicable)
            
        Returns:
            Dictionary with success status and created todo
        """
        try:
            # Calculate due date if due_hours provided
            if due_hours and not due_date:
                due_date = datetime.now() + timedelta(hours=due_hours)
            
            # Create todo object
            todo = Todo(
                title=title,
                description=description,
                category=category,
                priority=priority,
                assignee=assignee,
                due_date=due_date,
                appointment_id=appointment_id,
                session_id=session_id,
                status=self.STATUS_PENDING,
            )
            
            # Save to database
            with get_db_context() as db:
                db.add(todo)
                db.commit()
                db.refresh(todo)
                
                return {
                    "success": True,
                    "todo": todo.to_dict(),
                    "message": f"Task created: {title}",
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create task",
            }
    
    def get_tasks(
        self,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        appointment_id: Optional[int] = None,
        session_id: Optional[str] = None,
        due_before: Optional[datetime] = None,
        include_completed: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Get todos matching the specified filters.
        
        Args:
            assignee: Filter by assignee
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            appointment_id: Filter by appointment
            session_id: Filter by chat session
            due_before: Get tasks due before this date
            include_completed: Whether to include completed tasks
            
        Returns:
            List of todo dictionaries
        """
        with get_db_context() as db:
            query = db.query(Todo)
            
            # Apply filters
            if assignee:
                query = query.filter(Todo.assignee == assignee)
            
            if status:
                query = query.filter(Todo.status == status)
            elif not include_completed:
                # By default, exclude completed and cancelled tasks
                query = query.filter(
                    and_(
                        Todo.status != self.STATUS_COMPLETED,
                        Todo.status != self.STATUS_CANCELLED,
                    )
                )
            
            if priority:
                query = query.filter(Todo.priority == priority)
            
            if category:
                query = query.filter(Todo.category == category)
            
            if appointment_id:
                query = query.filter(Todo.appointment_id == appointment_id)
            
            if session_id:
                query = query.filter(Todo.session_id == session_id)
            
            if due_before:
                query = query.filter(Todo.due_date <= due_before)
            
            # Order by priority and due date
            priority_order = {
                self.PRIORITY_URGENT: 0,
                self.PRIORITY_HIGH: 1,
                self.PRIORITY_MEDIUM: 2,
                self.PRIORITY_LOW: 3,
            }
            
            todos = query.all()
            
            # Sort by priority then due date
            todos.sort(
                key=lambda t: (
                    priority_order.get(t.priority, 99),
                    t.due_date if t.due_date else datetime.max,
                )
            )
            
            return [todo.to_dict() for todo in todos]
    
    def get_task_by_id(self, todo_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific todo by ID."""
        with get_db_context() as db:
            todo = db.query(Todo).filter(Todo.id == todo_id).first()
            return todo.to_dict() if todo else None
    
    def update_task(
        self,
        todo_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Update a todo task.
        
        Args:
            todo_id: ID of todo to update
            title: New title (if provided)
            description: New description (if provided)
            priority: New priority (if provided)
            category: New category (if provided)
            assignee: New assignee (if provided)
            status: New status (if provided)
            due_date: New due date (if provided)
            
        Returns:
            Dictionary with success status and updated todo
        """
        try:
            with get_db_context() as db:
                todo = db.query(Todo).filter(Todo.id == todo_id).first()
                
                if not todo:
                    return {
                        "success": False,
                        "error": f"Todo {todo_id} not found",
                    }
                
                # Update fields if provided
                if title is not None:
                    todo.title = title
                if description is not None:
                    todo.description = description
                if priority is not None:
                    todo.priority = priority
                if category is not None:
                    todo.category = category
                if assignee is not None:
                    todo.assignee = assignee
                if status is not None:
                    todo.status = status
                    # Update completion time if completed
                    if status == self.STATUS_COMPLETED:
                        todo.completed_at = datetime.now()
                if due_date is not None:
                    todo.due_date = due_date
                
                todo.updated_at = datetime.now()
                
                db.commit()
                db.refresh(todo)
                
                return {
                    "success": True,
                    "todo": todo.to_dict(),
                    "message": f"Task updated: {todo.title}",
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update task",
            }
    
    def complete_task(self, todo_id: int) -> Dict[str, Any]:
        """Mark a task as completed."""
        return self.update_task(todo_id, status=self.STATUS_COMPLETED)
    
    def cancel_task(self, todo_id: int) -> Dict[str, Any]:
        """Mark a task as cancelled."""
        return self.update_task(todo_id, status=self.STATUS_CANCELLED)
    
    def delete_task(self, todo_id: int) -> Dict[str, Any]:
        """
        Delete a todo task.
        
        Args:
            todo_id: ID of todo to delete
            
        Returns:
            Dictionary with success status
        """
        try:
            with get_db_context() as db:
                todo = db.query(Todo).filter(Todo.id == todo_id).first()
                
                if not todo:
                    return {
                        "success": False,
                        "error": f"Todo {todo_id} not found",
                    }
                
                title = todo.title
                db.delete(todo)
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Task deleted: {title}",
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete task",
            }
    
    def get_overdue_tasks(self, assignee: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all overdue tasks."""
        return self.get_tasks(
            assignee=assignee,
            due_before=datetime.now(),
            include_completed=False,
        )
    
    def get_tasks_due_soon(
        self, hours: int = 24, assignee: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get tasks due within the specified number of hours."""
        return self.get_tasks(
            assignee=assignee,
            due_before=datetime.now() + timedelta(hours=hours),
            include_completed=False,
        )
    
    def create_appointment_reminder(
        self,
        appointment_id: int,
        appointment_date: str,
        appointment_time: str,
        patient_name: str,
    ) -> Dict[str, Any]:
        """
        Create an appointment reminder task.
        This is called automatically when appointments are scheduled.
        
        Args:
            appointment_id: ID of the appointment
            appointment_date: Appointment date (YYYY-MM-DD)
            appointment_time: Appointment time (HH:MM)
            patient_name: Patient's name
            
        Returns:
            Dictionary with success status and created todo
        """
        # Parse appointment datetime
        appt_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%Y-%m-%d %H:%M",
        )
        
        # Set reminder for 24 hours before appointment
        reminder_time = appt_datetime - timedelta(hours=24)
        
        # Create the reminder task
        return self.create_task(
            title=f"Appointment reminder: {patient_name}",
            description=f"Call {patient_name} to confirm appointment on {appointment_date} at {appointment_time}",
            priority=self.PRIORITY_MEDIUM,
            category=self.CATEGORY_APPOINTMENT,
            assignee="receptionist",
            due_date=reminder_time,
            appointment_id=appointment_id,
        )


# Create a singleton instance
todo_manager = TodoManager()


# Function calling wrapper for Gemini
def create_todo_function(
    title: str,
    description: str,
    priority: str = "medium",
    category: str = "other",
    assignee: Optional[str] = None,
    due_hours: Optional[int] = None,
) -> str:
    """
    Wrapper function for Gemini function calling.
    Creates a todo and returns a user-friendly string response.
    """
    result = todo_manager.create_task(
        title=title,
        description=description,
        priority=priority,
        category=category,
        assignee=assignee,
        due_hours=due_hours,
    )
    
    if result["success"]:
        return f"✓ Task created: {title} (Priority: {priority}, Assignee: {assignee or 'unassigned'})"
    else:
        return f"✗ Failed to create task: {result.get('error', 'Unknown error')}"


# Gemini function calling declaration
CREATE_TODO_DECLARATION = {
    "name": "create_todo",
    "description": "Create a todo task for clinic staff (reminders, follow-ups, callbacks, etc.)",
    "parameters": {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short title for the task (e.g., 'Call patient about lab results')",
            },
            "description": {
                "type": "string",
                "description": "Detailed description of what needs to be done",
            },
            "priority": {
                "type": "string",
                "enum": ["urgent", "high", "medium", "low"],
                "description": "Task priority level",
            },
            "category": {
                "type": "string",
                "enum": ["appointment", "followup", "callback", "prescription", "admin", "other"],
                "description": "Task category",
            },
            "assignee": {
                "type": "string",
                "description": "Who should handle this task (e.g., 'nurse', 'receptionist', 'Dr. Smith')",
            },
            "due_hours": {
                "type": "integer",
                "description": "How many hours from now the task is due (e.g., 24 for tomorrow)",
            },
        },
        "required": ["title", "description"],
    },
}
