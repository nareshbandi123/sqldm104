from src.models import api

# Fields required for creating an entity have a value of True
# Fields that are optional or present only on a newly created
# entity are False.
Attachment = api.create_model_class(
    "Attachment", {
        "attachment_id": True,
    }
)
