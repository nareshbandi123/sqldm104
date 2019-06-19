import pytest
import src.pages.login_page as login
from src.helpers.driver_manager import DriverManager as driver_manager
from src.test_cases.base_test import BaseTest

class TestForgotPassword(BaseTest):

    def setup_method(self):
        self.driver.get(self.data.server_name + self.data.forgot_password.url)
        self.driver.implicitly_wait(10)

    def teardown_method(self):
        self.driver.delete_all_cookies()

    @pytest.mark.testrail(id=5343)
    def test_forgot_password_success(self):
        login_page = login.LoginPage(self.driver)
        login_page.request_psw_reset(self.data.login.username)
        login_page.check_page(self.data.login_url)
        login_page.validate_reset(self.data.forgot_password.messages.email_sent_successfully)

    @pytest.mark.testrail(id=5339)
    def test_forgot_password_fail_missing_email(self):
        login_page = login.LoginPage(self.driver)
        login_page.request_psw_reset("")
        login_page.check_fp_validation(self.data.forgot_password.messages.err_missing_email)

    @pytest.mark.testrail(id=5340)
    def test_forgot_password_fail_invalid_email(self):
        login_page = login.LoginPage(self.driver)
        login_page.request_psw_reset(self.data.forgot_password.invalid_email)
        login_page.check_fp_validation(self.data.forgot_password.messages.err_email_not_valid)

    @pytest.mark.testrail(id=5341)
    def test_forgot_password_fail_not_existing_email(self):
        login_page = login.LoginPage(self.driver)
        login_page.request_psw_reset(self.data.login.false_username)
        login_page.check_fp_validation_non_existing_email(self.data.forgot_password.messages.err_email_not_existing)

if __name__ == "__main__":
    pytest.main()
