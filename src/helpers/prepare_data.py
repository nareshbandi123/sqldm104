import random
import string

from src.common import merge_configs, decode_data, read_config
from src.pages.administration.project_page import ProjectPage
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.administration.site_settings_page import SiteSettingsPage
from src.pages.project.cases_page import CasesPage
from src.pages.project.plans_page import PlansPage
from src.pages.project.runs_page import RunsPage
from src.pages.project.sections_page import SectionsPage
from src.pages.project.suite_page import SuitePage
from src.pages.project.testcases_page import TestCasesPage
from src.pages.login_page import LoginPage
from src.models.administration.user import RolePermissions
from src.pages.administration.integration_page import IntegrationPage
from src.pages.base_element import BasePageElement


class PrepareData(BasePageElement):
    def __init__(self, driver=None):
        self.driver = driver
        self.project = ProjectPage(driver)
        self.users_roles = UsersRolesPage(driver)
        self.suite = SuitePage(driver)
        self.section = SectionsPage(driver)
        self.tests = TestCasesPage(driver)
        self.run = RunsPage(driver)
        self.plan = PlansPage(driver)
        self.cases = CasesPage(driver)
        self.integration = IntegrationPage(self.driver)
        self.login = LoginPage(self.driver)
        self.site_settings_page = SiteSettingsPage(driver)

        self.t = read_config('../config/tests.json')
        self.data = merge_configs('~/testrail.json', '../config/data.json')
        self.p = read_config('../config/project.json')
        self.runs = read_config('../config/runs.json')
        self.users = read_config('../config/users.json')
        self.plans = read_config('../config/plans.json')
        self.site_settings = read_config('../config/site_settings.json')
        self.plugin = read_config("../config/plugin.json")
        self.sso_settings = read_config('../config/sso_settings.json')

        self.users_overview_url = self.data.server_name + self.users.overview_url

    def add_single_repo_project(self, add_project_url, project_name):
        self.project.open_page(add_project_url)
        project_id = self.project.add_single_repo_project(project_name)
        return project_id

    def add_multi_repo_project(self, add_project_url, project_name):
        self.project.open_page(add_project_url)
        project_id = self.project.add_multi_repo_project(project_name)
        return project_id

    def delete_existing_users(self, users_overview_url, message):
        self.users_roles.open_page(users_overview_url)
        self.users_roles.forget_all_added_users(message)

    def add_multiple_users(self, users, multiple_users_url, message):
        users_to_add = [user.full_name for user in users]
        user_mails = [user.email_address for user in users]
        users_add_str = ''.join([str(name) + ", " + str(email) + "\n" for name, email in zip(users_to_add, user_mails)])
        self.users_roles.open_page(multiple_users_url)
        self.users_roles.add_multiple_users(users_add_str, users, message)
        return users_to_add

    def add_test_cases(self, project_overview_url, suite_url, cases, section_name, message):
        self.suite.open_page(project_overview_url)
        suite_id = self.section.open_test_cases()
        test_case_url = suite_url + suite_id
        self.tests.add_multiple_test(cases, test_case_url, section_name, message)
        return suite_id

    def add_section_with_test_cases_inline(self, project_overview_url, cases_number: int):
        self.suite.open_page(project_overview_url)
        suite_id = self.section.open_test_cases()
        cases = []
        for case in range(0, cases_number):
            case = "TestCase_" + "".join(random.sample((string.ascii_uppercase+string.digits),6))
            cases.append(case)

        self.section.add_first_section(self.p.sections.first_section)
        self.section.press_add_section_button()
        section, section_id = self.section.get_section(self.p.sections.first_section)
        self.tests.press_add_test_inline(str(section_id))
        for case in cases:
            self.tests.add_test_case_inline(str(section_id), case)
            self.tests.confirm_adding_testcase_inline(section)

        return suite_id

    def add_first_section(self, project_overview_url):
        self.suite.open_page(project_overview_url)
        self.section.open_test_cases()
        self.section.add_first_section(self.p.sections.first_section)
        self.section.press_add_section_button()

    def add_test_case_inline(self, project_overview_url, section_name)-> string:
        case_name = "TestCase_" + "".join(random.sample((string.ascii_uppercase + string.digits), 6))
        self.suite.open_page(project_overview_url)
        self.section.open_test_cases()
        section, id = self.section.get_section(section_name)
        self.tests.press_add_test_inline(str(id))
        self.tests.add_test_case_inline(str(id), case_name)
        self.tests.confirm_adding_testcase_inline(section)
        return case_name

    def add_run_outside_plan(self, run_overview_url, run_data, message):
        self.suite.open_page(run_overview_url)
        self.run.click_add_test_run()
        run_id = self.run.add_data_to_run(run_data.name, run_data.description)
        self.suite.validate_success_message(message)
        return run_id

    def add_assignees_to_cases(self, run_view_url, users):
        self.suite.open_page(run_view_url)
        self.cases.add_assignee_to_cases(users)
        self.cases.validate_assignees_to_cases(users)

    def add_plan_with_run(self, run_overview_url, plan_data, message):
        self.suite.open_page(run_overview_url)
        self.plan.click_add_test_plan()
        message = self.plans.messagess.msg_success_added_plan
        plan_id, plan_run_id = self.plan.add_data_to_plan(plan_data.name, plan_data.description, message)
        self.suite.validate_success_message(message)
        return plan_id, plan_run_id

    def add_tester_user(self):
        user = decode_data(str(self.users.regular_user))

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.add_user(user)
        self.users_roles.select_user(self.users.regular_user.full_name)
        self.users_roles.open_access_tab()
        self.users_roles.change_role_for_user("Tester")

    def add_lead_user(self):
        user = decode_data(str(self.users.lead_user))

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.add_user(user)
        self.users_roles.select_user(self.users.lead_user.full_name)
        self.users_roles.open_access_tab()
        self.users_roles.change_role_for_user("Lead")

    def add_tester_user_with_modify_test_results_permission(self):
        user = decode_data(str(self.users.tester_user))

        self.add_role_with_modify_test_results_permission()
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.add_user(user)
        self.users_roles.select_user(self.users.tester_user.full_name)
        self.users_roles.open_access_tab()
        self.users_roles.change_role_for_user("Advanced Tester")

    def add_role_with_modify_test_results_permission(self):
        role = decode_data(str(self.users.roles.tester_role))
        role.permissions = (RolePermissions.RESULTS_ADD | RolePermissions.RESULTS_MODIFY).value

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)
        self.users_roles.check_success_message_displayed()

    def prepare_jira_integration(self):
        message = self.plugin.messages.success_updated_integration_settings
        self.integration.open_page(self.data.server_name + self.plugin.integration_url)
        self.integration.configure_jira_integration(
            self.plugin.jira.address,
            self.plugin.jira.user,
            self.plugin.jira.password
        )
        self.integration.save_settings()
        self.integration.check_success_message(message)

    def remove_integration(self):
        self.integration.open_page(self.data.server_name + self.plugin.integration_url)
        self.integration.clear_integration_settings()

    def login_as_admin(self):
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def login_as_tester(self, check_dashboard=True):
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.users.regular_user.email_address, self.users.regular_user.password, check_dashboard)

    def login_as_lead_user(self):
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.users.lead_user.email_address, self.users.lead_user.password)

    def enable_api(self):
        self.site_settings_page.open_page(self.data.server_name + self.sso_settings.site_settings_url)
        self.site_settings_page.click_api_tab()
        self.site_settings_page.enable_api()