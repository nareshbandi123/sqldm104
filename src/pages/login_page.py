from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import alert_is_present

from src.locators.login_locators import LoginLocators
from src.locators.dashboard_locators import DashboardLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage


class LoginPage(BasePage, BasePageElement):

    def enter_credentials(self, email_add, psw):
        self.wait_for_page_load(10)
        set_email = "document.getElementById('name').value = '{}';".format(email_add)
        set_password = "document.getElementById('password').value = '{}'".format(psw)
        self.wait_for_element_to_be_visible(LoginLocators.email_address)
        self.driver.execute_script(set_email)
        self.driver.execute_script(set_password)

    def login(self):
        self.wait_for_element_to_be_clickable(LoginLocators.login)
        self.click_element(LoginLocators.login)

    def check_admin(self, username):
        admin = self.find_element_by_locator(DashboardLocators.username)
        assert (admin.text == username)
        self.check_administration_access()

    def check_administration_access(self):
        administration = self.find_element_by_locator(DashboardLocators.administration)
        assert (administration is not None)

    def click_logout(self):
        self.wait_for_element_to_be_visible(DashboardLocators.username)
        try:
            self.click_element(DashboardLocators.username)
            self.wait_for_element_to_be_visible(DashboardLocators.logout)
            self.click_element(DashboardLocators.logout)
        except:
            self.driver.refresh()
            self.wait_for_element_to_be_visible(DashboardLocators.username)
            self.click_element(DashboardLocators.username)
            self.wait_for_element_to_be_visible(DashboardLocators.logout)
            self.click_element(DashboardLocators.logout)

    def request_psw_reset(self, email):
        self.find_element_by_locator(LoginLocators.fp_email_address).send_keys(email)
        self.click_element(LoginLocators.request_password_reset)

    def validate_reset(self, message):
        message_success = self.find_element_by_locator(LoginLocators.fp_message)
        assert message_success.text == message

    def check_fp_validation(self, message):
        self.check_element_is_visible(LoginLocators.fp_error_message)
        self.validate_element_text(LoginLocators.fp_error_message, message)

    def check_fp_validation_non_existing_email(self, message):
        self.check_element_is_visible(LoginLocators.fp_message)
        self.validate_element_text(LoginLocators.fp_message, message)

    def request_psw_cancel(self):
        self.click_element(LoginLocators.cancel)

    def login_should_fail(self, error_email='', error_pwd=''):
        self.login()
        elements = self.driver.find_elements_by_class_name(LoginLocators.error_email[1])
        if error_email == '':
            assert elements[0].text == error_pwd
        elif error_pwd == '':
            assert elements[0].text == error_email
        else:
            assert elements[0].text == error_email
            assert elements[1].text == error_pwd
        self.find_element_by_locator(LoginLocators.email_address).clear()
        self.find_element_by_locator(LoginLocators.password).clear()

    def login_failed_error_validate(self, error):
        self.wait_for_element_to_be_visible(LoginLocators.login_error_text)
        self.validate_element_text(LoginLocators.login_error_text, error)

    def simple_login(self, email, psw, check_dashboard=True):
        counter = 0
        while True:
            counter += 1
            # retry loop to workaround browser problems
            try:
                self.enter_credentials(email, psw)
                self.login()
                if check_dashboard:
                    self.check_if_dashboard_is_displayed()
                return
            except:
                if counter == 3:
                    raise

    def simple_login_without_check(self, email, psw):
        self.enter_credentials(email, psw)
        self.login()

    def check_if_dashboard_is_displayed(self):
        self.wait_for_redirect(10)
        self.wait_for_element_to_be_visible(DashboardLocators.dashboard_tab)
        self.check_element_is_visible(DashboardLocators.dashboard_tab)

    def check_sso_button_is_visible(self):
        self.check_element_is_visible(LoginLocators.sso_login)

    def check_sso_button_is_not_visible(self):
        self.driver.implicitly_wait(1)
        assert self.check_element_not_exists(LoginLocators.sso_login)

    def click_sso_button(self):
        self.click_element(LoginLocators.sso_login)

    def sso_sign_in(self, username, password):
        self.driver.delete_all_cookies()
        self.driver.refresh()
        self.wait_for_element_to_be_visible(LoginLocators.sso_username)
        self.send_keys_to_element(LoginLocators.sso_username, username)
        self.send_keys_to_element(LoginLocators.sso_password, password)
        self.click_element(LoginLocators.sso_signin)
        self.handle_alert_if_displayed()

    def check_sso_login_failed(self, error):
        self.wait_for_element_to_be_visible(LoginLocators.okta_sign_in_failed)
        self.validate_element_text(LoginLocators.okta_sign_in_failed, error)

    def click_forgot_password(self):
        self.wait_for_element_to_be_visible(LoginLocators.forgot_password)
        self.click_element(LoginLocators.forgot_password)

    def check_forgot_password_not_allowed(self, email, error):
        self.wait_for_element_to_be_visible(LoginLocators.fp_email_address)
        self.send_keys_to_element(LoginLocators.fp_email_address, email)
        self.click_element(LoginLocators.request_password_reset)
        self.wait_for_element_to_be_visible(LoginLocators.fp_message)
        self.validate_element_text(LoginLocators.fp_message, error)

    def logout_IDP(self, idp_url):
        self.open_page(idp_url)
        self.driver.delete_all_cookies()

    def check_login_page_displayed(self):
        self.check_current_url('/auth/login')
