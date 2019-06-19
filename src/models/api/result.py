from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Result = api.create_model_class(
    "Result", {
        "assignedto_id": False,
        "comment": False,
        "created_by": False,
        "created_on": False,
        "custom_step_results": False,
        "custom_steps": False,
        "defects": False,
        "elapsed": False,
        "id": False,
        "status_id": False,
        "test_id": False,
        "version": False,
        "attachment_ids": False,
        "id": False,
        "case_id": False,
    }
)
