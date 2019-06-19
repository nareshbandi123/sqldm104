from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Plan = api.create_model_class(
    "Plan", {
        'id': False,
        'name': True,
        'description': False,
        'milestone_id': False,
        'assignedto_id': False,
        'is_completed': False,
        'completed_on': False,
        'passed_count': False,
        'blocked_count': False,
        'untested_count': False,
        'retest_count': False,
        'failed_count': False,
        'custom_status1_count': False,
        'custom_status2_count': False,
        'custom_status3_count': False,
        'custom_status4_count': False,
        'custom_status5_count': False,
        'custom_status6_count': False,
        'custom_status7_count': False,
        'project_id': False,
        'created_on': False,
        'created_by': False,
        'url': False,
        'entries': False
    }
)
