from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Template = api.create_model_class(
    "Template", {
        "id": False,
        "is_default": False,
        "name": False,
    }
)