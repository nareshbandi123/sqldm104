from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
ConfigGroup = api.create_model_class(
    "ConfigGroup", {
        "name": True,
        "id": False,
        'project_id': False,
        'configs': False
    }
)
