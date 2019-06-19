from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Milestone = api.create_model_class(
    "Milestone", {
        "name": True,
        "description": False,
        "due_on": False,
        "parent_id": False,
        "start_on": False,
        "completed_on": False,
        "id": False,
        "is_completed": False,
        "is_started": False,
        "milestones": False,
        "project_id": False,
        "started_on": False,
        "url": False,
    }
)
