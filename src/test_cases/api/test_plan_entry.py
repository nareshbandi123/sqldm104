import pytest

from src.models.api.plan import Plan
from src.models.api.plan_entry import PlanEntry
from src.models.api.suite import Suite
from src.pages.login_page import LoginPage
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.api.api_page import APIPage
from src.helpers.api_client import APIClient
from src.test_cases.base_test import APIBaseTest
from src.common import read_config, decode_data
from src.models.api.case import Case
from src.models.api.config import Config
from src.models.api.section import Section
from src.helpers.driver_manager import DriverType, DriverManager


@pytest.mark.api
class TestPlanEntry(APIBaseTest):

    suite_mode = 3

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.attachments = read_config('../config/attachments.json')
        cls.users = read_config('../config/users.json')

        cls.client = APIClient(cls.data)
        cls.attachments_page = APIPage()
        cls.users_roles_page = UsersRolesPage(cls.driver)
        cls.login_page = LoginPage(cls.driver)

        cls.prepare_test_case()

    @classmethod
    def prepare_test_case(cls):
        # Add Config Groups and Configs
        cls.add_configs()

        # add test Suite
        suite = Suite(name="Test Suite")
        cls.suite = cls.client.add_suite(suite, cls.project.id)

        # add Section
        section = Section(name="Test Section", suite_id=cls.suite.id)
        section_created = cls.client.add_section(section, cls.project.id)
        cls.section = section_created

        # add test case
        case = Case(title="Test Case")
        cls.case = cls.client.add_case(case, section_created.id)

        # add Test Plan
        plan = Plan(name="Test Plan")
        cls.plan = cls.client.add_plan(plan, cls.project.id)

    def test_add_plan_entry_success(self):
        plan_entry = PlanEntry(
            suite_id=self.suite.id,
            include_all=True,
            case_ids=[self.case.id],
            config_ids=[self.config_ids[0], self.config_ids[1]],
            runs=[{
                "config_ids": [self.config_ids[0]],
                "include_all": True
            }, {
                "config_ids": [self.config_ids[1]],
                "include_all": True
            }],
            name="Windows",
        )
        plan_entry_added = self.client.add_plan_entry(self.plan.id, plan_entry)
        # check runs count
        self.attachments_page.assert_length(plan_entry_added.runs, 2)

        plan_entry = PlanEntry(
            id=plan_entry_added.id,
            name="config has been updated",
            suite_id=self.suite.id,
            config_ids=[self.config_ids[0], self.config_ids[1], self.config_ids[2],
                        self.config_ids[3], self.config_ids[4], self.config_ids[5]]
        )
        updated_plan_entry = self.client.update_plan_entry(self.plan.id, plan_entry)
        # check runs count
        self.attachments_page.assert_length(updated_plan_entry.runs, 9)

    def test_add_plan_entry_with_non_existing_user(self):
        plan_entry = PlanEntry(
            suite_id=self.suite.id,
            include_all=True,
            case_ids=[self.case.id],
            config_ids=[self.config_ids[0], self.config_ids[1]],
            runs=[{
                "config_ids": [self.config_ids[0]],
                "include_all": True
            }, {
                "config_ids": [self.config_ids[1]],
                "include_all": True
            }],
            name="Windows",
            assignedto_id=999
        )

        plan_entry_added_resp = self.client.add_plan_entry(self.plan.id, plan_entry, check_errors=False)

        self.attachments_page.assert_response_code(plan_entry_added_resp, 400)
        self.attachments_page.assert_response_error(plan_entry_added_resp, self.attachments.errors.assignedto_is_not_valid_user)

    def test_add_plan_entry_with_existing_user(self):
        plan_entry = PlanEntry(
            suite_id=self.suite.id,
            include_all=True,
            case_ids=[self.case.id],
            config_ids=[self.config_ids[0], self.config_ids[1]],
            runs=[{
                "config_ids": [self.config_ids[0]],
                "include_all": True
            }, {
                "config_ids": [self.config_ids[1]],
                "include_all": True
            }],
            name="Windows",
            assignedto_id=1
        )

        plan_entry_added_resp = self.client.add_plan_entry(self.plan.id, plan_entry, check_errors=False)
        self.attachments_page.assert_equality(plan_entry_added_resp['response']['runs'][0]['assignedto_id'], plan_entry.assignedto_id)

    def test_add_plan_entry_remove_config(self):
        plan_entry = PlanEntry(
            suite_id=self.suite.id,
            include_all=True,
            case_ids=[self.case.id],
            config_ids=[self.config_ids[0], self.config_ids[1]],
            runs=[{
                "config_ids": [self.config_ids[0]],
                "include_all": True
            }, {
                "config_ids": [self.config_ids[1]],
                "include_all": True
            }],
            name="Windows",
        )
        plan_entry_added = self.client.add_plan_entry(self.plan.id, plan_entry)
        # check runs count
        self.attachments_page.assert_length(plan_entry_added.runs, 2)

        for config_group_id in self.config_group_ids:
            config_group = self.client.get_config_group(config_group_id)
            self.attachments_page.assert_length_equality(config_group.configs, self.groups_configs[config_group.name])

        for idk in self.config_ids:
            deleted_config = self.client.delete_config(idk, check_errors=False)
            self.attachments_page.assert_response_code(deleted_config, 200)

        for config_group_id in self.config_group_ids:
            config_group = self.client.get_config_group(config_group_id)
            self.attachments_page.assert_length(config_group.configs, 0)

    def test_add_non_existing_config(self):
        resp = self.client.add_config(self.config_group_ids[0], Config(name=''), check_errors=False)

        self.attachments_page.assert_response_code(resp, 400)

    def test_0_id_config(self):

        config = Config(name='valid')
        config.id = 0

        resp = self.client.add_config(self.config_group_ids[0], config, check_errors=False)

        self.attachments_page.assert_response_code(resp, 200)

    def test_update_plan_without_permissions(self):
        user = decode_data(str(self.users.regular_user))
        user_overview_url = self.data.server_name + self.users.overview_url
        self.users_roles_page.open_page(user_overview_url)
        self.users_roles_page.add_user(user)

        role = decode_data(str(self.users.roles.no_permissions))

        self.users_roles_page.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles_page.add_role(role)

        self.users_roles_page.open_page(user_overview_url)
        self.users_roles_page.select_user(self.users.regular_user.full_name)

        self.users_roles_page.open_access_tab()
        self.users_roles_page.change_role_for_user(role.name)

        original_username = self.client.client.username
        original_password = self.client.client.password

        self.client.client.username = user.email_address
        self.client.client.password = user.password

        try:
            plan_entry = PlanEntry(
                suite_id=self.suite.id,
                include_all=True,
                case_ids=[self.case.id],
                config_ids=[self.config_ids[0], self.config_ids[1]],
                runs=[{
                    "config_ids": [self.config_ids[0]],
                    "include_all": True
                }, {
                    "config_ids": [self.config_ids[1]],
                    "include_all": True
                }],
                name="Windows",
            )
            resp = self.client.add_plan_entry(self.plan.id, plan_entry, check_errors=False)
            self.attachments_page.assert_response_error(resp, self.attachments.errors.insufficient_permissions_msg)
        finally:
            self.client.client.username = original_username
            self.client.client.password = original_password
