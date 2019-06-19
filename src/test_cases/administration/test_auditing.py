import datetime
import random
import string

import pytest
import time

from selenium.common.exceptions import WebDriverException

from src.common import read_config, decode_data, get_environment_variables
from src.test_cases.base_test import BaseTest
from src.models.administration.user import User
from src.pages.administration.customizations_page import CustomizationsPage
from src.pages.administration.project_page import ProjectPage
from src.pages.administration.site_settings_page import SiteSettingsPage
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.project.plans_page import PlansPage
import src.pages.project.runs_page as runs_page
from src.pages.project.sections_page import SectionsPage
from src.pages.project.suite_page import SuitePage
from src.pages.project.testcases_page import TestCasesPage
from src.helpers.prepare_data import PrepareData
from src.test_cases.administration.test_customizations import UI_SCRIPT_TEMPLATE

HOSTED, ENTERPRISE, TRIAL = get_environment_variables()


@pytest.mark.skipif(not ENTERPRISE, reason="TestRail is not Enterprise")
class TestAuditingSettings(BaseTest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Prepare page objects
        cls.site_settings_config = read_config('../config/site_settings.json')
        cls.auditing = read_config('../config/auditing.json')
        cls.p = read_config('../config/project.json')
        cls.site_settings = SiteSettingsPage(cls.driver)
        cls.project = ProjectPage(cls.driver)
        cls.site_settings_url = cls.data.server_name + cls.site_settings_config.site_settings_url
        cls.setup_database(cls.auditing)

    def setup_method(self):
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()

    def teardown_method(self):
        self.driver.delete_all_cookies()

    @pytest.mark.testrail(id=5972)
    @pytest.mark.skipif(not HOSTED, reason="TestRail is not Hosted")
    def test_custom_audit_log_retention_control_absence(self):
        self.site_settings.check_custom_audit_log_retention_control_is_not_present()

    @pytest.mark.testrail(id=5973)
    @pytest.mark.skipif(not HOSTED, reason="TestRail is not Hosted")
    def test_custom_audit_log_volume_control_absence(self):
        self.site_settings.check_custom_audit_log_volume_control_is_not_present()

    @pytest.mark.testrail(id=5660)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_control_presence(self):
        self.site_settings.check_custom_audit_log_retention_control_is_present()

    @pytest.mark.testrail(id=5663)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_control_presence(self):
        self.site_settings.check_custom_audit_log_volume_control_is_present()

    @pytest.mark.testrail(id=5967)
    def test_audit_level_is_off_by_default(self):
        self.site_settings.click_save_settings()
        self.site_settings.compare_values(self.site_settings.get_audit_level(), 'Off')
        audit_level_db_value = self.get_setting_value('audit_level')
        self.site_settings.compare_values(audit_level_db_value, '0')

    @pytest.mark.testrail(id=5656)
    def test_change_audit_level_setting(self):
        self.site_settings.set_audit_level("High")
        audit_level_db_value = self.get_setting_value('audit_level')
        self.site_settings.compare_values(audit_level_db_value, '3')

    @pytest.mark.testrail(id=5765)
    def test_audit_number_of_days_default_setting(self):
        self.site_settings.compare_values(self.site_settings.get_number_of_days(), '30 Days')
        db_value = self.get_setting_value('audit_number_of_days')
        self.site_settings.compare_values(db_value, '30')

    @pytest.mark.testrail(id=5659)
    def test_change_audit_number_of_days_setting(self):
        self.site_settings.set_number_of_days('60')
        db_value = self.get_setting_value('audit_number_of_days')
        self.site_settings.compare_values(db_value, '60')
        self.site_settings.compare_values(self.site_settings.get_number_of_days(), '60 Days')

    @pytest.mark.testrail(id=5766)
    def test_audit_number_of_records_default_setting(self):
        self.site_settings.compare_values(self.site_settings.get_number_of_records(), '1 Million')
        db_value = self.get_setting_value('audit_number_of_records')
        self.site_settings.compare_values(db_value, '1000000')

    @pytest.mark.testrail(id=5662)
    def test_change_audit_number_of_records_setting(self):
        self.site_settings.set_number_of_records('5000000')
        db_value = self.get_setting_value('audit_number_of_records')
        self.site_settings.compare_values(db_value, '5000000')
        self.site_settings.compare_values(self.site_settings.get_number_of_records(), '5 Million')

    @pytest.mark.testrail(id=5658)
    def test_audit_rows_per_page_default_setting(self):
        self.site_settings.compare_values(self.site_settings.get_audit_rows_per_page(), '50')
        db_value = self.get_setting_value('audit_rows_per_page')
        self.site_settings.compare_values(db_value, '50')

    @pytest.mark.testrail(id=5657)
    def test_change_audit_rows_per_page_setting(self):
        self.site_settings.set_audit_rows_per_page('60')
        db_value = self.get_setting_value('audit_rows_per_page')
        self.site_settings.compare_values(db_value, '60')
        self.site_settings.compare_values(self.site_settings.get_audit_rows_per_page(), '60')

    @pytest.mark.testrail(id=5968)
    def test_logging_levels_effective_on_log_page_with_level_low(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)
        project_name = self.p.project_info.project_name + "_" + "".join(random.sample((string.ascii_uppercase + string.digits), 6))
        edit_project_url = (self.data.server_name + self.p.edit_project_url)
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.site_settings.set_audit_level("Low")
        self.project.open_page(add_project_url)
        project_id = self.project.add_single_repo_project(project_name)
        self.project.open_page(edit_project_url + project_id)
        self.project.edit_project_name(project_name + " Edited")
        self.project.open_page(projects_overview_url)
        self.project.delete_project(project_name + " Edited")
        self.project.validate_success_message(message)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Project', 'Delete', entity_name=project_name + " Edited")
        self.site_settings.no_log_row_exists('Project', 'Update', position=1, entity_name=project_name + " Edited")
        self.site_settings.no_log_row_exists('Project', 'Create', position=2, entity_name=project_name)

    @pytest.mark.testrail(id=5969)
    def test_logging_levels_effective_on_log_page_with_level_medium(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)
        project_name = self.p.project_info.project_name + "_" + "".join(random.sample((string.ascii_uppercase + string.digits), 6))
        edit_project_url = (self.data.server_name + self.p.edit_project_url)
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.site_settings.set_audit_level("Medium")
        self.project.open_page(add_project_url)
        project_id = self.project.add_single_repo_project(project_name)
        self.project.open_page(edit_project_url + project_id)
        self.project.edit_project_name(project_name + " Edited")
        self.project.open_page(projects_overview_url)
        self.project.delete_project(project_name + " Edited")
        self.project.validate_success_message(message)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Project', 'Delete', entity_name=project_name + " Edited")
        self.site_settings.log_row_exists('Project', 'Update', position=1, entity_name=project_name + " Edited")
        self.site_settings.no_log_row_exists('Project', 'Create', position=2, entity_name=project_name)

    @pytest.mark.testrail(id=5970)
    def test_logging_levels_effective_on_log_page_with_level_off(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)
        project_name = self.p.project_info.project_name + "_" + "".join(random.sample((string.ascii_uppercase + string.digits), 6))
        edit_project_url = (self.data.server_name + self.p.edit_project_url)
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.site_settings.set_audit_level("Off")
        self.project.open_page(add_project_url)
        project_id = self.project.add_single_repo_project(project_name)
        self.project.open_page(edit_project_url + project_id)
        self.project.edit_project_name(project_name + " Edited")
        self.project.open_page(projects_overview_url)
        self.project.delete_project(project_name + " Edited")
        self.project.validate_success_message(message)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.no_log_row_exists('Project', 'Delete', entity_name=project_name + " Edited")
        self.site_settings.no_log_row_exists('Project', 'Update', position=1, entity_name=project_name + " Edited")
        self.site_settings.no_log_row_exists('Project', 'Create', position=2, entity_name=project_name)

    @pytest.mark.testrail(id=5767)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_controls_negative_value(self):
        self.site_settings.set_number_of_records_to_custom()
        self.site_settings.set_custom_number_of_records_to(-1)
        self.site_settings.assert_custom_number_of_records_not_as_entered(-1)

    @pytest.mark.testrail(id=5773)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_controls_wrong_value(self):
        self.site_settings.set_number_of_records_to_custom()
        self.site_settings.set_custom_number_of_records_to('wrong value')
        self.site_settings.assert_custom_number_of_records_not_as_entered('wrong value')
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_audit_record_volume_entered)

    @pytest.mark.testrail(id=5773)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_controls_empty_value(self):
        self.site_settings.set_number_of_records_to_custom()
        self.site_settings.set_custom_number_of_records_to('')
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_audit_record_volume_entered)

    @pytest.mark.testrail(id=5767)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_controls_zero_value(self):
        self.site_settings.set_number_of_records_to_custom()
        self.site_settings.set_custom_number_of_records_to(0)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_audit_record_volume_entered)

    @pytest.mark.testrail(id=5663)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_volume_controls_success(self):
        self.site_settings.set_number_of_records_to_custom()
        self.site_settings.set_custom_number_of_records_to(100000000)
        self.site_settings.click_save_settings()
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()

        db_value = self.get_setting_value('audit_custom_number_of_records')
        self.site_settings.compare_values(db_value, '100000000')
        self.site_settings.check_custom_number_of_records('100000000')

    @pytest.mark.testrail(id=5661)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_controls_negative_value(self):
        self.site_settings.set_number_of_days_to_custom()
        self.site_settings.set_custom_number_of_days_to(-1)
        self.site_settings.assert_custom_number_of_days_not_as_entered(-1)

    @pytest.mark.testrail(id=5772)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_controls_wrong_value(self):
        self.site_settings.set_number_of_days_to_custom()
        self.site_settings.set_custom_number_of_days_to('wrong value')
        self.site_settings.assert_custom_number_of_days_not_as_entered('wrong value')
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_retention_period_entered)

    @pytest.mark.testrail(id=5772)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_controls_empty_value(self):
        self.site_settings.set_number_of_days_to_custom()
        self.site_settings.set_custom_number_of_days_to('')
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_retention_period_entered)

    @pytest.mark.testrail(id=5661)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_controls_zero_value(self):
        self.site_settings.set_number_of_days_to_custom()
        self.site_settings.set_custom_number_of_days_to(0)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.auditing.messages.invalid_custom_retention_period_entered)

    @pytest.mark.testrail(id=5660)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_custom_audit_log_retention_controls_success(self):
        self.site_settings.set_number_of_days_to_custom()
        self.site_settings.set_custom_number_of_days_to(120)
        self.site_settings.click_save_settings()
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()

        db_value = self.get_setting_value('audit_custom_number_of_days')
        self.site_settings.compare_values(db_value, '120')
        self.site_settings.check_custom_number_of_days('120')


@pytest.mark.skipif(not ENTERPRISE, reason="TestRail is not Enterprise")
class TestAuditingLog(BaseTest):


    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Get test data
        cls.site_settings_config = read_config('../config/site_settings.json')
        cls.p = read_config('../config/project.json')
        cls.t = read_config("../config/tests.json")
        cls.runs = read_config('../config/runs.json')
        cls.users = read_config('../config/users.json')
        cls.auditing = read_config('../config/auditing.json')
        cls.customizations = read_config('../config/customizations.json')
        cls.plan_data = read_config('../config/plans.json')

        # Prepare page objects
        cls.site_settings_url = cls.data.server_name + cls.site_settings_config.site_settings_url
        cls.site_settings = SiteSettingsPage(cls.driver)
        cls.project = ProjectPage(cls.driver)
        cls.prepare_data = PrepareData(cls.driver)
        cls.section = SectionsPage(cls.driver)
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.suite = SuitePage(cls.driver)
        cls.runsPage = runs_page.RunsPage(cls.driver)
        cls.test_cases = TestCasesPage(cls.driver)
        cls.customizations_page = CustomizationsPage(cls.driver)
        cls.plans = PlansPage(cls.driver)

        # Add unique run timestamp and string for fields creation/deletion tests
        cls.stamp = int(time.time())
        cls.custom_string = ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

        cls.prepare_for_testing()

    @classmethod
    def prepare_for_testing(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)
        self.project_name = self.p.project_info.project_name + "_" + "".join(random.sample((string.ascii_uppercase + string.digits), 6))

        self.project.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.project_id = self.prepare_data.add_single_repo_project(add_project_url, self.p.project_info.project_name)
        self.project_id_multi = self.prepare_data.add_multi_repo_project(add_project_url, self.project_name)
        self.project.open_page(self.data.server_name + self.p.project_overview_url + self.project_id)
        self.suite_id = self.section.open_test_cases()
        self.suite_id = self.prepare_data.add_section_with_test_cases_inline(self.data.server_name + self.p.project_overview_url + self.project_id, 2)
        self.run_id = self.prepare_data.add_run_outside_plan( self.data.server_name + self.runs.overview_url + self.project_id,self.runs.runs[0],self.runs.messages.msg_success_added_test_run)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()
        self.site_settings.set_audit_level("High")
        self.driver.delete_all_cookies()

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)

        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.project.open_page(projects_overview_url)
        self.project.delete_existing_projects()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data(cls)
        super().teardown_class()

    def setup_method(self):
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def teardown_method(self):
        self.driver.delete_all_cookies()

    @pytest.mark.testrail(id=5864)
    @pytest.mark.dependency(name="test_project_create_appears_in_log")
    def test_project_create_appears_in_log(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)
        pytest.test_project_name = self.p.project_info.project_name + "_" + "".join(
            random.sample((string.ascii_uppercase + string.digits), 6))

        self.project.open_page(add_project_url)
        pytest.test_project_id = self.project.add_single_repo_project(pytest.test_project_name)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Project', 'Create', entity_name=pytest.test_project_name)

    @pytest.mark.testrail(id=5864)
    @pytest.mark.dependency(name="test_project_update_appears_in_log", depends=["test_project_create_appears_in_log"])
    def test_project_update_appears_in_log(self):
        edit_project_url = (self.data.server_name + self.p.edit_project_url + pytest.test_project_id)
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        try:
            self.project.open_page(edit_project_url)
            self.project.edit_project_name(self.p.project_info.project_name_edited)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Project', 'Update', entity_name=self.p.project_info.project_name_edited)
            self.site_settings.log_row_exists('Project', 'Create', position=1, entity_name=pytest.test_project_name)
        except:
            self.project.open_page(projects_overview_url)
            self.project.delete_project(self.p.project_info.project_name)
            self.project.validate_success_message(message)
            raise Exception()

    @pytest.mark.testrail(id=5864)
    @pytest.mark.dependency(depends=["test_project_create_appears_in_log", "test_project_update_appears_in_log"])
    def test_project_delete_appears_in_log(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.project.open_page(projects_overview_url)
        self.project.delete_project(self.p.project_info.project_name_edited)
        self.project.validate_success_message(message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Project', 'Delete', entity_name=self.p.project_info.project_name_edited)
        self.site_settings.log_row_exists('Project', 'Update', position=1, entity_name=self.p.project_info.project_name_edited)
        self.site_settings.log_row_exists('Project', 'Create', position=2, entity_name=pytest.test_project_name)

    @pytest.mark.testrail(id=5868)
    @pytest.mark.dependency(name="test_test_create_appears_in_log")
    def test_test_create_appears_in_log(self):
        self.test_cases.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.test_cases.open_test_case()
        self.test_cases.add_test_result()

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test', 'Update')

    @pytest.mark.testrail(id=5868)
    @pytest.mark.dependency(depends=["test_test_create_appears_in_log"])
    def test_test_update_appears_in_log(self):
        self.test_cases.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.test_cases.open_test_case()
        self.test_cases.edit_result_comment("Edited comment")

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test', 'Update')

    @pytest.mark.testrail(id=5865)
    @pytest.mark.dependency(name="test_suite_create_appears_in_log")
    def test_suite_create_appears_in_log(self):
        name = self.p.suites.add[0].name
        description = self.p.suites.add[0].description
        add_suite = self.data.server_name + self.p.suites.add_url + self.project_id_multi

        self.suite.open_page(add_suite)
        suite_id = self.suite.add_data_to_suite(name, description)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Suite', 'Create', entity_id=suite_id, entity_name=name)

    @pytest.mark.testrail(id=5865)
    @pytest.mark.dependency(name="test_suite_update_appears_in_log", depends=["test_suite_create_appears_in_log"])
    def test_suite_update_appears_in_log(self):
        name = self.p.suites.add[0].name
        new_name =  self.p.suites.edit.name
        description = self.p.suites.edit.description
        suites_overview = self.data.server_name + self.p.suites.overview_url + self.project_id_multi

        try:
            self.suite.open_page(suites_overview)
            suite_id = self.suite.get_suite_id(name)
            self.suite.edit_suite_list(suite_id)
            self.suite.edit_suite(new_name, description)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Suite', 'Update', entity_name=new_name)
            self.site_settings.log_row_exists('Suite', 'Create', entity_name=name, position=1)
        except:
            self.suite.open_page(suites_overview)
            suite_id = self.suite.get_suite_id(name)
            self.suite.edit_suite_list(suite_id)
            self.suite.delete_suite()
            raise Exception()

    @pytest.mark.testrail(id=5865)
    @pytest.mark.dependency(depends=["test_suite_create_appears_in_log", "test_suite_update_appears_in_log"])
    def test_suite_delete_appears_in_log(self):
        name = self.p.suites.add[0].name
        new_name = self.p.suites.edit.name
        suites_overview = self.data.server_name + self.p.suites.overview_url + self.project_id_multi

        self.suite.open_page(suites_overview)
        suite_id = self.suite.get_suite_id(new_name)
        self.suite.edit_suite_list(suite_id)
        self.suite.delete_suite()

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Suite', 'Delete', entity_name=new_name)
        self.site_settings.log_row_exists('Suite', 'Update', entity_name=new_name, position=1)
        self.site_settings.log_row_exists('Suite', 'Create', entity_name=name, position=2)

    @pytest.mark.testrail(id=5867)
    @pytest.mark.dependency(name="test_case_create_appears_in_log")
    def test_case_create_appears_in_log(self):
        TestAuditingLog.case_name = self.prepare_data.add_test_case_inline(self.data.server_name + self.p.project_overview_url + self.project_id, self.p.sections.first_section)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case', 'Create', entity_name=TestAuditingLog.case_name, position=2)
        self.site_settings.log_row_exists('Test Run', 'Update', entity_id=self.run_id, position=1)
        self.site_settings.log_row_exists('Test', 'Create', entity_name=TestAuditingLog.case_name)

    @pytest.mark.testrail(id=5867)
    @pytest.mark.dependency(name="test_case_update_appears_in_log", depends=["test_case_create_appears_in_log"])
    def test_case_update_appears_in_log(self):
        del_message = self.t.messages.msg_success_deleted_test_case

        try:
            self.suite.open_page(self.data.server_name + self.p.suites.overview_url + self.project_id)
            self.test_cases.edit_test_case_title_inline(self.p.sections.first_section, TestAuditingLog.case_name, TestAuditingLog.case_name + " Edited")
            section = self.test_cases.get_section(self.p.sections.first_section)[0]
            self.test_cases.find_nested_element_by_locator_and_value(section, 'link text', TestAuditingLog.case_name + " Edited")

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Case', 'Create', entity_name=TestAuditingLog.case_name, position=3)
            self.site_settings.log_row_exists('Test Run', 'Update', entity_id=self.run_id, position=2)
            self.site_settings.log_row_exists('Test', 'Create', entity_name=TestAuditingLog.case_name, position=1)
            self.site_settings.log_row_exists('Case', 'Update', entity_name=TestAuditingLog.case_name + " Edited")
        except:
            self.suite.open_page(self.data.server_name + self.p.suites.overview_url + self.project_id)
            self.test_casesdelete_test_case(TestAuditingLog.case_name, del_message)
            raise Exception()

    @pytest.mark.testrail(id=5867)
    @pytest.mark.dependency(depends=["test_case_create_appears_in_log", "test_case_update_appears_in_log"])
    def test_case_delete_appears_in_log(self):
        del_message = self.t.messages.msg_success_deleted_test_case

        self.suite.open_page(self.data.server_name + self.p.suites.overview_url + self.project_id)
        self.test_cases.delete_test_case(TestAuditingLog.case_name + " Edited", del_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case', 'Create', entity_name=TestAuditingLog.case_name, position=6)
        self.site_settings.log_row_exists('Test Run', 'Update', entity_id=self.run_id, position=5)
        self.site_settings.log_row_exists('Test', 'Create', entity_name=TestAuditingLog.case_name, position=4)
        self.site_settings.log_row_exists('Case', 'Update', entity_name=TestAuditingLog.case_name + " Edited", position=3)
        self.site_settings.log_row_exists('Test', 'Delete', entity_name=TestAuditingLog.case_name + " Edited", position=2)
        self.site_settings.log_row_exists('Test Run', 'Update', entity_id=self.run_id, position=1)
        self.site_settings.log_row_exists('Case', 'Delete', entity_name=TestAuditingLog.case_name + " Edited", position=0)

    @pytest.mark.testrail(id=5871)
    @pytest.mark.dependency(name="test_test_run_create_appears_in_log")
    def test_test_run_create_appears_in_log(self):
        self.run_id = self.prepare_data.add_run_outside_plan(
            self.data.server_name + self.runs.overview_url + self.project_id, self.runs.runs[0],
            self.runs.messages.msg_success_added_test_run)
        self.suite.validate_success_message(self.runs.messages.msg_success_added_test_run)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test', 'Create', position=0)
        self.site_settings.log_row_exists('Test', 'Create', position=1)
        self.site_settings.log_row_exists('Test Run', 'Create', entity_name=self.runs.runs[0].name, position=2)

    @pytest.mark.testrail(id=5871)
    @pytest.mark.dependency(name="test_test_run_update_appears_in_log", depends=["test_test_run_create_appears_in_log"])
    def test_test_run_update_appears_in_log(self):
        project_overview = self.data.server_name + self.p.project_overview_url + self.project_id
        name = self.runs.runs[1].name

        try:
            self.suite.open_page(project_overview)
            self.suite.go_to_test_run_tab()
            self.suite.edit_test_run(name)
            self.runsPage.validate_success_message(self.runs.messages.msg_success_edited_test_run)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Test Run', 'Update', entity_name=self.runs.runs[1].name, position=0)
            self.site_settings.log_row_exists('Test', 'Create', position=1)
            self.site_settings.log_row_exists('Test', 'Create', position=2)
            self.site_settings.log_row_exists('Test Run', 'Create', entity_name=self.runs.runs[0].name, position=3)
        except:
            self.suite.open_page(project_overview)
            self.suite.go_to_test_run_tab()
            self.suite.delete_test_run()
            self.project.confirm_delete_action()
            raise Exception()

    @pytest.mark.testrail(id=5871)
    @pytest.mark.dependency(depends=["test_test_run_create_appears_in_log", "test_test_run_update_appears_in_log"])
    def test_test_run_delete_appears_in_log(self):
        project_overview = self.data.server_name + self.p.project_overview_url + self.project_id

        self.suite.open_page(project_overview)
        self.suite.go_to_test_run_tab()
        self.suite.delete_test_run()
        self.project.confirm_delete_action()

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test Run', 'Delete', position=0)
        self.site_settings.log_row_exists('Test Run', 'Update', position=1)
        self.site_settings.log_row_exists('Test', 'Create', position=2)
        self.site_settings.log_row_exists('Test', 'Create', position=3)
        self.site_settings.log_row_exists('Test Run', 'Create', position=4)

    @pytest.mark.testrail(id=5870)
    @pytest.mark.dependency(name="test_test_plan_create_appears_in_log")
    def test_test_plan_create_appears_in_log(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id

        self.plans.open_page(add_plan_url)
        pytest.test_plan_id = self.plans.add_plan_simple(plan.name, plan.description)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test Plan', 'Create', entity_name=plan.name)

    @pytest.mark.testrail(id=5870)
    @pytest.mark.dependency(name="test_test_plan_update_appears_in_log",
                            depends=["test_test_plan_create_appears_in_log"])
    def test_test_plan_update_appears_in_log(self):
        plan = self.plan_data.plans[0]
        plans_edit_url = self.data.server_name + self.plan_data.edit_url + pytest.test_plan_id
        edit_message = self.plan_data.messages.msg_success_edited_plan
        plans_overview_url = self.data.server_name + self.runs.overview_url + self.project_id
        delete_message = self.plan_data.messages.msg_success_deleted_plan

        try:
            self.plans.open_page(plans_edit_url)
            self.plans.edit_plan_simple(plan.name + " Edited", plan.description, edit_message)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Test Plan', 'Update', entity_name=plan.name + " Edited")
            self.site_settings.log_row_exists('Test Plan', 'Create', position=1, entity_name=plan.name)
        except:
            self.plans.open_page(plans_overview_url)
            self.plans.delete_plan(plan.name, delete_message)
            raise Exception()

    @pytest.mark.testrail(id=5870)
    @pytest.mark.dependency(depends=["test_test_plan_create_appears_in_log", "test_test_plan_update_appears_in_log"])
    def test_test_plan_delete_appears_in_log(self):
        plan = self.plan_data.plans[0]
        plans_overview_url = self.data.server_name + self.runs.overview_url + self.project_id
        delete_message = self.plan_data.messages.msg_success_deleted_plan

        self.plans.open_page(plans_overview_url)
        self.plans.delete_plan(plan.name + " Edited", delete_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Test Plan', 'Delete', entity_name=plan.name + " Edited")
        self.site_settings.log_row_exists('Test Plan', 'Update', position=1, entity_name=plan.name + " Edited")
        self.site_settings.log_row_exists('Test Plan', 'Create', position=2, entity_name=plan.name)

    @pytest.mark.testrail(id=5861)
    @pytest.mark.dependency(name="test_user_create_appears_in_log")
    def test_user_create_appears_in_log(self):
        user_overview_url = self.data.server_name + self.users.overview_url
        full_name = self.plan_data.add.user_full_name
        email_address = 'user+{}@users.com'.format(int(time.time()))
        password = self.plan_data.add.user_password
        user = User(full_name, email_address, password)

        self.users_roles.open_page(user_overview_url)
        self.users_roles.add_user(user)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('User', 'Create', entity_name=full_name)

    @pytest.mark.testrail(id=5861)
    @pytest.mark.xfail(reason="TR-452")
    @pytest.mark.dependency(name="test_user_update_appears_in_log", depends=["test_user_create_appears_in_log"])
    def test_user_update_appears_in_log(self):
        user_overview_url = self.data.server_name + self.users.overview_url
        full_name = self.plan_data.add.user_full_name
        email_address = self.plan_data.add.user_email_address
        password = self.plan_data.add.user_password
        full_name_edited = full_name + " edited"
        user = User(full_name_edited, email_address, password)

        try:
            self.users_roles.open_page(user_overview_url)
            self.users_roles.select_user(full_name)
            self.users_roles.edit_user(user)
            self.users_roles.click_save_changes()
            self.users_roles.validate_success_message(self.users.messages.msg_success_updated_user)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('User', 'Update', entity_name=full_name_edited)
            self.site_settings.log_row_exists('User', 'Create', entity_name=full_name_edited, position=1)
        except WebDriverException:
            self.users_roles.open_page(user_overview_url)
            self.users_roles.forget_user(full_name)
            raise Exception()

    @pytest.mark.testrail(id=5861)
    @pytest.mark.dependency(name="test_user_set_as_inactive_update_appears_in_log",
                            depends=["test_user_create_appears_in_log", "test_user_update_appears_in_log"])
    def test_user_set_as_inactive_update_appears_in_log(self):
        user_overview_url = self.data.server_name + self.users.overview_url
        full_name = self.plan_data.add.user_full_name
        full_name_edited = full_name + " edited"

        try:
            self.users_roles.open_page(user_overview_url)
            self.users_roles.select_user(full_name_edited)
            self.users_roles.set_as_inactive()
            self.users_roles.click_save_changes()
            self.users_roles.validate_success_message(self.users.messages.msg_success_updated_user)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('User', 'Update', entity_name=full_name_edited)
            self.site_settings.log_row_exists('User', 'Update', entity_name=full_name_edited, position=1)
            self.site_settings.log_row_exists('User', 'Create', entity_name=full_name_edited, position=2)
        except WebDriverException:
            self.users_roles.open_page(user_overview_url)
            self.users_roles.forget_user(full_name_edited)
            raise Exception()

    @pytest.mark.testrail(id=5861)
    @pytest.mark.dependency(depends=["test_user_create_appears_in_log",
                                     "test_user_update_appears_in_log",
                                     "test_user_set_as_inactive_update_appears_in_log"])
    def test_user_forget_update_appears_in_log(self):
        user_overview_url = self.data.server_name + self.users.overview_url
        full_name = self.plan_data.add.user_full_name
        full_name_edited = full_name + " edited"

        self.users_roles.open_page(user_overview_url)
        self.users_roles.apply_filter('all')
        self.users_roles.forget_user(full_name_edited)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('User', 'Update')
        self.site_settings.log_row_exists('User', 'Update', position=1)
        self.site_settings.log_row_exists('User', 'Update', position=2)
        self.site_settings.log_row_exists('User', 'Create', position=3)

        self.site_settings.no_log_row_exists('User', 'Update', entity_name=full_name_edited)
        self.site_settings.no_log_row_exists('User', 'Update', entity_name=full_name_edited, position=1)
        self.site_settings.no_log_row_exists('User', 'Update', entity_name=full_name_edited, position=2)
        self.site_settings.no_log_row_exists('User', 'Create', entity_name=full_name_edited, position=3)

    @pytest.mark.testrail(id=5862)
    @pytest.mark.dependency(name="test_group_create_appears_in_log")
    def test_group_create_appears_in_log(self):
        self.users_roles.open_page(self.data.server_name + self.users.add_group_url)
        self.users_roles.add_group('Test Group Name', 1)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Group', 'Create', entity_name='Test Group Name')

    @pytest.mark.testrail(id=5862)
    @pytest.mark.dependency(name="test_group_update_appears_in_log", depends=["test_group_create_appears_in_log"])
    def test_group_update_appears_in_log(self):
        users_overview_url = self.data.server_name + self.users.overview_url

        try:
            self.users_roles.open_page(users_overview_url)
            self.users_roles.open_groups_tab()
            self.users_roles.open_group('Test Group Name')
            self.users_roles.edit_group('Test Group Name Edited', 1)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Group', 'Update', entity_name='Test Group Name Edited')
            self.site_settings.log_row_exists('Group', 'Create', entity_name='Test Group Name', position=1)
        except WebDriverException:
            self.users_roles.open_page(users_overview_url)
            self.users_roles.open_groups_tab()
            id = self.users_roles.retrieve_id_from_link('Test Group Name')
            self.users_roles.delete_group(id)
            self.users_roles.validate_success_message(self.users.messages.msg_success_deleted_group)
            raise Exception()

    @pytest.mark.testrail(id=5862)
    @pytest.mark.dependency(depends=["test_group_create_appears_in_log", "test_group_update_appears_in_log"])
    def test_group_delete_appears_in_log(self):
        users_overview_url = self.data.server_name + self.users.overview_url

        self.users_roles.open_page(users_overview_url)
        self.users_roles.open_groups_tab()
        id = self.users_roles.retrieve_id_from_link('Test Group Name Edited')
        self.users_roles.delete_group(id)
        self.users_roles.validate_success_message(self.users.messages.msg_success_deleted_group)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Group', 'Delete', entity_name='Test Group Name Edited')
        self.site_settings.log_row_exists('Group', 'Update', entity_name='Test Group Name Edited', position=1)
        self.site_settings.log_row_exists('Group', 'Create', entity_name='Test Group Name', position=2)

    @pytest.mark.testrail(id=5863)
    @pytest.mark.dependency(name="test_role_create_appears_in_log")
    def test_role_create_appears_in_log(self):
        role = decode_data(str(self.users.roles.new_role))

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Role', 'Create', entity_name=role.name)

    @pytest.mark.testrail(id=5863)
    @pytest.mark.dependency(name="test_role_update_appears_in_log", depends=["test_role_create_appears_in_log"])
    def test_role_update_appears_in_log(self):
        role = decode_data(str(self.users.roles.new_role))
        original_role_name = role.name
        role.name = role.name + " Edited"
        users_overview_url = self.data.server_name + self.users.overview_url
        message = self.users.roles.messages.msg_success_role_deleted

        try:
            self.users_roles.open_page(users_overview_url)
            self.users_roles.open_roles_tab()
            self.users_roles.open_role(original_role_name)
            self.users_roles.edit_role(role)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Role', 'Update', entity_name=role.name)
            self.site_settings.log_row_exists('Role', 'Create', entity_name=original_role_name, position=1)
        except:
            self.users_roles.open_page(users_overview_url)
            self.users_roles.open_roles_tab()
            self.users_roles.delete_role(original_role_name)
            self.users_roles.validate_success_message(message)
            raise Exception()

    @pytest.mark.testrail(id=5863)
    @pytest.mark.dependency(depends=["test_role_create_appears_in_log", "test_role_update_appears_in_log"])
    def test_role_delete_appears_in_log(self):
        role = decode_data(str(self.users.roles.new_role))
        original_role_name = role.name
        role.name = role.name + " Edited"
        message = self.users.roles.messages.msg_success_role_deleted
        users_overview_url = self.data.server_name + self.users.overview_url

        self.users_roles.open_page(users_overview_url)
        self.users_roles.open_roles_tab()
        self.users_roles.delete_role(role.name)
        self.users_roles.validate_success_message(message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Role', 'Delete', entity_name=role.name)
        self.site_settings.log_row_exists('Role', 'Update', entity_name=role.name, position=1)
        self.site_settings.log_row_exists('Role', 'Create', entity_name=original_role_name, position=2)

    @pytest.mark.testrail(id=5875)
    @pytest.mark.dependency(name="test_priority_create_appears_in_log")
    def test_priority_create_appears_in_log(self):
        name = self.customizations.add.new_priority_name
        abbreviation = self.customizations.add.new_priority_abbreviation
        added_message = self.customizations.messages.msg_priority_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_priority_url)
        self.customizations_page.add_priority(name, abbreviation, added_message)
        self.customizations_page.check_page(self.customizations.overview_url)
        self.customizations_page.check_priority(name, abbreviation)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Priority', 'Create', entity_name=name)

    @pytest.mark.testrail(id=5875)
    @pytest.mark.dependency(name="test_priority_update_appears_in_log", depends=["test_priority_create_appears_in_log"])
    def test_priority_update_appears_in_log(self):
        name = self.customizations.add.new_priority_name
        edit_name = self.customizations.add.edit_priority_name
        abbreviation = self.customizations.add.new_priority_abbreviation
        edited_message = self.customizations.messages.msg_priority_edited
        deleted_message = self.customizations.messages.msg_priority_deleted

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_priority(name, edit_name, abbreviation, edited_message)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Priority', 'Update', entity_name=edit_name)
            self.site_settings.log_row_exists('Priority', 'Create', position=1, entity_name=name)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_priority(name, deleted_message)
            raise Exception()

    @pytest.mark.testrail(id=5875)
    @pytest.mark.dependency(depends=["test_priority_create_appears_in_log", "test_priority_update_appears_in_log"])
    def test_priority_delete_appears_in_log(self):
        name = self.customizations.add.new_priority_name
        edit_name = self.customizations.add.edit_priority_name
        deleted_message = self.customizations.messages.msg_priority_deleted

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_priority(edit_name, deleted_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Priority', 'Delete', entity_name=edit_name)
        self.site_settings.log_row_exists('Priority', 'Update', position=1, entity_name=edit_name)
        self.site_settings.log_row_exists('Priority', 'Create', position=2, entity_name=name)

    @pytest.mark.testrail(id=5878)
    @pytest.mark.dependency(name="test_ui_script_create_appears_in_log")
    def test_ui_script_create_appears_in_log(self):
        name = self.customizations.add.new_ui_script_name
        script = UI_SCRIPT_TEMPLATE.replace("alert('Test Script');", "").format(name)
        added_message = self.customizations.messages.msg_ui_script_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_ui_script_url)
        self.customizations_page.add_ui_script(script, added_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('UI Script', 'Create', entity_name=name)

    @pytest.mark.testrail(id=5878)
    @pytest.mark.dependency(name="test_ui_script_update_appears_in_log",
                            depends=["test_ui_script_create_appears_in_log"])
    def test_ui_script_update_appears_in_log(self):
        name = self.customizations.add.new_ui_script_name
        edited_message = self.customizations.messages.msg_ui_script_edited
        edit_name = self.customizations.add.edit_ui_script_name
        edit_script = UI_SCRIPT_TEMPLATE.replace("alert('Test Script');", "").format(edit_name)
        deleted_message = self.customizations.messages.msg_ui_script_deleted

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_ui_script(name, edit_script, edited_message)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('UI Script', 'Update', entity_name=edit_name)
            self.site_settings.log_row_exists('UI Script', 'Create', entity_name=name, position=1)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_ui_script(name, deleted_message)
            raise Exception()

    @pytest.mark.testrail(id=5878)
    @pytest.mark.dependency(depends=["test_ui_script_create_appears_in_log", "test_ui_script_update_appears_in_log"])
    def test_ui_script_delete_appears_in_log(self):
        name = self.customizations.add.new_ui_script_name
        edit_name = self.customizations.add.edit_ui_script_name
        deleted_message = self.customizations.messages.msg_ui_script_deleted

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_ui_script(edit_name, deleted_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('UI Script', 'Delete', entity_name=edit_name)
        self.site_settings.log_row_exists('UI Script', 'Update', entity_name=edit_name, position=1)
        self.site_settings.log_row_exists('UI Script', 'Create', entity_name=name, position=2)

    @pytest.mark.testrail(id=5873)
    @pytest.mark.dependency(name="test_case_type_create_appears_in_log")
    def test_case_type_create_appears_in_log(self):
        add_case_type_url = (self.data.server_name + self.customizations.add_case_type_url)
        new_case_type_name = self.customizations.add.new_case_type_name

        self.customizations_page.open_page(add_case_type_url)
        self.customizations_page.new_case_type_name(new_case_type_name)
        self.customizations_page.check_page(self.customizations.overview_url)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case Type', 'Create', entity_name=new_case_type_name)

    @pytest.mark.testrail(id=5873)
    @pytest.mark.dependency(name="test_case_type_update_appears_in_log",
                            depends=["test_case_type_create_appears_in_log"])
    def test_case_type_update_appears_in_log(self):
        case_type_name = self.customizations.add.new_case_type_name
        case_type_new_name = self.customizations.add.edit_case_type_name

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_case_type(case_type_name, case_type_new_name)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Case Type', 'Update', entity_name=case_type_new_name)
            self.site_settings.log_row_exists('Case Type', 'Create', entity_name=case_type_name, position=1)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_case_type(case_type_name)
            raise Exception()

    @pytest.mark.testrail(id=5873)
    @pytest.mark.dependency(depends=["test_case_type_create_appears_in_log", "test_case_type_update_appears_in_log"])
    def test_case_type_delete_appears_in_log(self):
        case_type_name = self.customizations.add.new_case_type_name
        case_type_new_name = self.customizations.add.edit_case_type_name

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_case_type(case_type_new_name)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case Type', 'Delete', entity_name=case_type_new_name)
        self.site_settings.log_row_exists('Case Type', 'Update', entity_name=case_type_new_name, position=1)
        self.site_settings.log_row_exists('Case Type', 'Create', entity_name=case_type_name, position=2)

    @pytest.mark.testrail(id=5874)
    @pytest.mark.dependency(name="test_result_field_create_appears_in_log")
    def test_result_field_create_appears_in_log(self):
        result_field_label = "Custom Field Label {}".format(self.stamp)
        result_field_discription = self.customizations.custom_field.description
        result_field_system_name = "yourock_{}".format(self.custom_string)
        result_field_type = self.customizations.custom_field.edited_type
        success_msg = self.customizations.messages.msg_custom_field_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_result_field_url)
        self.customizations_page.custom_field_add_text_fields(result_field_label, result_field_system_name,result_field_discription)
        self.customizations_page.select_custom_field_type(result_field_type, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Result Field', 'Create', entity_name=result_field_system_name)

    @pytest.mark.testrail(id=5874)
    @pytest.mark.dependency(name="test_result_field_update_appears_in_log",
                            depends=["test_result_field_create_appears_in_log"])
    def test_result_field_update_appears_in_log(self):
        old_label = "Custom Field Label {}".format(self.stamp)
        new_label = "Edited Field {}".format(self.stamp)
        new_description = self.customizations.custom_field.edited_description
        success_msg = self.customizations.messages.msg_custom_field_edited
        result_field_system_name = "yourock_{}".format(self.custom_string)

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_custom_field(old_label, new_label, new_description, success_msg)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Result Field', 'Update', entity_name=result_field_system_name)
            self.site_settings.log_row_exists('Result Field', 'Create', entity_name=result_field_system_name, position=1)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_custom_field(old_label, success_msg)
            raise Exception()

    @pytest.mark.testrail(id=5874)
    @pytest.mark.dependency(depends=["test_result_field_create_appears_in_log",
                                     "test_result_field_update_appears_in_log"])
    def test_result_field_delete_appears_in_log(self):
        result_field_label = "Edited Field {}".format(self.stamp)
        success_msg = self.customizations.messages.msg_custom_field_deleted
        result_field_system_name = "yourock_{}".format(self.custom_string)

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_custom_field(result_field_label, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Result Field', 'Delete', entity_name=result_field_system_name)
        self.site_settings.log_row_exists('Result Field', 'Update', entity_name=result_field_system_name, position=1)
        self.site_settings.log_row_exists('Result Field', 'Create', entity_name=result_field_system_name, position=2)

    @pytest.mark.testrail(id=5872)
    @pytest.mark.dependency(name="test_case_field_create_appears_in_log")
    def test_case_field_create_appears_in_log(self):
        custom_field_label = "Custom Field Label {}".format(self.stamp)
        custom_field_description = self.customizations.custom_field.description
        custom_field_system_name = "yourock_{}".format(self.custom_string)
        custom_field_type = self.customizations.custom_field.edited_type
        success_msg = self.customizations.messages.msg_custom_field_added

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_custom_field_url)
        self.customizations_page.custom_field_add_text_fields(custom_field_label, custom_field_system_name,custom_field_description)
        self.customizations_page.select_custom_field_type(custom_field_type, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case Field', 'Create', entity_name=custom_field_system_name)

    @pytest.mark.testrail(id=5872)
    @pytest.mark.dependency(name="test_case_field_update_appears_in_log",
                            depends=["test_case_field_create_appears_in_log"])
    def test_case_field_update_appears_in_log(self):
        old_label = "Custom Field Label {}".format(self.stamp)
        new_label = "Edited Label {}".format(self.stamp)
        new_description = self.customizations.custom_field.edited_description
        success_msg = self.customizations.messages.msg_custom_field_edited
        case_field_system_name = "yourock_{}".format(self.custom_string)

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_custom_field(old_label, new_label, new_description, success_msg)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Case Field', 'Update', entity_name=case_field_system_name)
            self.site_settings.log_row_exists('Case Field', 'Create', entity_name=case_field_system_name, position=1)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_custom_field(old_label, success_msg)
            raise Exception()

    @pytest.mark.testrail(id=5872)
    @pytest.mark.dependency(depends=["test_case_field_create_appears_in_log", "test_case_field_update_appears_in_log"])
    def test_case_field_delete_appears_in_log(self):
        result_field_label = "Edited Label {}".format(self.stamp)
        success_msg = self.customizations.messages.msg_custom_field_deleted
        case_field_system_name = "yourock_{}".format(self.custom_string)

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_custom_field(result_field_label, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Case Field', 'Delete', entity_name=case_field_system_name)
        self.site_settings.log_row_exists('Case Field', 'Update', entity_name=case_field_system_name, position=1)
        self.site_settings.log_row_exists('Case Field', 'Create', entity_name=case_field_system_name, position=2)

    @pytest.mark.testrail(id=5876)
    @pytest.mark.dependency(name="test_template_create_appears_in_log")
    def test_template_create_appears_in_log(self):
        template_name = self.customizations.add.new_template_name
        success_msg = self.customizations.messages.msg_template_created

        self.customizations_page.open_page(self.data.server_name + self.customizations.add_template_url)
        self.customizations_page.create_new_template(template_name, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Template', 'Create', entity_name=template_name)

    @pytest.mark.testrail(id=5876)
    @pytest.mark.dependency(name="test_template_update_appears_in_log", depends=["test_template_create_appears_in_log"])
    def test_template_update_appears_in_log(self):
        old_template_name = self.customizations.add.new_template_name
        new_template_name = self.customizations.add.edited_template_name
        success_msg = self.customizations.messages.msg_template_updated
        delete_msg = self.customizations.messages.msg_template_deleted

        try:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.edit_template_field(old_template_name, new_template_name, success_msg)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Template', 'Update', entity_name=new_template_name)
            self.site_settings.log_row_exists('Template', 'Create', entity_name=old_template_name, position=1)
        except:
            self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
            self.customizations_page.delete_template(old_template_name, delete_msg)
            raise Exception()

    @pytest.mark.testrail(id=5876)
    @pytest.mark.dependency(depends=["test_template_create_appears_in_log", "test_template_update_appears_in_log"])
    def test_template_delete_appears_in_log(self):
        old_template_name = self.customizations.add.new_template_name
        edited_template_name = self.customizations.add.edited_template_name
        success_msg = self.customizations.messages.msg_template_deleted

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.delete_template(edited_template_name, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Template', 'Delete', entity_name=edited_template_name)
        self.site_settings.log_row_exists('Template', 'Update', entity_name=edited_template_name, position=1)
        self.site_settings.log_row_exists('Template', 'Create', entity_name=old_template_name, position=2)

    @pytest.mark.testrail(id=5877)
    def test_status_update_appears_in_log(self):
        status_name = self.customizations.status.label
        success_msg = self.customizations.messages.msg_status_edited

        self.customizations_page.open_page(self.data.server_name + self.customizations.overview_url)
        self.customizations_page.status_quick_edit(status_name, success_msg)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Status', 'Update')

    @pytest.mark.testrail(id=5866)
    @pytest.mark.dependency(name="test_section_create_appears_in_log")
    def test_section_create_appears_in_log(self):
        add_suite_url = self.data.server_name + self.p.suites.add_url + self.project_id_multi
        suite_name = self.p.suites.suite_name_for_section
        section_name = self.p.sections.first_section

        self.suite.open_page(add_suite_url)
        self.suite.add_data_to_suite(suite_name, 'Description')
        self.section.add_first_section(section_name)
        self.section.press_add_section_button()

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Section', 'Create', entity_name=section_name)

    @pytest.mark.testrail(id=5866)
    @pytest.mark.dependency(name="test_section_update_appears_in_log", depends=["test_section_create_appears_in_log"])
    def test_section_update_appears_in_log(self):
        section_url = self.data.server_name + self.p.suites.overview_url + self.project_id_multi
        edited_section_name = self.p.sections.edited_section
        section_name = self.p.sections.first_section

        try:
            self.section.open_page(section_url)
            self.section.go_to_sections()
            self.section.edit_first_section_name(edited_section_name)
            self.section.verify_new_section_name(edited_section_name)

            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.go_to_auditing_log_tab()
            self.site_settings.log_row_exists('Section', 'Update', entity_name=edited_section_name)
            self.site_settings.log_row_exists('Section', 'Create', entity_name=section_name, position=1)
        except:
            self.section.open_page(section_url)
            self.section.go_to_sections()
            self.section.delete_section(section_name)
            raise Exception()

    @pytest.mark.testrail(id=5866)
    @pytest.mark.dependency(depends=["test_section_create_appears_in_log", "test_section_update_appears_in_log"])
    def test_section_delete_appears_in_log(self):
        section_url = self.data.server_name + self.p.suites.overview_url + self.project_id_multi
        edited_section_name = self.p.sections.edited_section
        section_name = self.p.sections.first_section

        self.section.open_page(section_url)
        self.section.go_to_sections()
        self.section.delete_section(edited_section_name)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.log_row_exists('Section', 'Delete', entity_name=edited_section_name)
        self.site_settings.log_row_exists('Section', 'Update', entity_name=edited_section_name, position=1)
        self.site_settings.log_row_exists('Section', 'Create', entity_name=section_name, position=2)


@pytest.mark.skipif(not ENTERPRISE, reason="TestRail is not Enterprise")
class TestAuditingFilters(BaseTest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.site_settings_config = read_config('../config/site_settings.json')
        cls.auditing_config = read_config('../config/auditing.json')
        cls.site_settings_url = cls.data.server_name + cls.site_settings_config.site_settings_url
        cls.site_settings = SiteSettingsPage(cls.driver)
        cls.setup_database(cls.auditing_config)

    def setup_method(self):
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()

    def teardown_method(self):
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.clear_log_filter()
        self.driver.delete_all_cookies()

    @pytest.mark.testrail(id=7429)
    @pytest.mark.parametrize('entity_type_name', [
        'Project', 'User', 'Group', 'Role', 'Suite', 'Section', 'Case', 'Test', 'Milestone', 'Test Plan', 'Test Run',
        'Case Field', 'Result Field', 'Priority', 'Template', 'Status', 'UI Script', 'Case Type'
    ])
    def test_filter_by_entity_type(self, entity_type_name):
        self.site_settings.open_filters()
        self.site_settings.select_entity_type_filter(entity_type_name)
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering(entity_type_name, 'entity_type')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7445)
    @pytest.mark.parametrize('entity_type_name', [
        'Project', 'User', 'Group', 'Role', 'Suite', 'Section', 'Case', 'Test', 'Milestone', 'Test Plan', 'Test Run',
        'Case Field', 'Result Field', 'Priority', 'Template', 'Status', 'UI Script', 'Case Type'
    ])
    def test_filter_by_entity_type_and_date(self, entity_type_name):
        days = datetime.date.today() - datetime.date(2018, 11, 1)
        # Days amount from current day till date of records
        days_count = int(str(days).split()[0])

        self.site_settings.open_filters()
        self.site_settings.select_entity_type_filter(entity_type_name)
        self.site_settings.select_date_range(days_count)
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering(entity_type_name, 'entity_type')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7446)
    def test_filter_by_date(self):
        self.site_settings.open_filters()
        self.site_settings.select_date_filter('10/1/2018', '11/4/2018')
        self.site_settings.submit_filters()
        self.site_settings.assert_rows_count(2)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7447)
    def test_filter_by_author(self):
        self.site_settings.open_filters()
        self.site_settings.select_author_filter(self.data.login.full_name)
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering(self.data.login.full_name, 'author')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7448)
    def test_filter_by_author_and_date(self):
        self.site_settings.open_filters()
        self.site_settings.select_author_filter(self.data.login.full_name)
        days = datetime.date.today() - datetime.date(2018, 11, 5)
        # Days amount from current day till date of records
        days_count = int(str(days).split()[0])
        self.site_settings.select_date_range(days_count)
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering(self.data.login.full_name, 'author')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7449)
    def test_filter_by_action(self):
        self.site_settings.open_filters()
        self.site_settings.select_action_filter('Delete')
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering('Delete', 'action')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7450)
    def test_filter_by_action_and_date(self):
        self.site_settings.open_filters()
        self.site_settings.select_action_filter('Delete')
        days = datetime.date.today() - datetime.date(2018, 11, 5)
        # Days amount from current day till date of records
        days_count = int(str(days).split()[0])
        self.site_settings.select_date_range(days_count)
        self.site_settings.submit_filters()
        self.site_settings.compare_rows_after_filtering('Delete', 'action')
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7451)
    def test_filter_by_entity_name(self):
        self.site_settings.open_filters()
        self.site_settings.select_entity_name_filter('Hello world')
        self.site_settings.submit_filters()
        self.site_settings.assert_rows_count(4)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7452)
    def test_filter_by_entity_name_and_date(self):
        self.site_settings.open_filters()
        self.site_settings.select_entity_name_filter('Hello world')
        days = datetime.date.today() - datetime.date(2018, 11, 5)
        # Days amount from current day till date of records
        days_count = int(str(days).split()[0])
        self.site_settings.select_date_range(days_count)
        self.site_settings.submit_filters()
        self.site_settings.assert_rows_count(0)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7453)
    def test_filter_by_mode(self):
        self.site_settings.open_filters()
        self.site_settings.select_mode_filter('API')
        self.site_settings.submit_filters()
        self.site_settings.assert_rows_count(2)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7454)
    def test_filter_by_mode_and_date(self):
        self.site_settings.open_filters()
        self.site_settings.select_mode_filter('API')
        days = datetime.date.today() - datetime.date(2018, 11, 5)
        # Days amount from current day till date of records
        days_count = int(str(days).split()[0])
        self.site_settings.select_date_range(days_count)
        self.site_settings.submit_filters()
        self.site_settings.assert_rows_count(0)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7455)
    def test_filter_when_there_is_no_data(self):
        self.site_settings.test_match_any_of_the_above_mode(False)
        self.site_settings.assert_rows_count(0)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7456)
    def test_filter_with_match_any_of_the_above(self):
        self.site_settings.test_match_any_of_the_above_mode()
        self.site_settings.assert_rows_count(7)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=7457)
    def test_filter_with_match_all_of_the_above(self):
        self.site_settings.open_filters()
        self.site_settings.select_action_filter("Create")
        self.site_settings.select_entity_name_filter("te")
        self.site_settings.select_entity_type_filter("Template")
        self.site_settings.select_mode_filter("UI")
        self.site_settings.submit_filters()
        time.sleep(1)
        self.site_settings.log_row_exists("Template", "Create", entity_name="te")
        self.site_settings.assert_rows_count(1)
        self.site_settings.clear_log_filter()

    @pytest.mark.testrail(id=5650)
    def test_export_audit_log_download_tooltip(self):
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()
        self.site_settings.hover_audit_log_download_and_check_tooltip()

    @pytest.mark.testrail(id=5655)
    def test_export_audit_log_download_empty_log(self):
        self.site_settings.test_match_any_of_the_above_mode(False)
        self.site_settings.try_download_audit_log_and_validate()


if __name__ == "__main__":
    pytest.main()
