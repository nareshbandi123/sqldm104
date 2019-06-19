import pytest

import src.pages.administration.project_page as project_page
from src.common import read_config, get_environment_variables
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.administration import backups_page
from src.helpers.prepare_data import PrepareData
from src.test_cases.base_test import BaseTest

HOSTED, ENTERPRISE, TRIAL = get_environment_variables()


@pytest.mark.skipif(not HOSTED, reason="TestRail is not Hosted")
class TestBackups(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Get test data
        cls.p = read_config('../config/project.json')
        cls.site_settings = read_config('../config/site_settings.json')
        cls.users = read_config('../config/users.json')

        # Prepare page objects
        cls.project = project_page.ProjectPage(cls.driver)
        cls.backups = backups_page.BackupsPage(cls.driver)
        cls.prepare_data = PrepareData(cls.driver)

        cls.backups_url = cls.data.server_name + cls.site_settings.site_settings_url + cls.site_settings.tabs.backups
        cls.user_overview_url = cls.data.server_name + cls.users.overview_url

        cls.prepare_data.login_as_admin()
        cls.prepare_data.add_tester_user()

    @classmethod
    def teardown_class(cls):
        cls.prepare_data.login_as_admin()
        cls.reset_to_default_data(cls)
        super().teardown_class()

    def setup_method(self):
        self.backups.open_page(self.backups_url)

    def reset_to_default_data(self):
        self.backups.open_page(self.data.server_name + self.data.dashboard_url)
        self.backups.cancel_restoration()
        self.backups.open_page(self.backups_url)
        self.backups.set_backup_time('1')

    @pytest.mark.testrail(id=7463)
    def test_restore_button_displayed_and_enabled_by_default(self):
        self.backups.check_restore_button_enabled(True)

    @pytest.mark.testrail(id=5713)
    def test_backup_time_field_has_proper_date_and_disabled(self):
        if self.backups.check_last_backup_exists(self.site_settings.messages.no_backups_message):
            self.backups.check_last_backup_time_field_has_proper_date(self.site_settings.messages.no_backups_message)
            self.backups.check_last_backup_time_is_disabled()

    @pytest.mark.testrail(id=7464)
    def test_no_backup_time_recorded_yet(self):
        if not self.backups.check_last_backup_exists(self.site_settings.messages.no_backups_message):
            self.backups.check_last_backup_time_field_has_message(self.site_settings.messages.no_backups_message)
            self.backups.check_last_backup_time_is_disabled()

    @pytest.mark.testrail(id=7465)
    def test_initiate_backup_with_confirmation_page_and_just_cancel(self):
        self.backups.restore_backup_with_confirmation_and_cancel()

        self.backups.open_page(self.backups_url)
        self.backups.check_restore_button_enabled(True)

    @pytest.mark.testrail(id=7467)
    def test_initiate_backup_with_confirmation_page_ok_button(self):
        self.backups.restore_backup_with_confirmation_ok_button_check()

        self.backups.open_page(self.backups_url)
        self.backups.check_restore_button_enabled(True)

    @pytest.mark.testrail(id=7466)
    def test_initiate_backup_with_confirmation_page_and_cancel(self):
        self.backups.restore_backup_with_confirmation(self.site_settings.messages.confirm_message, cancel=True)

        self.backups.open_page(self.backups_url)
        self.backups.check_restore_button_enabled(True)

    @pytest.mark.testrail(id=5680)
    @pytest.mark.dependency(name="test_initiate_backup_with_confirmation_page")
    def test_initiate_backup_with_confirmation_page(self):
        self.backups.restore_backup_with_confirmation(self.site_settings.messages.confirm_message)
        self.backups.open_page(self.backups_url)
        self.backups.check_restore_button_enabled(False)
        self.backups.check_banner_message(self.site_settings.messages.banner_message)

    @pytest.mark.testrail(id=7468)
    @pytest.mark.dependency(depends=['test_initiate_backup_with_confirmation_page'])
    def test_banner_message_displayed(self):
        self.backups.open_page(self.data.server_name + self.data.dashboard_url)
        self.backups.check_banner_message(self.site_settings.messages.banner_message)

    @pytest.mark.testrail(id=5681)
    @pytest.mark.dependency(depends=['test_initiate_backup_with_confirmation_page'])
    def test_non_administrator_cant_login_while_frozen(self):
        self.prepare_data.login_as_tester(check_dashboard=False)
        self.login.login_failed_error_validate(self.site_settings.messages.frozen_message)

    @pytest.mark.testrail(ids=[5682,5683])
    @pytest.mark.dependency(depends=['test_initiate_backup_with_confirmation_page'])
    def test_administrator_can_login_and_cancel_restoration(self):
        self.prepare_data.login_as_admin()
        self.backups.open_page(self.data.server_name + self.data.dashboard_url)
        self.backups.cancel_restoration()
        # check banner disappear
        self.backups.open_page(self.data.server_name + self.data.dashboard_url)
        self.backups.check_banner_message_not_displayed()
        self.backups.open_page(self.backups_url)
        self.backups.check_restore_button_enabled(True)

    @pytest.mark.testrail(id=5677)
    def test_change_backup_time(self):
        self.backups.set_backup_time('18')
        self.backups.open_page(self.backups_url)
        self.backups.check_backup_time('18')

    @pytest.mark.testrail(id=7469)
    def test_access_to_backup_page_as_regular_user(self):
        self.backups.cancel_restoration()
        self.prepare_data.login_as_tester(check_dashboard=False)
        self.backups.open_page(self.backups_url)
        # check that backup page is not accessible
        self.login.check_login_page_displayed()


if __name__ == "__main__":
    pytest.main()
