import pytest
from src.common import read_config, merge_configs
import src.pages.login_page as login
from src.test_cases.base_test import BaseTest


class TestLogin(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.user = read_config('../config/users.json')

        cls.login_page = login.LoginPage(cls.driver)

    def setup_method(self):
        self.login_page.open_page(self.data.server_name)

    def teardown_method(self):
        self.driver.delete_all_cookies()

    @pytest.mark.testrail(id=5328)
    def test_login_success_admin(self):
        self.login_page.enter_credentials(self.data.login.username, self.data.login.password)
        self.login_page.login()
        self.login_page.check_page(self.data.dashboard_url)
        self.login_page.check_admin(self.data.login.full_name)

    def test_login_fail_missing_fields(self):
        self.login_page.enter_credentials("", "")
        self.login_page.login_should_fail(error_email=self.data.login.messages.err_missing_email, error_pwd=self.data.login.messages.err_missing_psw)

    @pytest.mark.testrail(id=5332)
    def test_login_fail_missing_password(self):
        self.login_page.enter_credentials(self.data.login.username, "")
        self.login_page.login_should_fail(error_pwd=self.data.login.messages.err_missing_psw)

    @pytest.mark.testrail(id=5331)
    def test_login_fail_missing_email(self):
        self.login_page.enter_credentials("", self.data.login.password)
        self.login_page.login_should_fail(error_email=self.data.login.messages.err_missing_email)

    @pytest.mark.testrail(id=5329)
    def test_login_fail_wrong_email(self):
        self.login_page.enter_credentials(self.data.login.false_username, self.data.login.password)
        self.login_page.login()
        self.login_page.login_failed_error_validate(self.data.login.messages.err_false_credentials)

    @pytest.mark.testrail(id=5330)
    def test_login_fail_wrong_password(self):
        self.login_page.enter_credentials(self.data.login.username, self.data.login.false_password)
        self.login_page.login()
        self.login_page.login_failed_error_validate(self.data.login.messages.err_false_credentials)

    @pytest.mark.testrail(id=88)
    def test_manual_logout(self):
        self.login_page.enter_credentials(self.data.login.username, self.data.login.password)
        self.login_page.login()
        self.login_page.check_page(self.data.dashboard_url)
        self.login_page.click_logout()
        self.login_page.check_page(self.data.login_url)

if __name__ == "__main__":
    pytest.main()
