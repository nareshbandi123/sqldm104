"""Model for audit log row"""


class AuditRecord(object):

    def __init__(self, date, entity_type, entity_id, entity_name, action, author, mode):
        self.date = date
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.entity_name = entity_name
        self.action = action
        self.author = author
        self.mode = mode
