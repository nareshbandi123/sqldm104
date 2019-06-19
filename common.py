import json
import os
import pytest
from src.helpers.api_client import APIClient
from src.models.administration.user import Role, User
from src.models.project.test_cases import AutomationType, Template, TestCase, Type, TestResult
from src.models.administration.plugin import Plugin, UserVariable
from typing import Any, Dict


class Config(dict):
    def __getattr__(self, item):
        return self[item]


def decode_data(path):
    updated_path = path.replace("\'", "\"")
    return json.loads(updated_path, object_hook=object_decoder)


def object_decoder(obj:Any):
    if '__type__' in obj and obj['__type__'] == 'User':
        return User(**obj)
    if '__type__' in obj and obj['__type__'] == 'Role':
        return Role(**obj)
    if '__type__' in obj and obj['__type__'] == 'Plugin':
        return Plugin(**obj)
    if '__type__' in obj and obj['__type__'] == 'UserVariable':
        return UserVariable(**obj)
    if '__type__' in obj and obj['__type__'] == 'TestResult':
        return TestResult(**obj)
    if '__type__' in obj and obj['__type__'] == 'TestCase':
        object = TestCase(**obj)
        object.template = Template(object.template)
        object.type = Type(object.type)
        object.priority = Type(object.priority)
        object.custom_automation_type = AutomationType(object.custom_automation_type)
        return TestCase(**obj)


def merge_configs(first_path, second_path, server=None):
    """Merge two config files, values in the first (which need not exist) take
    priority over values in the second."""
    first_path = os.path.expanduser(first_path)
    if os.path.isfile(first_path):
        initial_config = read_config(first_path)
        second_config = read_config(second_path)

        def merge(first, second):
            for key, value in first.items():
                if isinstance(value, Config):
                    second[key] = merge(value, second.get(key, Config()))
                    continue
                second[key] = value
            return second
        result = merge(initial_config, second_config)

    else:
        result = read_config(second_path)

    if second_path.endswith('data.json'):
        # allow picking the server from the interactive interpreter
        if server is None:
            try:
                server = pytest.config.getoption('server') or result.servers.default
            except AttributeError:
                # pytest.config is absent when you run this code outside of a pytest test run
                server = result.servers.default
        server_data = result.servers[server]
        result['server_name'] = server_data['server_name']
        connection = server_data['database_connection']
        result['database'] = result['database_connection'][connection]
        result['database']['dbtype'] = server_data['database_connection']
    return result


def read_config(path: str) -> Dict[str, Any]:
    with open(path, encoding='utf-8') as f:
        config = json.load(f)

    def configify(config) -> Dict[str, Any]:
        for key, val in config.items():
            if isinstance(val, dict):
                config[key] = configify(val)
            elif isinstance(val, list):
                for i, el in enumerate(val):
                    if isinstance(el, dict):
                        val[i] = configify(el)
        return Config(config)

    return configify(config)


def get_environment_variables():
    HOSTED = False
    ENTERPRISE = False
    TRIAL = False
    if pytest.config.getoption('server') == 'hosted':
        HOSTED = True
    version = read_config('../config/enterprise.json').version
    if 'enterprise' in version:
        ENTERPRISE = True
    if 'trial' in version:
        TRIAL = True

    return HOSTED, ENTERPRISE, TRIAL


def make_client(username, password):
    data = merge_configs('~/testrail.json', '../config/data.json')
    data.login.username = username
    data.login.password = password
    return APIClient(data)
