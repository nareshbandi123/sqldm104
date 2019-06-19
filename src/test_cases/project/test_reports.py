import pytest

import src.pages.administration.project_page as project_page
from src.helpers.api_client import APIClient
from src.common import read_config, decode_data, merge_configs
from src.helpers.prepare_data import PrepareData
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.project import reports_page
from src.pages.administration import site_settings_page as site_settings
from src.test_cases.base_test import BaseTest


# @pytest.mark.skip("until feature release")
class TestReports(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Get test data
        cls.p = read_config('../config/project.json')
        cls.reports = read_config("../config/reports.json")
        cls.sso_settings = read_config('../config/sso_settings.json')
        cls.users = read_config('../config/users.json')
        cls.site_settings_config = read_config('../config/site_settings.json')

        cls.client = APIClient(cls.data)

        # Prepare page objects
        cls.project = project_page.ProjectPage(cls.driver)
        cls.reports_page = reports_page.ReportsPage(cls.driver)
        cls.site_settings = site_settings.SiteSettingsPage(cls.driver)
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.prepare_data = PrepareData(cls.driver)

        cls.site_settings_url = cls.data.server_name + cls.sso_settings.site_settings_url
        cls.users_overview_url = cls.data.server_name + cls.users.overview_url

        # Perquisites for tests execution
        cls.setup_database(cls.reports)
        cls.prepare_for_testing(cls)

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data(cls)
        super().teardown_class()

    def setup_method(self):
        self.reports_page.open_page(self.data.server_name + self.reports.overview_url + self.project_id)

    def prepare_for_testing(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)

        self.project.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.project.open_page(add_project_url)
        self.project_id = self.project.add_single_repo_project(self.p.project_info.project_name)
        self.prepare_data.add_tester_user()

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.project.open_page(projects_overview_url)
        self.project.delete_project(self.p.project_info.project_name)
        self.project.validate_success_message(message)

    def test_get_reports_without_reports_existing(self):
        reports = self.client.get_reports(self.project_id)
        self.reports_page.check_reports_length(reports, 0)

    def test_create_new_report_template(self):
        self.reports_page.open_page(self.data.server_name + self.reports.reports.property_distribution.format(self.project_id))
        self.reports_page.check_schedule_on_demand_via_api()
        self.reports_page.click_add_report()
        self.reports_page.check_api_template_appears_on_the_page(self.reports.template_title.property_distribution)
        self.reports_page.validate_success_message(self.reports.messages.reports_templates_success_add)

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_edit_report_template(self):
        self.reports_page.edit_report_template_by_title(self.reports.template_title.property_distribution)
        self.reports_page.change_name(self.reports.report.new_name)
        self.reports_page.validate_success_message(self.reports.messages.reports_templates_success_update)
        self.reports_page.open_page(self.data.server_name + self.reports.overview_url + self.project_id)
        self.reports_page.check_api_template_appears_on_the_page(self.reports.report.new_name)

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_verify_api_on_demand_disabled_and_selected(self):
        self.reports_page.open_page(self.data.server_name + self.reports.overview_url + self.project_id)
        self.reports_page.edit_report_template_by_title(self.reports.report.new_name)
        self.reports_page.check_api_on_demand_checkbox_disabled_and_selected()

    def test_get_reports_with_api_disabled(self):
        try:
            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.click_api_tab()
            self.site_settings.disable_api()
            self.reports_page.expect_to_raise_exception(
                self.client.get_reports, [0],
                403,
                self.reports.errors.disabled_api)
        finally:
            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.click_api_tab()
            self.site_settings.enable_api()

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_get_reports_success(self):
        reports = self.client.get_reports(self.project_id)

        self.reports_page.check_reports_length(reports, 1)
        self.reports_page.expect_report_contents_check(reports[0])

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_run_report_success(self):
        reports = self.client.get_reports(self.project_id)
        report_id = reports[0]['id']
        resp = self.client.run_report(report_id)
        self.reports_page.check_report_links_in_response(resp)

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_run_report_without_permission_to_create(self):
        role_name = "Read-only"
        self.client.client.username = self.users.regular_user.email_address
        self.client.client.password = self.users.regular_user.password

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.select_user(self.users.regular_user.full_name)
        self.users_roles.open_access_tab()
        self.users_roles.change_role_for_user(role_name)
        reports = self.client.get_reports(self.project_id)
        report_id = reports[0]['id']
        self.reports_page.expect_to_raise_exception(
            self.client.run_report, [report_id],
            403,
            self.reports.errors.insufficient_permissions
        )

    @pytest.mark.run(depends=['test_create_new_report_template'])
    def test_delete_report_template(self):
        self.reports_page.open_page(self.data.server_name + self.reports.overview_url + self.project_id)
        self.reports_page.delete_report(self.reports.report.new_name)
        self.reports_page.open_page(self.data.server_name + self.reports.overview_url + self.project_id)
        self.reports_page.verify_deletion_of_report(self.reports.report.new_name)

    def test_get_reports_with_project_id_0(self):
        self.reports_page.expect_to_raise_exception(
            self.client.get_reports, [0],
            400,
            self.reports.errors.field_project_id_is_not_valid
        )

    def test_get_reports_unknown_project_id(self):
        self.reports_page.expect_to_raise_exception(
            self.client.get_reports, [99999],
            400,
            self.reports.errors.field_project_id_is_not_valid
        )

    def test_get_reports_unknown_user(self):
        valid_username = self.client.client.username
        try:
            self.client.client.username = "Anonymous"
            self.reports_page.expect_to_raise_exception(
                self.client.get_reports, [1],
                401,
                self.reports.errors.authentication_failed,
                self.reports.errors.maximum_number_of_failed_login_attempts
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    def test_run_report_unknown_user(self):
        valid_username = self.client.client.username
        try:
            self.client.client.username = "Anonymous"
            self.reports_page.expect_to_raise_exception(
                self.client.run_report, [1],
                401,
                self.reports.errors.authentication_failed,
                self.reports.errors.maximum_number_of_failed_login_attempts
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    def test_run_report_with_id_0(self):
        self.reports_page.expect_to_raise_exception(
            self.client.run_report, [0],
            400,
            self.reports.errors.not_a_valid_report
        )

    def test_run_report_with_unknown_report_id(self):
        self.reports_page.expect_to_raise_exception(
            self.client.run_report, [99999],
            400,
            self.reports.errors.not_a_valid_report
        )

    def test_run_report_with_api_disabled(self):
        try:
            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.click_api_tab()
            self.site_settings.disable_api()
            self.reports_page.expect_to_raise_exception(
                self.client.run_report, [0],
                403,
                self.reports.errors.disabled_api
            )
        finally:
            self.site_settings.open_page(self.site_settings_url)
            self.site_settings.click_api_tab()
            self.site_settings.enable_api()

    def test_run_report_without_api_on_demand_enabled(self):
        self.reports_page.open_page(self.data.server_name + self.reports.reports.property_distribution.format(self.project_id))
        self.reports_page.click_add_report()
        self.reports_page.validate_success_message(self.reports.messages.reports_templates_success_add)
        reports = self.client.get_reports(self.project_id)
        self.reports_page.check_reports_length(reports, 0)

    def test_run_report_without_permission_to_create(self):
        user = decode_data(str(self.users.regular_user))
        user_overview_url = self.data.server_name + self.users.overview_url
        self.users_roles.open_page(user_overview_url)
        self.users_roles.add_user(user)

        role = decode_data(str(self.users.roles.no_permissions))

        self.users_roles.open_page(self.data.server_name + self.users.add_role_url)
        self.users_roles.add_role(role)

        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.select_user(self.users.regular_user.full_name)

        self.users_roles.open_access_tab()
        self.users_roles.change_role_for_user(role.name)

        self.reports_page.open_page(self.data.server_name + self.reports.reports.property_distribution.format(self.project_id))
        self.reports_page.check_schedule_on_demand_via_api()
        self.reports_page.click_add_report()

        reports = self.client.get_reports(self.project_id)
        report_id = reports[0]['id']

        self.client.client.username = user.email_address
        self.client.client.password = user.password

        self.reports_page.expect_to_raise_exception(
            self.client.run_report, [report_id],
            403,
            self.reports.errors.insufficient_permissions
        )


if __name__ == "__main__":
    pytest.main()
