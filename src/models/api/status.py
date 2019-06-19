from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Status = api.create_model_class(
    "Status", {
        "color_bright": False,
        "color_dark": False,
        "color_medium": False,
        "id": False,
        "is_final": False,
        "is_system": False,
        "is_untested": False,
        "label": False,
        "name": False
    }
)