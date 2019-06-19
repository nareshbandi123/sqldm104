from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
_Test = api.create_model_class(
    "Test", {
        "assignedto_id": False,
        "case_id": False,
        "estimate": False,
        "estimate_forecast": False,
        "id": False,
        "milestone_id": False,
        "priority_id": False,
        "refs": False,
        "run_id": False,
        "status_id": False,
        "title": False,
        "type_id": False,
        "template_id": False,
        "custom_automation_type": False,
        'custom_preconds': False,
        'custom_steps': False,
        'custom_expected': False,
        'custom_steps_separated': False,
        'custom_mission': False,
        'custom_goals': False,
    }
)

class Test(_Test):
    # Needed so that pytest won't think this is a test class
    __test__ = False
