from src.locators.general_locators import GeneralLocators
from src.locators.project.suite_locators import SuiteLocator
from src.locators.project.testcases_locators import TestCaseLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
import time


class SuitePage(BasePage, BasePageElement):

    def verify_page_with_no_suites(self, title):
        self.validate_element_text(SuiteLocator.empty_title, title)

    def add_data_to_suite(self, name, description) -> int:
        self.wait_until_not_busy()
        self.send_keys_to_element(SuiteLocator.suite_name, name)
        self.send_keys_to_element(SuiteLocator.suite_description, description)
        form = self.find_element_by_locator(SuiteLocator.form)
        self.click_nested_element(form, SuiteLocator.add)
        self.wait_until_not_busy()
        return self.retrieve_id_from_url(self.driver.current_url)

    def validate_empty_suite(self, name, description, message, empty_message):
        self.validate_element_text(SuiteLocator.suite_title, name)
        self.validate_element_text(SuiteLocator.suite_description, description)
        self.validate_element_text(SuiteLocator.empty_title, empty_message)
        self.validate_element_text(SuiteLocator.success_message, message)

    def edit_suite_details(self):
        self.click_element(SuiteLocator.button_edit)

    def edit_suite_list(self, id):
        element = self.find_element_by_locator_and_value(By.ID, SuiteLocator.suite_row + str(id))
        self.click_nested_element(element, SuiteLocator.suite_row_edit)

    def open_selected_suite(self, name) -> int:
        id = self.retrieve_id_from_link(name)
        self.click_element_with_locator_and_value(By.LINK_TEXT, str(id))
        return id

    def edit_suite(self, name, description):
        self.clear_element_data(SuiteLocator.suite_name)
        self.send_keys_to_element(SuiteLocator.suite_name, name)
        self.clear_element_data(SuiteLocator.suite_description)
        self.send_keys_to_element(SuiteLocator.suite_description, description)
        form = self.find_element_by_locator(SuiteLocator.form)
        self.click_nested_element(form, SuiteLocator.add)

    def delete_suite(self):
        self.click_element(SuiteLocator.delete_suite)
        self.confirm_popup_delete()

    def get_suite_id(self, name) -> int:
        return self.retrieve_id_from_link(name)

    def run_test_on_suite_list(self, id):
        row = self.find_element_by_locator((By.ID, SuiteLocator.suite_row + str(id)))
        self.click_nested_element(row, SuiteLocator.suite_row_run_test)

    def add_test_run_from_suite(self):
        buttons = self.find_element_by_locator(GeneralLocators.form)
        self.click_nested_element(buttons, GeneralLocators.add)

    def check_runs_number(self, id, num):
        row = self.find_element_by_locator((By.ID, SuiteLocator.suite_row + str(id)))
        element = self.find_nested_element(row, SuiteLocator.suite_row_summary_desc)
        if num > 0:
            assert str(str(num) + " active test run") in element.text
        else:
            assert "No active test runs." in element.text

    def close_first_run(self, name):
        id = self.get_suite_id(name)
        suite_row = self.find_element_by_locator_and_value(By.ID, SuiteLocator.suite_row + str(id))
        self.click_nested_element(suite_row, SuiteLocator.suite_row_test_runs)

        links = self.find_elements_by_locator((By.LINK_TEXT, name))
        assert len(links) > 0
        links[0].click()
        self.click_element(SuiteLocator.run_edit_link)
        self.click_element(SuiteLocator.run_close_link)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

    def add_case(self, name):
        suite_url = self.driver.current_url
        self.click_element(TestCaseLocators.add_first_testcase)
        self.send_keys_to_element(TestCaseLocators.case_title, name)
        self.click_element(TestCaseLocators.case_accept)
        self.open_page(suite_url)

    def open_suite(self, name):
        self.click_element((By.LINK_TEXT, name))

    def open_columns_dialog(self):
        self.wait_for_blockui_to_close()
        self.hover_over_element_and_click(SuiteLocator.columns_dialog)
        self.wait_until_not_busy()

    def update_columns(self):
        self.wait_for_blockui_to_close()
        self.click_element(SuiteLocator.update_columns)
        # Allow time for column change to propagate, there is no
        # reliable event to wait for.
        time.sleep(2)

    def add_column(self, column_type):
        self.open_columns_dialog()
        self.wait_until_not_busy()
        self.click_element(SuiteLocator.add_column)
        self.wait_until_not_busy()
        self.select_option_text_on_element(SuiteLocator.column_items, column_type)
        self.click_element(SuiteLocator.add_column_submit)
        self.update_columns()

    def delete_column(self, column_type):
        self.open_columns_dialog()
        self.wait_until_not_busy()
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        attempts = 0
        while True:
            try:
                attempts += 1
                row_element = self.find_nested_element(dialog, SuiteLocator.column_row_by_name(column_type))
                cells = row_element.find_elements_by_tag_name('td')
                delete = cells[5]
                WebDriverWait(self.driver, 10).until(ec.visibility_of(delete))
                delete.click()
            except (StaleElementReferenceException, ElementNotInteractableException):
                if attempts == 3:
                    raise
                continue
            break
        self.update_columns()

    def edit_column(self, column_type):
        self.wait_until_not_busy()
        self.open_columns_dialog()
        self.wait_until_not_busy()
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        row_element = self.find_nested_element(dialog, SuiteLocator.column_row_by_name(column_type))
        cells = row_element.find_elements_by_tag_name('td')
        move_up = cells[3]
        move_up.click()
        width = cells[1].find_element_by_tag_name('input')
        width.clear()
        width.send_keys('200')
        self.update_columns()

    def assert_column_exists(self, column_name):
        self.find_element_by_locator(SuiteLocator.column_header(column_name))

    def assert_column_absent(self, column_name):
        self.wait_until_not_busy()
        headers = self.find_element_by_locator(SuiteLocator.columns_headers)
        assert column_name not in headers.text

    def assert_column_position_and_width(self, column_type, position, width):
        groups_block = self.find_element_by_locator(SuiteLocator.group_block)
        header_row = self.find_nested_element(groups_block, SuiteLocator.column_row_by_name(column_type))
        headers = header_row.find_elements_by_tag_name('th')
        # There are two empty headers before the named titles in the grid,
        # so with zero based indexing the index of our column is the position + 1
        column_header = headers[position]
        assert column_header.text == column_type
        assert column_header.size['width'] == width

    def go_to_test_run_tab(self):
        self.click_element(SuiteLocator.test_run_tab)

    def edit_test_run(self, test_run_name):
        self.click_element(SuiteLocator.run_edit_link)
        self.clear_element_data(SuiteLocator.suite_name)
        self.send_keys_to_element(SuiteLocator.suite_name, test_run_name)
        self.send_keys_to_element(SuiteLocator.suite_name, Keys.ENTER)

    def delete_test_run(self):
        self.click_element(SuiteLocator.run_edit_link)
        self.click_element(SuiteLocator.delete_suite)

