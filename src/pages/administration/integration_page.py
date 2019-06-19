from src.pages.base_page import BasePage
from src.pages.base_element import BasePageElement
from src.models.administration.plugin import Plugin, UserVariable
from src.locators.administration.integration_locators import IntegrationLocators
from src.locators.general_locators import GeneralLocators
from selenium.webdriver.common.by import By


class IntegrationPage(BasePage, BasePageElement):

    def add_defects_data(self, plugin_data: Plugin):
        self.send_keys_to_element(IntegrationLocators.defect_view_url, plugin_data.defect_view_url)
        self.send_keys_to_element(IntegrationLocators.defect_add_url, plugin_data.defect_add_url)
        self.select_option_on_element(IntegrationLocators.defect_plugin, plugin_data.plugin_name)
        self.wait_for_element_to_be_invisible(IntegrationLocators.defectBusy)
        self.clear_element_data(IntegrationLocators.defect_config)
        self.send_keys_to_element(IntegrationLocators.defect_config, plugin_data.defect_plugin)

    def add_user_variable(self, user_variable: UserVariable):
        self.wait_for_element_to_be_invisible(GeneralLocators.blockUI)
        self.click_element(IntegrationLocators.add_user_variable)
        form = self.find_element_by_locator(GeneralLocators.dialog)
        self.send_keys_to_nested_element(form, IntegrationLocators.userFieldLabel, user_variable.user_label)
        self.send_keys_to_nested_element(form, IntegrationLocators.userFieldDesc, user_variable.user_description)
        self.send_keys_to_nested_element(form, IntegrationLocators.userFieldName, user_variable.user_system_name)
        self.select_option_text_on_nested_element(form, IntegrationLocators.userFieldType, user_variable.user_type)
        if (user_variable.user_type == "String"):
            self.click_element(IntegrationLocators.userFieldFallback)
            self.send_keys_to_nested_element(form, IntegrationLocators.userFieldFallback, user_variable.user_fallback)
        if (user_variable.user_type == "Password"):
            self.click_element(IntegrationLocators.userFieldPassword)
            self.send_keys_to_nested_element(form, IntegrationLocators.userFieldPassword, user_variable.user_fallback)
        self.click_nested_element(form, IntegrationLocators.userFieldSubmit)
        self.validate_added_user_variable(user_variable)

    def validate_added_user_variable(self, user_variable:UserVariable):
        column = self.find_element_by_locator_and_value(By.ID, IntegrationLocators.userVariableColumn + user_variable.user_system_name)
        self.validate_nested_element_text(column, IntegrationLocators.userColumn_name, user_variable.user_system_name)
        self.validate_nested_element_text(column, IntegrationLocators.userColumn_type, user_variable.user_type)

    def save_settings(self):
        self.wait_for_element_to_be_invisible(GeneralLocators.blockUI)
        self.click_element(IntegrationLocators.accept)

    def check_success_message(self, message):
        self.validate_element_text(GeneralLocators.message_success, message)

    def clear_integration_settings(self):
        self.clear_element_data(IntegrationLocators.defect_view_url)
        self.clear_element_data(IntegrationLocators.defect_add_url)
        self.select_option_on_element(IntegrationLocators.defect_plugin, "")
        self.clear_all_user_varibles()
        self.click_element(IntegrationLocators.accept)

    def clear_all_user_varibles(self):
        user_variables = self.find_elements_by_locator(IntegrationLocators.user_variables)
        for variable in user_variables:
            self.click_nested_element(variable, IntegrationLocators.userColumn_delete)
            dialog = self.find_element_by_locator(GeneralLocators.dialog)
            self.click_nested_element(dialog, GeneralLocators.ok)

    def configure_jira_integration(self, address, user, pwd):
        self.click_element(IntegrationLocators.configure_jira_integration_btn)
        dialog = self.find_element_by_locator(IntegrationLocators.jira_integration_dialog)
        self.send_keys_to_nested_element(dialog, IntegrationLocators.jira_integration_address, address)
        self.send_keys_to_nested_element(dialog, IntegrationLocators.jira_integration_user, user)
        self.send_keys_to_nested_element(dialog, IntegrationLocators.jira_integration_password, pwd)
        self.click_nested_element(dialog, IntegrationLocators.jira_integration_submit)