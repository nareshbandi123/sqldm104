from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
PlanEntry = api.create_model_class(
    "PlanEntry", {
        "case_ids": False,
        "suite_id": False,
        "runs": False,
        "description": False,
        "name": False,
        "include_all": False,
        "config_ids": False,
        "id": False,
        "assignedto_id": False
    }
)
