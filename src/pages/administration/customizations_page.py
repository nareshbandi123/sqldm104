import pytest
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from src.pages.base_page import BasePage
from src.pages.base_element import BasePageElement
from src.locators.administration.customizations_locators import CustomizationsLocators
from src.locators.general_locators import GeneralLocators


class CustomizationsPage(BasePage, BasePageElement):

    def new_case_type_name(self, name):
        self.send_keys_to_element(GeneralLocators.name, name)
        self.click_element(GeneralLocators.submit_button)

    def validate_add_case_type_success(self, message):
        self.validate_element_text(GeneralLocators.message_success, message)

    def validate_add_case_type_missing_name(self, message):
        self.validate_element_text(GeneralLocators.message_error, message)

    def check_add_case_type_name(self, name):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        link.click()
        self.validate_element_text(GeneralLocators.name, name)

    def edit_case_type(self, name, new_name):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        link.click()
        self.clear_element_data(GeneralLocators.name)
        self.send_keys_to_element(GeneralLocators.name, new_name)
        self.click_element(GeneralLocators.submit_button)

    def delete_case_type(self, name):
        try:
            case = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
            case_row = self.get_grandparent_element(case)
            case_row.find_element_by_xpath("td[3]/a").click()
            self.confirm_popup_delete()
        except TimeoutException:
            pytest.fail("Element not found")
        except NoSuchElementException:
            pytest.fail("Element not found")

    def check_case_type_cannot_be_deleted(self, name):
        case = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        case_row = self.get_grandparent_element(case)
        delete_cell = case_row.find_element_by_xpath("td[3]")
        # Assert there is no delete link in this row
        assert len(delete_cell.find_elements_by_tag_name('a')) == 0

    def validate_case_type_deleted(self, message):
        self.validate_element_text(GeneralLocators.message_success, message)

    def validate_custom_field_required_fields(self, message):
        self.click_element(CustomizationsLocators.add_custom_field)
        self.validate_element_text(GeneralLocators.message_error, message)

    def custom_field_add_text_fields(self, label, system_name, description):
        self.send_keys_to_element(GeneralLocators.label, label)
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, description)
        self.send_keys_to_element(GeneralLocators.name, system_name)

    def select_custom_field_type(self, field_type, added_message):
        self.select_option_on_element(CustomizationsLocators.add_custom_field_type, field_type)
        self.click_element(CustomizationsLocators.add_custom_field)
        self.validate_element_text(GeneralLocators.message_success, added_message)

    def check_custom_field(self, label, system_name, description, field_type):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(label))
        link.click()
        self.validate_element_text(GeneralLocators.label, label)
        self.validate_element_text(CustomizationsLocators.add_custom_field_description, description)
        self.validate_element_text(GeneralLocators.name, system_name)

        type_box = self.find_element_by_locator(CustomizationsLocators.add_custom_field_type)
        select = Select(type_box)
        selected_field_type = select.first_selected_option.text
        assert selected_field_type == field_type

    def delete_custom_field(self, label, deleted_message):
        field = self.find_element_by_locator(CustomizationsLocators.element_by_name(label))
        field_row = self.get_grandparent_element(field)
        field_row.find_element_by_xpath("td[8]/a").click()
        self.confirm_popup_delete()
        self.validate_element_text(GeneralLocators.message_success, deleted_message)

    def edit_custom_field(self, label, new_label, new_description, edited_msg):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(label))
        link.click()
        self.clear_element_data(GeneralLocators.label)

        description_box = self.find_element_by_locator(GeneralLocators.label)
        self.send_keys_to_element(GeneralLocators.label, new_label)
        # CTRL-A plus BACKSPACE are needed for selenium to clear the textarea as .clear() doesn't work.
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, Keys.CONTROL + "a")
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, Keys.BACKSPACE)
        # Added same field clearing for MacOS, as COMMAND key is needed
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, Keys.COMMAND + "a")
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, Keys.BACKSPACE)
        self.send_keys_to_element(CustomizationsLocators.add_custom_field_description, new_description)

        select_templates = self.find_element_by_locator(CustomizationsLocators.add_custom_field_include_specific_templates)
        select_templates.click()

        exploratory_session = self.find_element_by_locator(CustomizationsLocators.add_custom_field_exploratory_session)
        exploratory_session.click()

        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, edited_msg)

    def check_template_fields(self):
        select_templates = self.find_element_by_locator(CustomizationsLocators.add_custom_field_include_specific_templates)
        exploratory_session = self.find_element_by_locator(CustomizationsLocators.add_custom_field_exploratory_session)
        testcase_text = self.find_element_by_locator(CustomizationsLocators.add_custom_field_testcase_text)
        testcase_steps = self.find_element_by_locator(CustomizationsLocators.add_custom_field_testcase_steps)

        assert select_templates.is_selected()
        assert exploratory_session.is_selected()
        assert not testcase_text.is_selected()
        assert not testcase_steps.is_selected()

    def validate_priority_required_field(self, message):
        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_error, message)

    def add_priority(self, name, abbreviation, added_message):
        self.send_keys_to_element(GeneralLocators.name, name)
        self.send_keys_to_element(CustomizationsLocators.add_priority_abbreviation, abbreviation)
        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, added_message)

    def check_priority(self, name, abbreviation):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        link.click()

        self.validate_element_text(GeneralLocators.name, name)
        self.validate_element_text(CustomizationsLocators.add_priority_abbreviation, abbreviation)

    def delete_priority(self, name, deleted_message):
        field = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        field_row = self.get_grandparent_element(field)
        field_row.find_element_by_xpath("td[6]/a").click()
        self.confirm_popup_delete()
        self.validate_element_text(GeneralLocators.message_success, deleted_message)

    def edit_priority(self, name, edit_name, edit_abbreviation, edited_message):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        link.click()

        self.clear_element_data(GeneralLocators.name)
        self.clear_element_data(CustomizationsLocators.add_priority_abbreviation)
        self.send_keys_to_element(GeneralLocators.name, edit_name)
        self.send_keys_to_element(CustomizationsLocators.add_priority_abbreviation, edit_abbreviation)

        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, edited_message)

    def add_ui_script(self, script, added_message):
        self.clear_element_data(CustomizationsLocators.add_ui_script_script)
        self.send_keys_to_element(CustomizationsLocators.add_ui_script_script, script)
        self.click_element(CustomizationsLocators.add_ui_script)
        self.validate_element_text(GeneralLocators.message_success, added_message)

    def check_ui_script(self, name, script, active):
        link = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        link.click()

        script_box = self.find_element_by_locator(CustomizationsLocators.add_ui_script_script)
        # We have to normalise whitespace because the browser adds and removes whitespace
        script_from_browser = '\n'.join([line.rstrip() for line in script_box.get_attribute('value').strip().split('\n')])
        assert script_from_browser == script.strip()

        active_button = self.find_element_by_locator(CustomizationsLocators.add_ui_script_active)
        assert active_button.is_selected() == active

    def delete_ui_script(self, name, deleted_message):
        # Cannot use confirm_popup_delete as there is no confirm element for ui scripts
        field = self.find_element_by_locator(CustomizationsLocators.element_by_name(name))
        field_row = self.get_grandparent_element(field)
        field_row.find_element_by_xpath("td[4]/a").click()

        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)
        self.validate_element_text(GeneralLocators.message_success, deleted_message)

    def edit_ui_script(self, name, edit_script, edited_message):
        link = self.find_element_by_locator_and_value(By.XPATH, "//span[contains(text(), '" + name + "')]")
        link.click()

        self.clear_element_data(CustomizationsLocators.add_ui_script_script)
        self.send_keys_to_element(CustomizationsLocators.add_ui_script_script, edit_script)
        self.click_element(CustomizationsLocators.add_ui_script_active)
        self.click_element(CustomizationsLocators.add_ui_script_edit_save)
        self.validate_element_text(GeneralLocators.message_success, edited_message)

    def check_edit_status_fields(self):
        name_box = self.find_element_by_locator(GeneralLocators.name)
        assert not name_box.is_enabled()

        is_final = self.find_element_by_locator(CustomizationsLocators.edit_status_is_final)
        assert not is_final.is_enabled()

        is_active = self.find_element_by_locator(CustomizationsLocators.edit_status_is_active)
        assert not is_active.is_enabled()

        color_dark = self.find_element_by_locator(CustomizationsLocators.edit_status_color_dark)
        assert color_dark.is_enabled()

        color_medium = self.find_element_by_locator(CustomizationsLocators.edit_status_color_medium)
        assert color_medium.is_enabled()

        color_bright = self.find_element_by_locator(CustomizationsLocators.edit_status_color_bright)
        assert color_bright.is_enabled()

    def edit_status(self, status, edited_message):
        self.clear_element_data(GeneralLocators.name)
        self.clear_element_data(GeneralLocators.label)
        self.clear_element_data(CustomizationsLocators.edit_status_color_dark)
        self.clear_element_data(CustomizationsLocators.edit_status_color_medium)
        self.clear_element_data(CustomizationsLocators.edit_status_color_bright)

        self.send_keys_to_element(GeneralLocators.name, status.name)
        self.send_keys_to_element(GeneralLocators.label, status.label)
        self.send_keys_to_element(CustomizationsLocators.edit_status_color_dark, status.color_dark)
        self.send_keys_to_element(CustomizationsLocators.edit_status_color_medium, status.color_medium)
        self.send_keys_to_element(CustomizationsLocators.edit_status_color_bright, status.color_bright)

        is_final = self.find_element_by_locator(CustomizationsLocators.edit_status_is_final)
        is_active = self.find_element_by_locator(CustomizationsLocators.edit_status_is_active)
        if is_final.is_selected() != status.is_final:
            self.click_element(CustomizationsLocators.edit_status_is_final)
        if is_active.is_selected() != status.is_active:
            self.click_element(CustomizationsLocators.edit_status_is_active)

        self.click_element(GeneralLocators.submit_button)

    def status_quick_edit(self, status_name, success_msg):
        status_link = self.find_element_by_locator_and_value(By.XPATH, "//span[contains(text(), '" + status_name + "')]")
        status_link.click()
        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, success_msg)

    def check_status(self, status):
        self.validate_element_text(GeneralLocators.name, status.name)
        self.validate_element_text(GeneralLocators.label, status.label)
        self.validate_element_text(CustomizationsLocators.edit_status_color_dark, status.color_dark)
        self.validate_element_text(CustomizationsLocators.edit_status_color_medium, status.color_medium)
        self.validate_element_text(CustomizationsLocators.edit_status_color_bright, status.color_bright)

        is_final = self.find_element_by_locator(CustomizationsLocators.edit_status_is_final)
        is_active = self.find_element_by_locator(CustomizationsLocators.edit_status_is_active)
        assert is_final.is_selected() == status.is_final
        assert is_active.is_selected() == status.is_active

    def create_new_template(self, template_name, success_msg):
        self.clear_element_data(CustomizationsLocators.add_template_field)
        self.send_keys_to_element(CustomizationsLocators.add_template_field, template_name)
        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, success_msg)

    def edit_template_field(self, old_name, new_name, success_msg):
        link = self.find_element_by_locator_and_value(By.XPATH, "//span[contains(text(), '" + old_name + "')]")
        link.click()
        self.clear_element_data(CustomizationsLocators.add_template_field)
        self.send_keys_to_element(CustomizationsLocators.add_template_field, new_name)
        self.click_element(GeneralLocators.submit_button)
        self.validate_element_text(GeneralLocators.message_success, success_msg)

    def delete_template(self, name, success_msg):
        field = self.find_element_by_locator_and_value(By.XPATH, "//span[contains(text(), '" + name + "')]")
        field_row = self.get_grandparent_element(field)
        field_row.find_element_by_xpath("td[3]/a").click()

        self.confirm_popup_delete()
        self.validate_element_text(GeneralLocators.message_success, success_msg)
