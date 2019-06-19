from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Priority = api.create_model_class(
    "Priority", {
        "id": False,
        "is_default": False,
        "priority": False,
        "name": False,
        "short_name": False
    }
)