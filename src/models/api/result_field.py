from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
ResultField = api.create_model_class(
    "ResultField", {
        # type in add_case_field, type_id in get_case_fields
        "type": False,
        "name": True,
        "label": True,
        "description": False,
        "include_all": False,
        "template_ids": False,
        "configs": False,
        "id": False,
        "system_name": False,
        "entity_id": False,
        "is_multi": False,
        "is_active": False,
        "status_id": False,
        "is_system": False,
        "type_id": False,
        "display_order": False,
        "location_id": False,
    }
)

ResultFieldContext = api.create_model_class(
    "ResultFieldContext", {
        "is_global": True,
        "project_ids": False,
    }
)

ResultFieldOptions = api.create_model_class(
    "ResultFieldOptions", {
        "type": False,
        "is_required": False,
        "default_value": False,
        "items": False,
        "format": False,
        "rows": False,
        "has_expected": False,
    }
)