from enum import Flag


class Users(object):
    def __init__(self):
        self.users = []


class User(object):
    def __init__(self,
                 full_name,
                 email_address,
                 password,
                 id=0,
                 language=None,
                 locale=None,
                 time_zone=None,
                 is_admin=None,
                 status=None,
                 remember_me=None,
                 notifications=None,
                 role=None,
                 is_reset_password_forced=None,
                 last_activity=None,
                 gdpr=None,
                 sso_enabled=0,
                 __type__="User"):
        self.id = id
        self.full_name = full_name
        self.email_address = email_address
        self.password = password
        self.is_admin = is_admin
        self.status = status
        self.remember_meme = remember_me
        self.locale = locale
        self.language = language
        self.notifications = notifications
        self.role = role
        self.time_zone = time_zone
        self.is_reset_password_forced = is_reset_password_forced
        self.last_activity = last_activity
        self.gdpr = gdpr
        self.sso_enabled = sso_enabled


class Role(object):
    def __init__(self,
                 name,
                 id=0,
                 is_default=0,
                 permissions=0,
                 __type__="Role"):
        self.id = id
        self.name = name
        self.is_default = bool(is_default)
        self.permissions = permissions


class RolePermissions(Flag):
    ATTACHMENTS_ADD = 0x00001000
    ATTACHMENTS_DEL = 0x00002000
    CASES_ADD = 0x00000004
    CASES_DEL = 0x00000008
    CONFIGS_ADD = 0x00000400
    CONFIGS_DEL = 0x00000800
    MILESTONES_ADD = 0x00000010
    MILESTONES_DEL = 0x00000020
    RUNS_ADD = 0x00000040
    RUNS_DEL = 0x00000080
    RUNS_CLOSE = 0x00000100
    RUNS_CLOSED_DEL = 0x00040000
    REPORTS_ADD = 0x00004000
    REPORTS_DEL = 0x00008000
    SCHEDULED_REPORTS_ADD = 0x00010000
    SCHEDULED_REPORTS_DEL = 0x00020000
    SUITES_ADD = 0x00000001
    SUITES_DEL = 0x00000002
    RESULTS_ADD = 0x00000200
    RESULTS_MODIFY = 0x00080000
