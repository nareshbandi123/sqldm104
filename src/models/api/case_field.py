from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
CaseField = api.create_model_class(
    "CaseField", {
        "configs": False,
        "description": False,
        "display_order": False,
        "id": False,
        "label": True,
        "name": True,
        "system_name": False,
        "type_id": False,
        "type": False,
        "include_all": False,
        "template_ids": False,
        "entity_id": False,
        "location_id": False,
        "is_multi": False,
        "is_active": False,
        "status_id": False,
        "is_system": False,
    }
)

CaseFieldContext = api.create_model_class(
    "CaseFieldContext", {
        "is_global": True,
        "project_ids": False,
    }
)

CaseFieldOptions = api.create_model_class(
    "CaseFieldOptions", {
        "format": False,
        "rows": False,
        "has_expected": False,
        "has_actual": False,
        "is_required": False,
        "items": False,
        "default_value": False,
    }
)