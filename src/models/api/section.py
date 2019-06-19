from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Section = api.create_model_class(
    "Section", {
        "depth": False,
        "description": False,
        "display_order": False,
        "id": False,
        "name": True,
        "parent_id": False,
        "suite_id": False
    }
)
