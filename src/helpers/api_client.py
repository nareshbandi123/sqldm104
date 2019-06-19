import json

import requests

from src.models.api.config import Config
from src.models.api.config_group import ConfigGroup
from src.models.api.milestone import Milestone
from src.models.api.plan import Plan
from src.models.api.plan_entry import PlanEntry
from src.models.api.attachment import Attachment
from src.models.api.case import Case, CaseType
from src.models.api.case_field import CaseField, CaseFieldContext, CaseFieldOptions
from src.models.api.result import Result
from src.models.api.section import Section
from src.models.api.suite import Suite
from src.models.api.run import Run
from src.models.api.priority import Priority
from src.models.api.project import Project
from src.models.api.result_field import ResultField
from src.models.api.status import Status
from src.models.api.template import Template
from src.models.api.test import Test
from src.models.api.user import User


class APIError(Exception):
    def __init__(self, message, status_code, error_text):
        self.message = message
        self.error_text = error_text
        self.status_code = status_code

        error_message = 'Status code {} : Message {!r} : Error: {!r}'.format(status_code, message, self.error)
        super().__init__(error_message)

    def __repr__(self):
        return 'APIError({!r}, status_code={})'.format(self.message, self.status_code)

    @property
    def error(self):
        try:
            return json.loads(self.error_text)['error']
        except (json.JSONDecodeError, KeyError):
            return self.error_text

class Client(object):
    def __init__(self, config, requester=None):
        self.requester = requester or requests
        self.base_url = config.server_name + config.api_url
        self.username = config.login.username
        self.password = config.login.password

    def send_get(self, endpoint, check_errors=True, params=None):
        auth = (self.username, self.password)
        headers = {'content-type': 'application/json'}
        resp = self.requester.get(self.base_url + endpoint, auth=auth, headers=headers, params=params)
        if check_errors:
            if resp.status_code != 200:
                raise APIError(endpoint, resp.status_code, resp.text)
            try:
                return resp.json()
            except json.JSONDecodeError:
                return resp.text
        else:
            return resp

    def send_post(self, endpoint, obj=None, headers=None, check_errors=True, **kwargs):
        auth = (self.username, self.password)
        headers = headers if headers is not None else {'content-type': 'application/json'}

        kwargs.update(dict(auth=auth, headers=headers))
        if obj is not None:
            kwargs['json'] = self.serialize(obj)

        resp = self.requester.post(self.base_url + endpoint, **kwargs)
        if check_errors:
            if resp.status_code != 200:
                raise APIError(endpoint, resp.status_code, resp.text)
            # Some api calls (like deleting an entity) return an empty body
            if resp.text:
                return resp.json()
        else:
            return {"response": '' if len(resp.text) == 0 else resp.json(),
                    "response_code": resp.status_code}

    def serialize(self, obj):
        if isinstance(obj, dict) and "results" in obj:
            return {"results": [self.serialize(result) for result in obj["results"]]}
        output = {}
        for field in obj.fields:
            value = getattr(obj, field)
            if value is not None:
                output[field] = value
        return output


class APIClient(object):
    def __init__(self, config):
        self.client = Client(config)

    def get_priorities(self):
        response = self.client.send_get('get_priorities')
        return [Priority(**args) for args in response]

    def get_statuses(self):
        response = self.client.send_get('get_statuses')
        return [Status(**args) for args in response]

    def get_templates(self, project_id):
        response = self.client.send_get(f'get_templates/{project_id}')
        return [Template(**args) for args in response]

    def add_project(self, project):
        response = self.client.send_post('add_project', project)
        return Project(**response)

    def get_projects(self):
        response = self.client.send_get('get_projects')
        return [Project(**args) for args in response]

    def get_project(self, id):
        response = self.client.send_get('get_project/{}'.format(id))
        return Project(**response)

    def delete_project(self, project):
        self.client.send_post('delete_project/{}'.format(project.id))

    def update_project(self, project):
        response = self.client.send_post('update_project/{}'.format(project.id), project)
        return Project(**response)

    def add_run(self, run, project_id):
        response = self.client.send_post('add_run/{}'.format(project_id), run)
        return Run(**response)

    def get_run(self, run_id):
        response = self.client.send_get(f'get_run/{run_id}')
        return Run(**response)

    def get_runs(self, project_id, **kwargs):
        response = self.client.send_get(f'get_runs/{project_id}', params=kwargs)
        return [Run(**args) for args in response]

    def update_run(self, run):
        response = self.client.send_post(f'update_run/{run.id}', run)
        return Run(**response)

    def delete_run(self, run):
        self.client.send_post('delete_run/{}'.format(run.id))

    def close_run(self, run):
        response = self.client.send_post('close_run/{}'.format(run.id))
        return Run(**response)

    def add_suite(self, suite, project_id):
        response = self.client.send_post('add_suite/{}'.format(project_id), suite)
        return Suite(**response)

    def get_suite(self, suite_id):
        response = self.client.send_get(f'get_suite/{suite_id}')
        return Suite(**response)

    def get_suites(self, project_id):
        response = self.client.send_get(f'get_suites/{project_id}')
        return [Suite(**args) for args in response]

    def update_suite(self, suite):
        response = self.client.send_post(f'update_suite/{suite.id}', suite)
        return Suite(**response)

    def delete_suite(self, suite):
        self.client.send_post(f'delete_suite/{suite.id}')

    def add_section(self, section, project_id):
        response = self.client.send_post('add_section/{}'.format(project_id), section)
        return Section(**response)

    def get_section(self, section_id):
        response = self.client.send_get(f'get_section/{section_id}')
        return Section(**response)

    def get_sections(self, project_id):
        response = self.client.send_get(f'get_sections/{project_id}')
        return [Section(**args) for args in response]

    def update_section(self, section):
        response = self.client.send_post(f'update_section/{section.id}', section)
        return Section(**response)

    def delete_section(self, section):
        self.client.send_post(f'delete_section/{section.id}')

    def add_milestone(self, milestone, project_id):
        response = self.client.send_post(f'add_milestone/{project_id}', milestone)
        return Milestone(**response)

    def get_milestone(self, milestone_id):
        response = self.client.send_get(f'get_milestone/{milestone_id}')
        return Milestone(**response)

    def get_milestones(self, project_id):
        response = self.client.send_get(f'get_milestones/{project_id}')
        return [Milestone(**args) for args in response]

    def update_milestone(self, milestone):
        response = self.client.send_post(f'update_milestone/{milestone.id}', milestone)
        return Milestone(**response)

    def delete_milestone(self, milestone):
        self.client.send_post(f'delete_milestone/{milestone.id}')

    def add_case(self, case, section_id):
        response = self.client.send_post('add_case/{}'.format(section_id), case)
        return Case(**response)

    def get_case(self, case_id):
        response = self.client.send_get(f'get_case/{case_id}')
        return Case(**response)

    def get_cases(self, project_id, **kwargs):
        response = self.client.send_get(f'get_cases/{project_id}', params=kwargs)
        return [Case(**args) for args in response]

    def update_case(self, case):
        response = self.client.send_post(f'update_case/{case.id}', case)
        return Case(**response)

    def delete_case(self, case):
        self.client.send_post(f'delete_case/{case.id}')

    def get_case_types(self):
        response = self.client.send_get('get_case_types')
        return [CaseType(**args) for args in response]

    def add_result(self, result, test_id):
        response = self.client.send_post(f'add_result/{test_id}', result)
        return Result(**response)

    def add_results(self, results, run_id):
        result_dict = dict(results=results)
        response = self.client.send_post(f'add_results/{run_id}', result_dict)
        return [Result(**args) for args in response]

    def get_results(self, test_id):
        response = self.client.send_get(f'get_results/{test_id}')
        results = []
        for result in response:
            results.append(Result(**result))
        return results

    def get_results_for_case(self, run_id, case_id):
        response = self.client.send_get(f'get_results_for_case/{run_id}/{case_id}')
        results = []
        for result in response:
            results.append(Result(**result))
        return results

    def get_results_for_run(self, run_id):
        response = self.client.send_get(f'get_results_for_run/{run_id}')
        results = []
        for result in response:
            results.append(Result(**result))
        return results

    def add_results_for_cases(self, results, run_id):
        result_dict = dict(results=results)
        response = self.client.send_post(f'add_results_for_cases/{run_id}', result_dict)
        return [Result(**args) for args in response]

    def add_result_for_case(self, result, run_id, case_id):
        response = self.client.send_post(f'add_result_for_case/{run_id}/{case_id}', result)
        return Result(**response)

    def add_attachment_to_result(self, files, result_id, check_errors=True):
        response = self.client.send_post('add_attachment_to_result/{}'.format(result_id), headers={}, files=files, check_errors=check_errors)
        if 'response_code' in response.keys():
            return response['response'], response['response_code']
        else:
            return Attachment(**response), 200

    def add_attachment_to_results(self, files, run_id, check_errors=True):
        response = self.client.send_post(f'add_attachment_to_result/{run_id}', headers={}, files=files, check_errors=check_errors)
        if 'response_code' in response.keys():
            return Attachment(**response['response']), response['response_code']
        else:
            return Attachment(**response), 200

    def get_attachment(self, attachment_id):
        response = self.client.send_get('get_attachment/{}'.format(attachment_id))
        return response

    def add_attachment_to_result_for_case(self, files, result_id, case_id, check_errors=True):
        response = self.client.send_post('add_attachment_to_result_for_case/{}/{}'.format(result_id, case_id), headers={}, files=files, check_errors=check_errors)
        if 'response_code' in response.keys():
            return response['response'], response['response_code']
        else:
            return Attachment(**response), 200

    def add_attachment_to_results_for_cases(self, files, run_id, check_errors=True):
        response = self.client.send_post(f'add_attachment_to_results_for_cases/{run_id}', headers={}, files=files, check_errors=check_errors)
        if 'response_code' in response.keys():
            return response['response'], response['response_code']
        else:
            return Attachment(**response), 200

    def get_attachments_for_case(self, case_id):
        response = self.client.send_get('get_attachments_for_case/{}'.format(case_id))
        return response

    def get_attachments_for_test(self, test_id):
        response = self.client.send_get('get_attachments_for_test/{}'.format(test_id))
        return response

    def delete_attachment(self, attachment_id):
        response = self.client.send_post('delete_attachment/{}'.format(attachment_id))
        return response

    def add_plan(self, plan, project_id):
        response = self.client.send_post('add_plan/{}'.format(project_id), plan)
        return Plan(**response)

    def get_plan(self, plan_id):
        response = self.client.send_get('get_plan/{}'.format(plan_id))
        return Plan(**response)

    def get_plans(self, project_id):
        response = self.client.send_get('get_plans/{}'.format(project_id))
        return [Plan(**args) for args in response]

    def update_plan(self, plan):
        response = self.client.send_post(f'update_plan/{plan.id}', plan)
        return Plan(**response)

    def close_plan(self, plan):
        response = self.client.send_post(f'close_plan/{plan.id}')
        return Plan(**response)

    def delete_plan(self, plan):
        self.client.send_post(f'delete_plan/{plan.id}')

    def add_plan_entry(self, plan_id, plan_entry, check_errors=True):
        response = self.client.send_post('add_plan_entry/{}'.format(plan_id), plan_entry, check_errors=check_errors)
        if 'response_code' in response.keys():
            return response
        else:
            return PlanEntry(**response)

    def update_plan_entry(self, plan_id, plan_entry):
        response = self.client.send_post('update_plan_entry/{}/{}'.format(plan_id, plan_entry.id), plan_entry)
        return PlanEntry(**response)

    def delete_plan_entry(self, plan_id, entry_id):
        self.client.send_post(f'delete_plan_entry/{plan_id}/{entry_id}')

    def add_config_group(self, project_id, group):
        response = self.client.send_post('add_config_group/{}'.format(project_id), group)
        return ConfigGroup(**response)

    def add_config(self, config_group_id, config, check_errors=True):
        response = self.client.send_post('add_config/{}'.format(config_group_id), config, check_errors=check_errors)
        if 'response_code' in response.keys():
            return response
        else:
            return Config(**response)

    def update_config(self, config):
        response = self.client.send_post(f'update_config/{config.id}', config)
        return Config(**response)

    def delete_config(self, config_id, check_errors=True):
        response = self.client.send_post(f'delete_config/{config_id}', check_errors=check_errors)
        return response

    def get_configs(self, project_id):
        response = self.client.send_get(f'get_configs/{project_id}')
        config_groups = [ConfigGroup(**args) for args in response]
        for group in config_groups:
            configs = list(group.configs)
            group.configs = [Config(**args) for args in configs]
        return config_groups

    def get_config_group(self, config_group_id, check_errors=True):
        response = self.client.send_get(f'get_config_group/{config_group_id}', check_errors=check_errors)
        return ConfigGroup(**response)

    def delete_config_group(self, config_group_id):
        self.client.send_post(f'delete_config_group/{config_group_id}')

    def update_config_group(self, config_group):
        response = self.client.send_post(f'update_config_group/{config_group.id}', config_group)
        return ConfigGroup(**response)

    def get_reports(self, project_id):
        reports = self.client.send_get('get_reports/{}'.format(project_id))
        return reports

    def run_report(self, report_id):
        response = self.client.send_get('run_report/{}'.format(report_id))
        return response

    def get_test(self, test_id):
        response = self.client.send_get(f'get_test/{test_id}')
        return Test(**response)

    def get_tests(self, run_id):
        response = self.client.send_get(f'get_tests/{run_id}')
        return [Test(**args) for args in response]

    def get_user(self, user_id):
        response = self.client.send_get(f'get_user/{user_id}')
        return User(**response)

    def get_user_by_email(self, email):
        response = self.client.send_get(f'get_user_by_email&email={email}')
        return User(**response)

    def get_users(self):
        response = self.client.send_get('get_users')
        return [User(**args) for args in response]

    def get_case_fields(self):
        response = self.client.send_get('get_case_fields')
        return [_make_case_field(args) for args in response]

    def add_case_field(self, case_field):
        configs = case_field.configs
        case_field.configs = []
        try:
            if configs is not None:
                for config in configs:
                    case_field.configs.append({
                        "context": self.client.serialize(config['context']),
                        "options": self.client.serialize(config['options']),
                    })
            response = self.client.send_post('add_case_field', case_field)
            return _make_case_field(response)
        finally:
            # restore the original object
            case_field.configs = configs

    def get_result_fields(self):
        response = self.client.send_get('get_result_fields')
        return [ResultField(**args) for args in response]

def _make_case_field(args):
    case_field = CaseField(**args)
    raw_configs = case_field.configs
    if isinstance(raw_configs, str):
        configs = json.loads(raw_configs)
    else:
        configs = raw_configs
    case_field.configs = []
    for config in configs:
        case_field.configs.append({
            "context": CaseFieldContext(**config['context']),
            "options": CaseFieldOptions(**config['options']),
        })
    return case_field
