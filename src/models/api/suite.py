from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Suite = api.create_model_class(
    "Suite", {
        "description": False,
        "id": False,
        "name": True,
        "project_id": False,
        "url": False,
        "is_master": False,
        'is_baseline': False,
        'is_completed': False,
        'completed_on': False,
    }
)
