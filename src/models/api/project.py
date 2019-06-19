from src.models.api import create_model_class


# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
project_fields = {
    "announcement": True,
    "completed_on": False,
    "id": False,
    "is_completed": False,
    "name": True,
    "show_announcement": True,
    "suite_mode": True,
    "url": False,
}

Project = create_model_class("Project", project_fields)