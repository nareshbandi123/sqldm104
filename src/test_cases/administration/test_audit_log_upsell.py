import pytest

from src.pages.administration.users_roles_page import UsersRolesPage
from src.common import read_config, decode_data, get_environment_variables
from src.test_cases.base_test import BaseTest
from src.pages.administration.project_page import ProjectPage
from src.pages.administration.site_settings_page import SiteSettingsPage
from src.pages.login_page import LoginPage

HOSTED, ENTERPRISE, TRIAL = get_environment_variables()


class TestAuditLogUpsell(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Get test data
        cls.sso_settings = read_config('../config/sso_settings.json')
        cls.user = read_config('../config/users.json')
        cls.auditing = read_config('../config/auditing.json')

        # Prepare page objects
        cls.site_settings_url = cls.data.server_name + cls.sso_settings.site_settings_url
        cls.license_url = cls.data.server_name + cls.auditing.license_url
        cls.user_overview_url = cls.data.server_name + cls.user.overview_url
        cls.site_settings = SiteSettingsPage(cls.driver)
        cls.login = LoginPage(cls.driver)
        cls.project = ProjectPage(cls.driver)
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.setup_database(cls.auditing)

        cls.login_as_admin(cls)
        cls.prepare_regular_user(cls)

    def prepare_regular_user(self):
        self.users_roles.open_page(self.user_overview_url)

        user = decode_data(str(self.auditing.regular_user))
        self.users_roles.add_user(user)

    @classmethod
    def teardown_class(cls):
        cls.driver.delete_all_cookies()
        cls.driver.quit()

    def login_as_admin(self):
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def relogin_as_regular_user(self):
        self.login.click_logout()

        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)

        self.login.simple_login(
            self.auditing.regular_user.email_address,
            self.auditing.regular_user.password
        )

    @pytest.mark.testrail(id=5665)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_if_auditing_tab_is_hidden_with_standard_license(self):
        standard_license = self.auditing.licenses.standard

        self.site_settings.open_page(self.license_url)
        success_message = self.auditing.messages.successfully_updated_license_message
        self.site_settings.insert_license_key(standard_license, success_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.check_auditing_log_tab_is_not_displayed()

    @pytest.mark.testrail(id=5666)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_if_auditing_tab_is_accessible_with_enterprise_license(self):
        enterprise_license = self.auditing.licenses.enterprise

        self.site_settings.open_page(self.license_url)
        success_message = self.auditing.messages.successfully_updated_license_message
        self.site_settings.insert_license_key(enterprise_license, success_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_log_tab()

    @pytest.mark.testrail(id=7459)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_check_external_integration(self):
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()
        self.site_settings.check_audit_write_logs_displayed()
        self.site_settings.check_audit_write_logs_is_not_selected()

    @pytest.mark.testrail(id=7458)
    @pytest.mark.skipif(not HOSTED, reason="TestRail is not Hosted")
    def test_check_external_integration_hidden(self):
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.go_to_auditing_configuration_tab()
        self.site_settings.check_audit_write_logs_is_not_displayed()

    @pytest.mark.testrail(id=7462)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_accessing_log_page_without_license(self):
        self.remove_setting('license_key')

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.check_auditing_log_tab_is_not_displayed()

    @pytest.mark.testrail(id=7460)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_downgrading_to_standard_license(self):
        standard_license = self.auditing.licenses.standard

        self.site_settings.open_page(self.license_url)
        success_message = self.auditing.messages.successfully_updated_license_message
        self.site_settings.insert_license_key(standard_license, success_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.check_auditing_log_tab_is_not_displayed()

    @pytest.mark.testrail(id=5650)
    @pytest.mark.skipif(HOSTED, reason="TestRail is Hosted")
    def test_if_auditing_tab_is_hidden_with_regular_license(self):
        regular_license = self.auditing.licenses.regular

        self.site_settings.open_page(self.license_url)
        success_message = self.auditing.messages.successfully_updated_license_message
        self.site_settings.insert_license_key(regular_license, success_message)

        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.check_auditing_log_tab_is_not_displayed()

    @pytest.mark.testrail(id=5770)
    def test_open_auditing_without_administrator_rights(self):
        if not HOSTED:
            enterprise_license = self.auditing.licenses.enterprise

            self.site_settings.open_page(self.license_url)
            success_message = self.auditing.messages.successfully_updated_license_message
            self.site_settings.insert_license_key(enterprise_license, success_message)

        self.relogin_as_regular_user()
        self.site_settings.open_page(self.site_settings_url)
        self.site_settings.check_auditing_log_tab_is_not_displayed()


if __name__ == "__main__":
    pytest.main()
