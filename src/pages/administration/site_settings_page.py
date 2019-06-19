import time

import requests
from datetime import date, timedelta
from dateutil import parser
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from src.models.administration.audit_record import AuditRecord
from src.pages.base_page import BasePage
from src.pages.base_element import BasePageElement
from src.locators.administration.site_settings_locators import Sitesettings_locators
from src.locators.general_locators import GeneralLocators
from selenium.webdriver.common.by import By

NUM_OF_COLUMNS = 7
DATE_INDEX = 0
ENTITY_TYPE_INDEX = 1
ENTITY_ID_INDEX = 2
ENTITY_NAME_INDEX = 3
ACTION_INDEX = 4
AUTHOR_INDEX = 5
MODE_INDEX = 6


class SiteSettingsPage(BasePage, BasePageElement):

    def click_site_settings(self):
        self.click_element(Sitesettings_locators.site_settings_button)

    def click_login_tab(self):
        self.click_element(Sitesettings_locators.login_tab)

    def go_to_sso_tab(self):
        self.click_element(Sitesettings_locators.sso_tab)

    def click_sso_switch(self):
        self.click_element(Sitesettings_locators.sso_switch)

    def click_save_settings(self):
        self.click_element(Sitesettings_locators.save_settings)

    def click_cancel(self):
        self.click_element(GeneralLocators.cancel)

    def click_test_connection(self):
        self.click_element(Sitesettings_locators.test_connection)

    def switch_off_sso(self):
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.sso_switch_indicator), 'checked'):
            self.click_element(Sitesettings_locators.sso_switch)
            self.click_save_settings()

    # Some sample data is needed to save settings with SSO ON.
    def configure_sso(self, idp_sso_url='', idp_issuer_url='', certificate='', fallback='false',
                      create_account='false'):
        # if the field is not displayed the SSO is disabled
        self.clear_sso_data()
        self.send_keys_to_element(Sitesettings_locators.saml_idp_sso_url, idp_sso_url)
        self.send_keys_to_element(Sitesettings_locators.saml_idp_issuer_url, idp_issuer_url)
        self.send_keys_to_element(Sitesettings_locators.saml_ssl_certificate, certificate)
        if fallback == 'true':
            self.click_element(Sitesettings_locators.saml_authentication_fallback)
        if create_account == 'true':
            self.click_element(Sitesettings_locators.saml_create_account_first_login)

    def switch_on_sso(self):
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.sso_switch_indicator), 'checked') is None:
            self.click_element(Sitesettings_locators.sso_switch)

    def clear_sso_data(self):
        self.clear_element_data(Sitesettings_locators.saml_idp_issuer_url)
        self.clear_element_data(Sitesettings_locators.saml_idp_sso_url)
        self.clear_element_data(Sitesettings_locators.saml_ssl_certificate)
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.saml_authentication_fallback), 'checked'):
            self.click_element(Sitesettings_locators.saml_authentication_fallback)
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.saml_create_account_first_login), 'checked'):
            self.click_element(Sitesettings_locators.saml_create_account_first_login)

    def get_sso_checkbox_state(self):
        return self.get_attribute_value_from_element(self.find_element_by_locator(Sitesettings_locators.sso_switch),
                                                     'checked')

    def check_sso_not_enabled(self):
        assert self.check_element_is_visible(Sitesettings_locators.saml_idp_issuer_url) == False

    def check_sso_config_visible(self):
        self.check_element_is_visible(Sitesettings_locators.saml_idp_issuer_url)
        self.check_element_is_visible(Sitesettings_locators.saml_idp_sso_url)
        self.check_element_is_visible(Sitesettings_locators.saml_entity_id)
        self.check_element_is_visible(Sitesettings_locators.saml_sso_url)
        self.check_element_is_visible(Sitesettings_locators.saml_ssl_certificate)
        self.check_element_is_visible(Sitesettings_locators.saml_authentication_fallback)
        self.check_element_is_visible(Sitesettings_locators.saml_create_account_first_login)

    def check_sso_settings(self, fallback=None, create_account=None, idp_sso_url='', idp_issuer_url='',
                           idp_certificate='http://www.example.com'):
        assert self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_idp_sso_url), 'value') == idp_sso_url
        assert self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_idp_issuer_url), 'value') == idp_issuer_url
        self.check_certificate(str.rstrip(idp_certificate))
        assert self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_authentication_fallback), 'checked') == fallback
        assert self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_create_account_first_login),
            'checked') == create_account

    def check_sso_entity_fields_disabled(self):
        assert self.get_attribute_value_from_element(self.find_element_by_locator(Sitesettings_locators.saml_entity_id),
                                                     'readonly')
        assert self.get_attribute_value_from_element(self.find_element_by_locator(Sitesettings_locators.saml_sso_url),
                                                     'readonly')

    def check_certificate(self, certificate):
        assert str.rstrip(self.find_element_by_locator(Sitesettings_locators.saml_ssl_certificate).text) == certificate

    def check_sso_error_displayed(self, error):
        elements = self.find_elements_by_locator(GeneralLocators.message_error)
        for elem in elements:
            if elem.get_attribute('id') is None:
                assert elem.text == error

    def check_success_message(self, message):
        self.wait_for_redirect(10)
        text = self.find_element_by_locator(GeneralLocators.message_success).text
        assert text == message

    def login_okta(self, email, password):
        self.send_keys_to_element(Sitesettings_locators.okta_username, email)
        self.send_keys_to_element(Sitesettings_locators.okta_password, password)
        self.click_element(Sitesettings_locators.okta_login_button)
        self.handle_alert_if_displayed()
        self.wait_for_redirect(10)

    def upload_invalid_certificate(self, path, message):
        self.click_element(Sitesettings_locators.saml_ssl_certificate_upload)
        self.execute_javascript(
            'document.getElementsByClassName(\'dz-hidden-input\')[0].setAttribute(\'style\',"visibility:visible;")')
        self.send_keys_to_element(Sitesettings_locators.file_upload, path)
        dialog = self.find_element_by_locator(Sitesettings_locators.invalid_certificate_dialog)
        assert dialog.find_element(*GeneralLocators.dialog_message).text == message

    def upload_certificate(self, path):
        self.click_element(Sitesettings_locators.saml_ssl_certificate_upload)
        self.execute_javascript(
            'document.getElementsByClassName(\'dz-hidden-input\')[0].setAttribute(\'style\',"visibility:visible;")')
        self.send_keys_to_element(Sitesettings_locators.file_upload, path)
        self.wait_for_element_to_be_clickable(Sitesettings_locators.upload_button)
        self.click_element(Sitesettings_locators.upload_button)
        self.click_element(Sitesettings_locators.save_settings)

    def disable_fallback(self):
        self.click_element(Sitesettings_locators.saml_authentication_fallback)
        self.click_save_settings()

    def paste_certificate(self, idp_certificate):
        self.clear_element_data(Sitesettings_locators.saml_ssl_certificate)
        self.send_keys_to_element(Sitesettings_locators.saml_ssl_certificate, idp_certificate)

    def read_settings(self):
        values = {}
        values['idp_sso_url'] = self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_idp_sso_url), 'value')
        values['idp_issuer_url'] = self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_idp_issuer_url), 'value')
        values['idp_certificate'] = self.find_element_by_locator(Sitesettings_locators.saml_ssl_certificate).text
        values['fallback'] = self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_authentication_fallback), 'checked')
        values['create_account'] = self.get_attribute_value_from_element(
            self.find_element_by_locator(Sitesettings_locators.saml_create_account_first_login), 'checked')
        return values

    def open_app(self, app_name):
        self.wait_for_page_load(10)
        locator = (By.XPATH, Sitesettings_locators.get_app_locator(app_name))
        self.click_element(locator)
        self.wait_for_new_tab_to_open(5)
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.handle_alert_if_displayed()
        self.wait_for_redirect(10)

    def check_sso_fields_hidden(self):
        self.wait_for_element_to_be_invisible(Sitesettings_locators.saml_entity_id)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_entity_id)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_sso_url)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_idp_sso_url)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_idp_issuer_url)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_authentication_fallback)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_create_account_first_login)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_ssl_certificate)
        assert not self.check_element_is_visible(Sitesettings_locators.saml_ssl_certificate_upload)

    def check_sso_fields_visible(self):
        self.wait_for_element_to_be_visible(Sitesettings_locators.saml_entity_id)
        assert self.check_element_is_visible(Sitesettings_locators.saml_entity_id)
        assert self.check_element_is_visible(Sitesettings_locators.saml_sso_url)
        assert self.check_element_is_visible(Sitesettings_locators.saml_idp_sso_url)
        assert self.check_element_is_visible(Sitesettings_locators.saml_idp_issuer_url)
        assert self.check_element_is_visible(Sitesettings_locators.saml_authentication_fallback)
        assert self.check_element_is_visible(Sitesettings_locators.saml_create_account_first_login)
        assert self.check_element_is_visible(Sitesettings_locators.saml_ssl_certificate)
        assert self.check_element_is_visible(Sitesettings_locators.saml_ssl_certificate_upload)

    def check_entity_settings(self, entity_id, entity_sso_url):
        self.wait_for_element_to_be_visible(Sitesettings_locators.saml_entity_id)
        assert self.get_attribute_value_from_element(self.find_element_by_locator(Sitesettings_locators.saml_entity_id),
                                                     'value') == entity_id
        self.wait_for_element_to_be_visible(Sitesettings_locators.saml_sso_url)
        assert self.get_attribute_value_from_element(self.find_element_by_locator(Sitesettings_locators.saml_sso_url),
                                                     'value') == entity_sso_url

    def click_api_tab(self):
        self.click_element(Sitesettings_locators.api_tab)

    def enable_api(self):
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.api_enable_checkbox), 'checked') is None:
            self.click_element(Sitesettings_locators.api_enable_checkbox)
            self.click_save_settings()

    def disable_api(self):
        if self.get_attribute_value_from_element(
                self.find_element_by_locator(Sitesettings_locators.api_enable_checkbox), 'checked'):
            self.click_element(Sitesettings_locators.api_enable_checkbox)
            self.click_save_settings()

    def go_to_auditing_log_tab(self):
        self.click_element(Sitesettings_locators.auditing_tab)
        self.click_element(Sitesettings_locators.auditing_log_tab)

    def go_to_auditing_configuration_tab(self):
        self.click_element(Sitesettings_locators.auditing_tab)
        self.click_element(Sitesettings_locators.auditing_configuration_tab)

    def check_auditing_log_tab_is_not_displayed(self):
        assert self.check_element_not_exists(Sitesettings_locators.auditing_tab)

    def audit_level_on_the_page(self):
        assert self.check_element_is_visible(Sitesettings_locators.audit_level)

    def select_date_range(self, days=0):
        """
        Select custom date
        To field = current date
        From field = current date - days parameter
        """
        date_mode = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_date)
        self.wait_for_element_to_be_visible(Sitesettings_locators.audit_filter_logs_date)
        self.click_nested_element(date_mode, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(date_mode, Sitesettings_locators.audit_filter_select, "Custom")
        self.clear_nested_element(date_mode, Sitesettings_locators.audit_filter_date_custom_from)
        self.send_keys_to_nested_element(date_mode, Sitesettings_locators.audit_filter_date_custom_from,
                                         (date.today() - timedelta(days)).strftime("%m/%d/%Y"))
        author_mode = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_author)
        self.click_nested_element(author_mode, Sitesettings_locators.audit_filter_link)
        self.clear_nested_element(date_mode, Sitesettings_locators.audit_filter_date_custom_to)
        self.send_keys_to_nested_element(date_mode, Sitesettings_locators.audit_filter_date_custom_to,
                                         date.today().strftime("%m/%d/%Y"))
        self.click_nested_element(author_mode, Sitesettings_locators.audit_filter_link)

    def _get_audit_log_row_data(self, position):
        """Get row by position and retrieve it's data"""
        row_index = position + 1
        self.wait_for_page_load(10)
        audit_grid = self.find_element_by_locator(Sitesettings_locators.audit_grid)
        WebDriverWait(self.driver, 10).until(lambda d: len(audit_grid.find_elements_by_css_selector("tr")) > 0)
        audit_rows = self.find_nested_elements(audit_grid, Sitesettings_locators.audit_grid_row)
        row = audit_rows[row_index]
        row_columns = self.find_nested_elements(row, Sitesettings_locators.audit_row_column)
        assert len(row_columns) == NUM_OF_COLUMNS, "Number of columns in audit log table is less than 7"

        row_date_value = row_columns[DATE_INDEX].text
        row_entity_type = row_columns[ENTITY_TYPE_INDEX].text
        row_entity_id = row_columns[ENTITY_ID_INDEX].text
        row_entity_name = row_columns[ENTITY_NAME_INDEX].text
        row_action = row_columns[ACTION_INDEX].text
        row_author = row_columns[AUTHOR_INDEX].text
        row_mode = row_columns[MODE_INDEX].text

        return AuditRecord(date=row_date_value, entity_type=row_entity_type, entity_id=row_entity_id,
                           entity_name=row_entity_name, action=row_action, author=row_author, mode=row_mode)

    def log_row_exists(self, entity_type, action, entity_id=None, entity_name=None, mode='UI', position=0):
        audit_record = self._get_audit_log_row_data(position)
        self.validate_date(audit_record.date)
        assert audit_record.entity_type == entity_type, \
            "Entity type don't match. Expected: {} Actual: {}".format(entity_type, audit_record.entity_type)
        assert audit_record.action == action, \
            "Action don't match. Expected: {} Actual: {}".format(action, audit_record.action)
        assert audit_record.mode == mode, "Mode don't match. Expected: {} Actual: {}".format(mode, audit_record.mode)
        if entity_id:
            assert audit_record.entity_id == entity_id, \
                "Entity id don't match. Expected: {} Actual: {}".format(entity_id, audit_record.entity_id)
        if entity_name:
            assert audit_record.entity_name == entity_name, \
                "Entity name don't match. Expected: {} Actual: {}".format(entity_name, audit_record.entity_name)

    def no_log_row_exists(self, entity_type, action, entity_name=None, position=0):
        audit_record = self._get_audit_log_row_data(position)
        assert not (audit_record.entity_type == entity_type and audit_record.action == action
                    and audit_record.entity_name == entity_name)

    def validate_date(self, date_to_parse):
        parser.parse(date_to_parse)

    def set_audit_level(self, level):
        self.select_item_from_dropdown(Sitesettings_locators.audit_level, level)
        self.click_save_settings()

    def get_audit_level(self):
        select = Select(self.find_element_by_locator(Sitesettings_locators.audit_level))
        return select.first_selected_option.text

    def set_number_of_rows(self, number):
        self.select_item_from_dropdown(Sitesettings_locators.audit_rows_per_page, number)
        self.click_save_settings()

    def set_number_of_records(self, number):
        self.select_item_from_dropdown(Sitesettings_locators.audit_number_of_records, value=number)
        self.click_save_settings()

    def get_number_of_records(self):
        select = Select(self.find_element_by_locator(Sitesettings_locators.audit_number_of_records))
        return select.first_selected_option.text

    def get_audit_rows_per_page(self):
        inp = self.find_element_by_locator(Sitesettings_locators.audit_rows_per_page)
        return self.get_attribute_value_from_element(inp, 'value')

    def set_audit_rows_per_page(self, value):
        self.execute_javascript('javascript:document.getElementById("audit_rows_per_page").value={};'.format(value))
        self.click_save_settings()

    def set_number_of_records_to_custom(self):
        self.select_item_from_dropdown(Sitesettings_locators.audit_number_of_records, value="custom")

    def set_number_of_days_to_custom(self):
        self.select_item_from_dropdown(Sitesettings_locators.audit_number_of_days, value="custom")

    def set_custom_number_of_records_to(self, value):
        self.clear_element_data(Sitesettings_locators.audit_custom_number_of_records)
        self.send_keys_to_element(Sitesettings_locators.audit_custom_number_of_records, value=value)

    def set_custom_number_of_days_to(self, value):
        self.clear_element_data(Sitesettings_locators.audit_custom_number_of_days)
        self.send_keys_to_element(Sitesettings_locators.audit_custom_number_of_days, value=value)

    def check_custom_number_of_records(self, value):
        elem = self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_records)
        assert self.get_attribute_value_from_element(elem, 'value') == value

    def check_custom_number_of_days(self, value):
        elem = self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_days)
        assert self.get_attribute_value_from_element(elem, 'value') == value

    def set_number_of_days(self, number):
        self.select_item_from_dropdown(Sitesettings_locators.audit_number_of_days, value=number)
        self.click_save_settings()

    def get_number_of_days(self):
        select = Select(self.find_element_by_locator(Sitesettings_locators.audit_number_of_days))
        return select.first_selected_option.text

    def get_number_of_days(self):
        select = Select(self.find_element_by_locator(Sitesettings_locators.audit_number_of_days))
        return select.first_selected_option.text

    def open_filters(self):
        self.wait_for_element_to_be_visible(Sitesettings_locators.audit_filter_by_change)
        self.click_element(Sitesettings_locators.audit_filter_by_change)

    def submit_filters(self):
        self.click_element(Sitesettings_locators.audit_filter_apply)
        self.wait_for_element_to_be_invisible(GeneralLocators.busy)
        self.wait_for_element_to_be_invisible(GeneralLocators.busy)

    def select_entity_type_filter(self, entity_type):
        entity_type_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_entity_type)
        self.click_nested_element(entity_type_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(entity_type_block, Sitesettings_locators.audit_filter_select,
                                                  entity_type)

    def select_date_filter(self, date_from, date_to):
        date_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_date)
        self.click_nested_element(date_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(date_block, Sitesettings_locators.audit_filter_select, "Custom")
        self.send_keys_to_nested_element(date_block, Sitesettings_locators.audit_filter_date_custom_to, date_to)
        self.send_keys_to_nested_element(date_block, Sitesettings_locators.audit_filter_date_custom_from, date_from)

    def select_author_filter(self, author_name):
        author_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_author)
        self.click_nested_element(author_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(author_block, Sitesettings_locators.audit_filter_select, author_name)

    def select_action_filter(self, action):
        action_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_action)
        self.click_nested_element(action_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(action_block, Sitesettings_locators.audit_filter_select, action)

    def select_entity_name_filter(self, entity_name):
        entity_name_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_entity_name)
        self.click_nested_element(entity_name_block, Sitesettings_locators.audit_filter_link)
        self.send_keys_to_nested_element(entity_name_block, Sitesettings_locators.audit_filter_text_input_field,
                                         entity_name)

    def select_mode_filter(self, mode):
        mode_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_mode)
        self.click_nested_element(mode_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(mode_block, Sitesettings_locators.audit_filter_select, mode)

    def test_match_any_of_the_above_mode(self, and_or_switch=True):
        self.wait_for_element_to_be_visible(Sitesettings_locators.audit_filter_by_change)
        self.click_element(Sitesettings_locators.audit_filter_by_change)
        mode_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_mode)
        self.click_nested_element(mode_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(mode_block, Sitesettings_locators.audit_filter_select, "API")

        entity_type_block = self.find_element_by_locator(Sitesettings_locators.audit_filter_logs_entity_type)
        self.click_nested_element(entity_type_block, Sitesettings_locators.audit_filter_link)
        self.select_option_text_on_nested_element(entity_type_block, Sitesettings_locators.audit_filter_select,
                                                  "Template")

        if and_or_switch:
            self.click_element(Sitesettings_locators.audit_filter_filter_mode_or)
        else:
            self.click_element(Sitesettings_locators.audit_filter_filter_mode_and)

        self.click_element(Sitesettings_locators.audit_filter_apply)

    def calculate_rows_by_text_in_column(self, text, column):
        mapping = {
            'date': 1,
            'entity_type': 2,
            'entity_id': 3,
            'entity_name': 4,
            'action': 5,
            'author': 6,
            'mode': 7,
        }
        col = mapping[column]
        self.wait_for_results_loading()
        rows = self.find_elements_by_locator(
            (By.XPATH, "//table[@id='auditGrid']//tr//td[{}][contains(text(),'{}')]".format(
                col,
                text
            )))
        return len(rows)

    def calculate_total_rows(self):
        self.wait_for_results_loading()
        rows = self.find_elements_by_locator((By.XPATH, "//table[@id='auditGrid']//tr//td[2]"))
        return len(rows)

    def clear_log_filter(self):
        elements = self.find_elements_by_locator(Sitesettings_locators.audit_filter_reset)
        if len(elements) > 0:
            if elements[0].is_displayed():
                self.click_element(Sitesettings_locators.audit_filter_reset)

        self.wait_until_element_not_displayed(Sitesettings_locators.audit_filter_reset)
        self.wait_until_element_not_displayed(Sitesettings_locators.audit_filter_logs_busy)
        self.wait_for_results_loading()

    def wait_for_results_loading(self):
        self.wait_until_element_not_displayed(Sitesettings_locators.audit_filter_logs_bubble)
        self.wait_until_element_not_displayed(Sitesettings_locators.audit_filter_pagination_loader)

    def compare_values(self, param1, param2):
        assert param1 == param2

    def compare_rows_after_filtering(self, text, column):
        rows_with_text = self.calculate_rows_by_text_in_column(text, column)
        total_rows = self.calculate_total_rows()
        assert rows_with_text == total_rows

    def assert_rows_count(self, count):
        total_rows = self.calculate_total_rows()
        assert total_rows >= count

    def hover_audit_log_download_and_check_tooltip(self):
        self.driver.minimize_window()
        link_element = self.find_element_by_locator((By.ID, 'export-audit-link'))

        hover = ActionChains(self.driver).move_to_element(link_element)
        hover.perform()
        hover.pause(3.0)

        self.wait_for_element_to_be_visible(Sitesettings_locators.audit_download_tooltip)
        tooltip = self.find_element_by_locator(Sitesettings_locators.audit_download_tooltip)
        self.validate_nested_element_text(tooltip, (By.CLASS_NAME, 'tooltip-header'), 'Export Audit Log')

        link_element.click()

    def try_download_audit_log_and_validate(self):
        self.driver.minimize_window()
        link_element = self.find_element_by_locator((By.ID, 'export-audit-link'))
        link_element.click()

        download_link = self.find_element_by_locator((By.ID, 'export-audit-link-csv'))

        cookies = self.driver.get_cookies()
        href = self.get_attribute_value_from_element(download_link, 'href')
        s = requests.Session()
        [s.cookies.set(c['name'], c['value']) for c in cookies]
        resp = s.get(href)
        exported_log = resp.text
        assert exported_log.startswith(
            '﻿"Date","Entity Type","Entity Id","Entity Name","Action Type","Author ID","Mode"')
        # len of empty file
        assert len(exported_log) == 82

    def insert_license_key(self, license, message, error=False):
        license_key_div = self.find_element_by_locator(Sitesettings_locators.license_key_div)
        change_link = self.find_nested_element_by_locator_and_value(license_key_div, By.LINK_TEXT, 'Change')
        change_link.click()
        self.send_keys_to_element(Sitesettings_locators.license_key_textarea, license)
        self.click_element(GeneralLocators.ok)
        self.wait_for_element_to_be_visible(GeneralLocators.message_success)
        self.check_success_message(message)

    def check_audit_write_logs_displayed(self):
        self.check_element_is_visible(Sitesettings_locators.audit_write_logs)

    def check_audit_write_logs_is_not_displayed(self):
        self.check_element_not_exists(Sitesettings_locators.audit_write_logs)

    def check_audit_write_logs_is_not_selected(self):
        checkbox = self.find_element_by_locator(Sitesettings_locators.audit_write_logs)
        assert checkbox.is_selected() is False

    def assert_custom_number_of_records_not_as_entered(self, value):
        input = self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_records)
        assert input.get_attribute('value') != value

    def assert_custom_number_of_days_not_as_entered(self, value):
        input = self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_days)
        assert input.get_attribute('value') != value

    def check_custom_audit_log_retention_control_is_not_present(self):
        assert self.check_element_is_visible(Sitesettings_locators.audit_custom_number_of_days) is False

    def check_custom_audit_log_volume_control_is_not_present(self):
        assert self.check_element_is_visible(Sitesettings_locators.audit_custom_number_of_records) is False

    def check_custom_audit_log_retention_control_is_present(self):
        assert self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_days)

    def check_custom_audit_log_volume_control_is_present(self):
        assert self.find_element_by_locator(Sitesettings_locators.audit_custom_number_of_records)
