from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Case = api.create_model_class(
    "Case", {
        "created_by": False,
        "created_on": False,
        'custom_automation_type': None,
        "custom_checkbox": False,
        "custom_date": False,
        "custom_dropdown": False,
        "custom_expected": False,
        "custom_goals": False,
        "custom_milestone": False,
        "custom_mission": False,
        "custom_preconds": False,
        "custom_steps": False,
        "custom_steps_separated": False,
        "custom_url": False,
        "custom_version": False,
        "custom_status": False,
        "custom_assignee": False,
        "custom_scenario": False,
        "display_order": False,
        "estimate": False,
        "estimate_forecast": False,
        "id": False,
        "milestone_id": False,
        "priority_id": False,
        "refs": False,
        "row_number": False,
        "section_id": False,
        "suite_id": False,
        "display_order": False,
        "title": True,
        "template_id": False,
        "type_id": False,
        "updated_by": False,
        "updated_on": False,
    }
)

CaseType = api.create_model_class(
    "CaseType", {
        "id": False,
        "is_default": False,
        "name": False,
    }
)
