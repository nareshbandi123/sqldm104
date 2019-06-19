from typing import TypeVar

class Plugin(object):

    def __init__(self,
                 plugin_name,
                 user_variable_username,
                 user_variable_password,
                 defect_view_url=None,
                 defect_add_url=None,
                 defect_plugin=None,
                 __type__="Plugin"):
        self.plugin_name = plugin_name
        self.defect_view_url = defect_view_url
        self.defect_add_url = defect_add_url
        self.defect_plugin = defect_plugin
        self.user_variable_username = user_variable_username
        self.user_variable_password = user_variable_password

class UserVariable(object):
    def __init__(self,
                 user_label=None,
                 user_description=None,
                 user_system_name=None,
                 user_type=None,
                 user_fallback=None,
                 __type__="UserVariable"
                 ):
        self.user_label = user_label
        self.user_description = user_description
        self.user_system_name = user_system_name
        self.user_type = user_type
        self.user_fallback = user_fallback