import pytest
from src.pages.administration.site_settings_page import SiteSettingsPage
from src.pages.administration.users_roles_page import UsersRolesPage
from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config
import os

ENTERPRISE = False
if read_config('../config/enterprise.json').version == 'enterprise trial':
    ENTERPRISE = True
elif read_config('../config/enterprise.json').version == 'enterprise':
    ENTERPRISE = True


@pytest.mark.skipif(not ENTERPRISE, reason="TestRail is not Enterprise")
class TestSSO(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.sso_settings = read_config('../config/sso_settings.json')
        cls.user = read_config('../config/users.json')

        #Set URLs
        cls.sso_settings_url = cls.data.server_name + cls.sso_settings.site_settings_url + cls.sso_settings.tabs.sso
        cls.user_overview_url = cls.data.server_name + cls.user.overview_url

        #Initialize Page Objects
        cls.site_settings = SiteSettingsPage(cls.driver)
        cls.users = UsersRolesPage(cls.driver)

        cls.setup_database(cls.sso_settings)

        platform = cls.data.database.dbtype
        if platform == "mssql":
            cls.valid_settings = cls.sso_settings.valid_settings_windows
        elif platform == "mysql":
            cls.valid_settings = cls.sso_settings.valid_settings_linux
        else:
            cls.valid_settings = cls.sso_settings.valid_settings_hosted

    @classmethod
    def teardown_class(cls):
        cls.login.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.login.open_page(cls.sso_settings_url)
        cls.site_settings.switch_off_sso()

        super().teardown_class()
        cls.teardown_database()

    def setup_method(self):
        self.login.open_page(self.data.idp_url)
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.site_settings.open_page(self.sso_settings_url)
        self.site_settings.switch_off_sso()
        self.site_settings.open_page(self.sso_settings_url)

    def teardown_method(self):
        self.login.open_page(self.data.server_name)
        self.driver.delete_all_cookies()

    def clean_up_user(self, username):
        self.login.open_page(self.data.server_name)
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.users.open_page(self.user_overview_url)
        self.users.forget_user(username)

    def test_sso_button_not_visible(self):
        self.login.click_logout()
        self.login.check_sso_button_is_not_visible()

    @pytest.mark.testrail(id=5248)
    def test_default_sso_setting(self):
        self.site_settings.check_sso_not_enabled()

    @pytest.mark.testrail(id=5369)
    def test_sso_checkbox_not_enabled(self):
        self.users.open_page(self.user_overview_url)
        self.users.select_user(self.data.login.full_name)
        self.users.check_sso_checkbox_state('disabled')

    def test_fields_hidden_on_sso_off(self):
        self.site_settings.switch_on_sso()
        self.site_settings.check_sso_fields_visible()
        self.site_settings.switch_off_sso()
        self.site_settings.check_sso_fields_hidden()

    def test_testrail_entity_settings(self):
        entity_id = self.data.server_name + self.sso_settings.valid_settings.entity_id
        entity_sso_url = self.data.server_name + self.sso_settings.valid_settings.entity_sso_url
        self.site_settings.switch_on_sso()
        self.site_settings.check_entity_settings(entity_id, entity_sso_url)

    @pytest.mark.testrail(id=5290)
    def test_check_sso_enabled(self):
        self.site_settings.click_sso_switch()
        self.site_settings.check_sso_config_visible()

    def test_check_entity_settings_exist_disabled(self):
        self.site_settings.click_sso_switch()
        self.site_settings.check_sso_entity_fields_disabled()

    @pytest.mark.testrail(id=5288)
    def test_cancel_settings(self):
        self.site_settings.click_sso_switch()
        settings = self.site_settings.read_settings()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='true',
                                         create_account='true')
        self.site_settings.click_cancel()
        self.site_settings.open_page(self.sso_settings_url)
        self.site_settings.click_sso_switch()
        self.site_settings.check_sso_settings(idp_sso_url=settings['idp_sso_url'], idp_issuer_url=settings['idp_issuer_url'],
                                              idp_certificate=settings['idp_certificate'], fallback=settings['fallback'],
                                              create_account=settings['create_account'])

    @pytest.mark.testrail(id=5421)
    def test_check_invalid_sso_url(self):
        self.site_settings.click_sso_switch()
        self.site_settings.clear_sso_data()
        self.site_settings.configure_sso(idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_idp_sso_url_required)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5287)
    def test_check_invalid_issuer_url(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.sso_settings.invalid_settings.invalid_idp_sso_url,
                                         certificate=self.valid_settings.idp_certificate)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_idp_issuer_url_required)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5299)
    def test_check_invalid_certificate(self):
        self.site_settings.click_sso_switch()
        self.site_settings.clear_sso_data()
        self.site_settings.configure_sso(idp_sso_url=self.sso_settings.invalid_settings.invalid_idp_sso_url,
                                         idp_issuer_url=self.sso_settings.invalid_settings.invalid_idp_issuer_url)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_certificate_required)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5300)
    def test_invalid_test_connection_sso_url(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate)
        self.site_settings.click_test_connection()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_idp_sso_url_required)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5280)
    def test_invalid_testconnection_issuer_url(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         certificate=self.valid_settings.idp_certificate)
        self.site_settings.click_test_connection()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_idp_issuer_url_required)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5301)
    def test_invalid_testconnection_certificate(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate="Sample Certificate")
        self.site_settings.click_test_connection()
        self.site_settings.check_sso_error_displayed(self.sso_settings.messages.error_certificate_invalid)
        self.site_settings.click_cancel()

    @pytest.mark.testrail(id=5279)
    def test_test_connection(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='true')
        self.site_settings.click_test_connection()
        user_test = decode_data(str(self.user.add[0]))
        self.site_settings.login_okta(user_test.email_address, user_test.password)
        self.site_settings.check_success_message(self.sso_settings.messages.success_test_connection)
        self.site_settings.click_cancel()
        self.login.logout_IDP(self.data.idp_url)
        self.login.open_page(self.data.server_name)

    @pytest.mark.testrail(ids=[5286, 5289])
    @pytest.mark.dependency(name="test_save_settings_success")
    def test_save_settings_success(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='true',
                                         create_account='true')
        self.site_settings.click_save_settings()
        self.site_settings.check_success_message(self.sso_settings.messages.success_updated_site_settings)

    @pytest.mark.testrail(id=5268)
    @pytest.mark.dependency(depends=['test_save_settings_success'])
    def test_pre_existing_settings_exist(self):
        self.site_settings.click_sso_switch()
        self.site_settings.check_sso_settings(idp_sso_url=self.valid_settings.idp_sso_url,
                                              idp_issuer_url=self.valid_settings.idp_issuer_url,
                                              idp_certificate=self.valid_settings.idp_certificate,
                                              fallback='true', create_account='true')

    @pytest.mark.testrail(id=5427)
    @pytest.mark.dependency(depends=['test_save_settings_success'])
    def test_certificate_paste(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate='', fallback='true', create_account='true')
        self.site_settings.paste_certificate(self.valid_settings.idp_certificate)
        self.site_settings.click_save_settings()
        self.site_settings.check_sso_settings(idp_sso_url=self.valid_settings.idp_sso_url,
                                              idp_issuer_url=self.valid_settings.idp_issuer_url,
                                              idp_certificate=self.valid_settings.idp_certificate,
                                              fallback='true', create_account='true')
        self.site_settings.click_cancel()

    def test_idp_certificate_upload_invalid(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate="")
        certificate_path = os.path.normpath(os.path.abspath(os.path.join('../data/', self.sso_settings.invalid_settings.certificate_file_path)))
        self.site_settings.upload_invalid_certificate(certificate_path,  self.sso_settings.messages.error_invalid_certificate_uploaded)

    @pytest.mark.testrail(id=5297)
    def test_idp_certificate_upload(self):
        self.site_settings.click_sso_switch()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate="")
        certificate_path = os.path.normpath(os.path.abspath(os.path.join('../data/', self.valid_settings.certificate_file_path)))
        self.site_settings.upload_certificate(certificate_path)
        self.site_settings.click_save_settings()
        self.site_settings.check_success_message(self.sso_settings.messages.success_updated_site_settings)

    @pytest.mark.dependency(depends=['test_save_settings_success'])
    def test_sso_button_visible_on_login_page(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate)
        self.site_settings.click_save_settings()
        self.login.click_logout()
        self.login.check_sso_button_is_visible()
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def test_login_sso_fail(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, 'invalid_password')
        self.login.check_sso_login_failed(self.data.login.messages.err_sso_sign_in_failed)
        self.site_settings.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    @pytest.mark.testrail(id=5309)
    def test_administrator_fallback_login(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.open_page(self.user_overview_url)
        self.users.enable_sso_user(self.data.login.full_name)
        self.login.click_logout()
        self.login.simple_login(self.data.login.username, self.data.login.password)

    @pytest.mark.testrail(id=5313)
    def test_fallback_login_not_allowed(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        user_to_edit = decode_data(str(self.user.add[0]))
        self.login.open_page(self.user_overview_url)
        self.users.add_user(user_to_edit)
        self.users.enable_sso_user(user_to_edit.full_name)
        self.login.click_logout()
        try:
            self.login.enter_credentials(user_to_edit.email_address, user_to_edit.password)
            self.login.login()
            self.login.login_failed_error_validate(self.data.login.messages.err_fallback_disabled)
        finally:
            self.clean_up_user(user_to_edit.full_name)

    @pytest.mark.testrail(id=5278)
    def test_fallback_login_allowed(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='true', create_account='false')
        self.site_settings.click_save_settings()
        user_to_edit = decode_data(str(self.user.add[0]))
        self.login.open_page(self.user_overview_url)
        self.users.add_user(user_to_edit)
        self.users.enable_sso_user(user_to_edit.full_name)
        self.login.click_logout()
        try:
            self.login.simple_login(user_to_edit.email_address, user_to_edit.password)
        finally:
            self.clean_up_user(user_to_edit.full_name)

    @pytest.mark.testrail(id=5277)
    def test_sso_login_disabled(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, self.data.login.sso_password)
        self.login.login_failed_error_validate(self.data.login.messages.err_sso_disabled)
        self.login.logout_IDP(self.data.idp_url)
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def test_create_account_fail(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        user_to_check = decode_data(str(self.user.add[3]))
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(user_to_check.email_address, user_to_check.password)
        self.login.login_failed_error_validate(self.data.login.messages.err_sso_disabled)
        self.login.logout_IDP(self.data.idp_url)
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    @pytest.mark.testrail(id=5276)
    @pytest.mark.dependency(name="test_create_account_success")
    def test_create_account_success(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='true')
        self.site_settings.click_save_settings()
        user_to_check = decode_data(str(self.user.add[3]))
        self.users.open_page(self.user_overview_url)
        if self.users.check_user_exists(user_to_check.full_name):
            self.users.forget_user(user_to_check.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(user_to_check.email_address, user_to_check.password)
        try:
            self.login.check_if_dashboard_is_displayed()
            self.users.open_page(self.data.server_name)
            self.login.click_logout()
            self.login.logout_IDP(self.data.idp_url)
        finally:
            self.clean_up_user(user_to_check.full_name)

    @pytest.mark.testrail(id=5372)
    @pytest.mark.dependency(name="test_login_sso_success")
    def test_login_sso_success(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.open_page(self.user_overview_url)
        self.users.enable_sso_user(self.data.login.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, self.data.login.sso_password)
        self.login.check_if_dashboard_is_displayed()
        self.login.click_logout()
        self.login.logout_IDP(self.data.idp_url)
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    @pytest.mark.testrail(id=5320)
    def test_login_from_idp(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.open_page(self.user_overview_url)
        self.users.enable_sso_user(self.data.login.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, self.data.login.sso_password)
        self.login.check_if_dashboard_is_displayed()
        self.login.click_logout()
        self.site_settings.open_page(self.data.idp_url)
        self.site_settings.open_app(self.valid_settings.app_name)
        try:
            self.login.check_if_dashboard_is_displayed()
        finally:
            self.login.close_tab()
            self.login.switch_to_window(0)

    def test_existing_sso_session(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.open_page(self.user_overview_url)
        self.users.enable_sso_user(self.data.login.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, self.data.login.sso_password)
        self.login.check_if_dashboard_is_displayed()
        self.site_settings.open_new_tab(self.data.server_name)
        try:
            self.login.check_if_dashboard_is_displayed()
        finally:
            self.login.close_tab()
            self.login.switch_to_window(0)

    def test_sso_logout(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.login.open_page(self.user_overview_url)
        self.users.enable_sso_user(self.data.login.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(self.data.login.username, self.data.login.sso_password)
        self.login.check_if_dashboard_is_displayed()
        self.login.click_logout()
        self.login.check_login_page_displayed()

    def test_local_user_logout(self):
        user = decode_data(str(self.user.add[0]))
        self.users.open_page(self.user_overview_url)
        self.users.add_user(user)
        try:
            self.login.click_logout()
            self.login.simple_login(user.email_address, user.password)
            self.login.check_if_dashboard_is_displayed()
            self.login.click_logout()
            self.login.check_login_page_displayed()
        finally:
            self.clean_up_user(user.full_name)

    @pytest.mark.dependency(name="test_default_login_type_local", depends=['test_login_sso_success'])
    def test_default_login_type_local(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.site_settings.open_page(self.user_overview_url)
        self.users.check_users_sso_local()
        self.users.select_user(self.data.login.full_name)
        self.users.check_sso_checkbox_state('enabled')
        self.users.check_sso_checkbox_value(False)

    @pytest.mark.testrail(id=5371)
    def test_enable_and_disable_sso_user(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        self.site_settings.open_page(self.user_overview_url)
        self.users.select_user(self.data.login.full_name)
        self.users.check_sso_checkbox_state('enabled')
        self.users.check_sso_checkbox_value(False)
        self.users.click_sso_checkbox()
        self.users.click_save_changes()
        self.users.select_user(self.data.login.full_name)
        self.users.check_sso_checkbox_value(True)
        self.users.click_sso_checkbox()
        self.users.click_save_changes()
        self.users.select_user(self.data.login.full_name)
        self.users.check_sso_checkbox_value(False)

    @pytest.mark.testrail(id=5375)
    @pytest.mark.dependency(depends=['test_default_login_type_local'])
    def test_change_local_user_to_sso(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='false')
        self.site_settings.click_save_settings()
        user_to_check = decode_data(str(self.user.add[0]))
        self.users.open_page(self.user_overview_url)
        self.users.add_user(user_to_check)
        self.users.enable_sso_user(user_to_check.full_name)
        self.users.check_user_login_type_is_sso(user_to_check.full_name)
        self.users.open_page(self.user_overview_url)
        self.users.forget_user(user_to_check.full_name)

    @pytest.mark.dependency(name="test_hidden_fields_for_sso_only_users", depends=['test_create_account_success'])
    def test_hidden_fields_for_sso_only_users(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='true')
        self.site_settings.click_save_settings()
        user_to_test = decode_data(str(self.user.add[3]))
        self.users.open_page(self.user_overview_url)
        if self.users.check_user_exists(user_to_test):
            self.users.forget_user(user_to_test.full_name)
        self.login.click_logout()
        self.login.click_sso_button()
        self.login.sso_sign_in(username=user_to_test.email_address, password=user_to_test.password)
        self.login.check_if_dashboard_is_displayed()
        try:
            self.login.open_page(self.data.server_name + self.data.my_settings_url)
            self.users.check_sso_checkbox_not_shown()
            self.users.check_email_field_disabled()
            self.users.check_password_field_not_displayed()
            self.login.click_logout()
            self.login.logout_IDP(self.data.idp_url)
        finally:
            self.clean_up_user(user_to_test.full_name)

    @pytest.mark.testrail(id=5367)
    @pytest.mark.dependency(depends=['test_hidden_fields_for_sso_only_users'])
    def test_reset_password_not_allowed(self):
        self.site_settings.switch_on_sso()
        self.site_settings.configure_sso(idp_sso_url=self.valid_settings.idp_sso_url,
                                         idp_issuer_url=self.valid_settings.idp_issuer_url,
                                         certificate=self.valid_settings.idp_certificate,
                                         fallback='false', create_account='true')
        self.site_settings.click_save_settings()
        user_to_test = decode_data(str(self.user.add[3]))
        self.users.open_page(self.user_overview_url)
        self.users.add_user(user_to_test)
        try:
            self.users.enable_sso_user(user_to_test.full_name)
            self.login.click_logout()
            self.login.click_forgot_password()
            self.login.check_forgot_password_not_allowed(user_to_test.email_address,
                                                         self.data.forgot_password.messages.err_forgot_pwd_disabled)
        finally:
            self.clean_up_user(user_to_test.full_name)


if __name__ == "__main__":
        pytest.main()
