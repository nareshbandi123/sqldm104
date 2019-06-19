from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Run = api.create_model_class(
    "Run", {
        "assignedto_id": False,
        "blocked_count": False,
        "case_ids": False,
        "completed_on": False,
        "config": False,
        "config_ids": False,
        "created_by": False,
        "created_on": False,
        "custom_status1_count": False,
        "custom_status2_count": False,
        "custom_status3_count": False,
        "custom_status4_count": False,
        "custom_status5_count": False,
        "custom_status6_count": False,
        "custom_status7_count": False,
        "description": False,
        "failed_count": False,
        "id": False,
        "include_all": False,
        "is_completed": False,
        "milestone_id": False,
        "name": False,
        "passed_count": False,
        "plan_id": False,
        "project_id": False,
        "retest_count": False,
        "row_number": False,
        "suite_id": False,
        "untested_count": False,
        "url": False,
    }
)
