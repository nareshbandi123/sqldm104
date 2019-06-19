import os
import requests

from src.locators.project.testcases_locators import TestCaseLocators
from src.locators.project.section_locators import SectionLocators
from src.models.project.test_cases import TestCase, TestResult
from src.locators.general_locators import GeneralLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage
from src.pages.project.sections_page import SectionsPage as sections
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from src.common import decode_data
import time


class TestCasesPage(BasePage, BasePageElement):

    def get_section(self, section_name:str):
        return sections(self.driver).get_section(section_name)

    def press_add_first_testcase_button(self) -> int:
        self.click_element(TestCaseLocators.add_first_testcase)

    def press_add_test_inline(self, section_id: str):
        section = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionColumn + section_id)
        self.click_nested_element(section, TestCaseLocators.addCase_inline)

    def add_test_case_inline(self, section_id: str, title: str):
        section = self.find_element_by_locator_and_value(By.ID, SectionLocators.sectionColumn + section_id)
        self.send_keys_to_nested_element(section, TestCaseLocators.case_title_inline, title)

    def press_add_test_case_button(self):
        self.driver.implicitly_wait(3)
        try:
            first = self.find_elements_by_locator(TestCaseLocators.add_first_testcase)
            if len(first) > 0:
                self.press_add_first_testcase_button()
            else:
                self.click_element(TestCaseLocators.addCase)
        finally:
            self.driver.implicitly_wait(10)

    def confirm_adding_testcase_inline(self, section: WebElement):
        self.click_nested_element(section, TestCaseLocators.case_confirm_inline)
        self.wait_until_not_busy()

    def insert_test_data_to_testcase_text(self, test_case: TestCase):
        self.send_keys_to_element(TestCaseLocators.case_title, test_case.title)
        if test_case.section is not None:
            self.select_option_value_on_element(TestCaseLocators.case_section, str(test_case.section))
        self.select_option_value_on_element(TestCaseLocators.case_template, str(1))
        self.select_option_value_on_element(TestCaseLocators.case_type, str(test_case.type))
        self.select_option_value_on_element(TestCaseLocators.case_priority, str(test_case.priority))
        self.send_keys_to_element(TestCaseLocators.case_estimate, test_case.estimate)
        self.send_keys_to_element(TestCaseLocators.case_refs, test_case.refs)
        self.select_option_value_on_element(TestCaseLocators.case_custom_automation_type, str(test_case.custom_automation_type))
        self.send_keys_to_element(TestCaseLocators.case_custom_preconds, test_case.preconditions)
        self.send_keys_to_element(TestCaseLocators.case_custom_steps, test_case.steps)
        self.send_keys_to_element(TestCaseLocators.case_custom_expected, test_case.expected_result)

    def confirm_test_case(self):
        self.wait_for_blockui_to_close()
        self.wait_until_not_busy()
        self.click_element(TestCaseLocators.case_accept)

    def verify_test_case(self, test_case: TestCase, message: str)-> TestCase:
        self.validate_element_text(GeneralLocators.message_success, message)
        test_case.id = self.find_element_by_locator(TestCaseLocators.overview_id).text
        self.click_element(GeneralLocators.edit)
        self._check_test_case(test_case)
        return test_case

    def _check_test_case(self, test_case):
        self.validate_element_value(TestCaseLocators.case_title, test_case.title)
        self.validate_selected_option_value_on_element(TestCaseLocators.case_template, str(1))
        self.validate_selected_option_value_on_element(TestCaseLocators.case_type, str(test_case.type))
        self.validate_selected_option_value_on_element(TestCaseLocators.case_priority, str(test_case.priority))
        self.validate_element_value(TestCaseLocators.case_estimate, test_case.estimate)
        self.validate_element_value(TestCaseLocators.case_refs, test_case.refs)
        self.validate_selected_option_value_on_element(TestCaseLocators.case_custom_automation_type, str(test_case.custom_automation_type))
        self.validate_element_value(TestCaseLocators.case_custom_preconds, test_case.preconditions)
        self.validate_element_value(TestCaseLocators.case_custom_steps, test_case.steps)
        self.validate_element_value(TestCaseLocators.case_custom_expected, test_case.expected_result)

    def validate_test_case_on_list(self, section_name:str, test_case:TestCase):
        section, id = self.get_section(section_name)
        self.find_nested_element_by_locator_and_value(section, By.LINK_TEXT, str(test_case.id))
        self.find_nested_element_by_locator_and_value(section, By.LINK_TEXT, str(test_case.title))

    def validate_test_case_inline(self, section_name:str, test_case:TestCase)->int:
        section, id = self.get_section(section_name)
        test = self.find_nested_element_by_locator_and_value(section, By.LINK_TEXT, str(test_case.title))
        url = self.get_attribute_value_from_element(test, "href")
        return self.retrieve_id_from_url(url)

    def edit_test_case(self, edit_case:TestCase):
        self.click_element(GeneralLocators.edit)
        self.clear_element_data(TestCaseLocators.case_title)
        self.send_keys_to_element(TestCaseLocators.case_title, edit_case.title)
        self.select_option_value_on_element(TestCaseLocators.case_template, str(1))
        self.select_option_value_on_element(TestCaseLocators.case_type, str(edit_case.type))
        self.select_option_value_on_element(TestCaseLocators.case_priority, str(edit_case.priority))
        self.clear_element_data(TestCaseLocators.case_estimate)
        self.send_keys_to_element(TestCaseLocators.case_estimate, edit_case.estimate)
        self.clear_element_data(TestCaseLocators.case_refs)
        self.send_keys_to_element(TestCaseLocators.case_refs, edit_case.refs)
        self.select_option_value_on_element(TestCaseLocators.case_custom_automation_type, str(edit_case.custom_automation_type))
        self.clear_element_data(TestCaseLocators.case_custom_preconds)
        self.send_keys_to_element(TestCaseLocators.case_custom_preconds, edit_case.preconditions)
        self.clear_element_data(TestCaseLocators.case_custom_steps)
        self.send_keys_to_element(TestCaseLocators.case_custom_steps, edit_case.steps)
        self.clear_element_data(TestCaseLocators.case_custom_expected)
        self.send_keys_to_element(TestCaseLocators.case_custom_expected, edit_case.expected_result)

    def edit_test_case_title_inline(self, section_name, title, new_title):
        section, id = self.get_section(section_name)
        title_element = self.find_nested_element_by_locator_and_value(section, By.LINK_TEXT, title)
        hover = ActionChains(self.driver).move_to_element(title_element)
        hover.perform()
        hover.pause(0.1)

        # refresh elements
        section, id = self.get_section(section_name)
        self.click_nested_element(section, TestCaseLocators.edit_title_image(title))

        self.wait_for_element_to_be_visible(GeneralLocators.dialog)
        self.clear_element_data(TestCaseLocators.case_title_edit)
        self.send_keys_to_element(TestCaseLocators.case_title_edit, new_title)
        self.click_element(TestCaseLocators.case_edit_title_submit)

    def get_first_test_case_title(self):
        test_case = self.find_element_by_locator(TestCaseLocators.first_test_case)
        return test_case.text

    def check_test_case(self, section_name, test_case):
        title = test_case.title
        section, id = self.get_section(section_name)
        title_element = self.find_nested_element_by_locator_and_value(section, By.LINK_TEXT, title)
        hover = ActionChains(self.driver).move_to_element(title_element)
        hover.perform()
        hover.pause(0.1)

        section, id = self.get_section(section_name)
        self.click_nested_element(section, TestCaseLocators.edit_case_image(title))
        self._check_test_case(test_case)

    def add_multiple_test(self, test_cases, test_case_url, default_section_name, message):
        test_case = decode_data(str(test_cases[0]))
        self.press_add_first_testcase_button()
        self.insert_test_data_to_testcase_text(test_case)
        self.confirm_test_case()
        test_case = self.verify_test_case(test_case, message)
        self.open_page(test_case_url)
        self.validate_test_case_on_list(default_section_name, test_case)
        for case in test_cases[1:]:
            case = decode_data(str(case))
            case.section = None
            self.press_add_test_case_button()
            self.insert_test_data_to_testcase_text(case)
            self.confirm_test_case()
            case = self.verify_test_case(case, message)
            self.open_page(test_case_url)
            self.validate_test_case_on_list(default_section_name, case)

    def add_tests(self, *cases):
        for case in cases:
            self.click_element(GeneralLocators.test_cases)
            self.press_add_test_case_button()
            self.insert_test_data_to_testcase_text(case)
            self.confirm_test_case()

    def delete_test_case(self, name, message):
        self.wait_until_not_busy()
        self.click_element((By.LINK_TEXT, name))
        self.click_element(TestCaseLocators.case_edit)
        self.click_element(TestCaseLocators.case_delete)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)
        self.validate_element_text(GeneralLocators.message_success, message)

    def add_attachment(self, filename, with_edit=False):
        if with_edit:
            self.click_element(GeneralLocators.edit)
        # It's the attachment input at position 3 we need to set the filename on
        attachment_index = 3
        self.set_attachment_on_input(3, filename)

    def verify_text_attachment(self, attachment_path):
        filename = os.path.basename(attachment_path)
        # Verify the attachment exists, has the correct name and description (size and type)
        attachment = self.find_element_by_locator((By.LINK_TEXT, filename))
        description = self.find_element_by_locator(TestCaseLocators.attachment_description)
        assert description.text == 'Text Document, 79B'

        cookies = self.driver.get_cookies()
        href = self.get_attribute_value_from_element(attachment, 'href')
        s = requests.Session()
        requests_cookies = [s.cookies.set(c['name'], c['value']) for c in cookies]
        resp = s.get(href)
        browser_version = resp.text
        original = open(attachment_path).read()
        assert browser_version == original

    def open_test_case(self):
        # go to case page
        link = self.find_element_by_locator(TestCaseLocators.case_in_test_run)
        href = link.get_attribute('href')
        self.open_page(href)

    def add_test_result(self):
        self.click_element(TestCaseLocators.case_add_result)
        self.select_item_from_dropdown(TestCaseLocators.case_add_result_status, visible_text="Passed")
        self.select_item_from_dropdown(TestCaseLocators.case_add_result_assigned_to, visible_text="Me")
        self.send_keys_to_element(TestCaseLocators.case_add_result_comment, "Comment for test case Result")
        self.click_element(TestCaseLocators.case_add_result_submit)
        change = self.find_element_by_locator(TestCaseLocators.case_edit_change)
        return self.retrieve_id_from_string(change.get_attribute('id'))

    def edit_result_comment(self, comment, change_id=None):
        if change_id:
            result_edit_link = self.find_element_by_locator((By.ID, TestCaseLocators.case_edit_change_id.format(change_id)))
        else:
            result_edit_link = self.find_element_by_locator(TestCaseLocators.case_edit_change)

        result_edit_link.click()
        dialog = self.find_element_by_locator(TestCaseLocators.case_add_result_dialog)
        comment_area = self.find_nested_element(dialog, TestCaseLocators.case_add_result_comment)
        comment_area.clear()
        comment_area.send_keys(comment)

        self.select_item_from_dropdown(TestCaseLocators.case_add_result_status, visible_text="Blocked")
        self.select_item_from_dropdown(TestCaseLocators.case_add_result_assigned_to, visible_text="Nobody (Unassigned)")

        self.click_element(TestCaseLocators.case_add_result_submit)
        # wait for action complete
        self.wait_until_not_busy()
        time.sleep(1)

    def delete_attachment(self, filename):
        self.click_element(GeneralLocators.edit)
        attachment = self.find_element_by_locator((By.LINK_TEXT, filename))
        hover = ActionChains(self.driver).move_to_element(attachment)
        hover.perform()
        self.click_element(TestCaseLocators.delete_attachment)
        dialog = self.find_element_by_locator(GeneralLocators.dialog)
        self.click_nested_element(dialog, GeneralLocators.ok)

        self.confirm_test_case()

    def verify_no_attachment(self, filename, message):
        self.validate_element_text(GeneralLocators.message_success, message)
        self.click_element(GeneralLocators.edit)
        attachments = self.find_elements_by_locator((By.LINK_TEXT, filename))
        assert len(attachments) == 0

    def _perform_drag_and_drop_case(self, case_name, section_id):
        drag_target_locator = TestCaseLocators.drag_target_from_section_id(section_id)
        drag_target = self.find_element_by_locator(drag_target_locator)

        case_row_locator = TestCaseLocators.row_containing_testcase(case_name)
        case_row = self.find_element_by_locator(case_row_locator)
        case_dragger = self.find_nested_element(case_row, TestCaseLocators.case_dragger)

        chain = ActionChains(self.driver)
        chain.drag_and_drop(case_dragger, drag_target)
        chain.perform()

    def copy_case(self, case_name, section_id):
        self._perform_drag_and_drop_case(case_name, section_id)
        self.wait_for_element_to_be_visible(TestCaseLocators.drag_menu_copy)
        self.click_element(TestCaseLocators.drag_menu_copy)

    def move_case(self, case_name, section_id):
        self._perform_drag_and_drop_case(case_name, section_id)
        self.wait_for_element_to_be_visible(TestCaseLocators.drag_menu_move)
        self.click_element(TestCaseLocators.drag_menu_move)

    def open_test_case_in_run(self, run_url, case_name):
        # go to case page
        self.open_page(run_url)
        selected_case = self.find_element_by_locator_and_value(By.LINK_TEXT, case_name)
        href = selected_case.get_attribute('href')
        self.open_page(href)
        return href

    def add_result(self, test_result:TestResult):
        self.open_add_result_dialog()
        self.select_item_from_dropdown(TestCaseLocators.case_add_result_status, test_result.status)
        self.select_item_from_dropdown(TestCaseLocators.case_add_result_assigned_to, test_result.assigned_to)
        self.send_keys_to_element(TestCaseLocators.case_add_result_comment,test_result.comment)
        self.click_element(TestCaseLocators.case_add_result_submit)
        self.refresh_page()
        return self.extract_id_from_latest_result()

    def extract_id_from_latest_result(self) -> id:
        self.resultsContainer = self.find_element_by_locator(TestCaseLocators.resultsContainer)
        self.container = self.find_nested_element(self.resultsContainer, TestCaseLocators.change_container)
        self.test_result = self.find_nested_element(self.resultsContainer, TestCaseLocators.change_top)
        return self.retrieve_id_from_string(self.test_result.get_attribute('id'))

    def open_test_result(self, change_id):
        self.click_element(TestCaseLocators.case_add_result)

    def edit_test_result(self, test_result:TestResult):
        self.click_element(TestCaseLocators.case_edit)

        dialog = self.find_element_by_locator(TestCaseLocators.case_add_result_dialog)

        if test_result.comment is not None:
            comment_area = self.find_nested_element(dialog, TestCaseLocators.case_add_result_comment)
            comment_area.clear()
            comment_area.send_keys(test_result.comment)

        if test_result.status is not None:
            self.select_item_from_dropdown(TestCaseLocators.case_add_result_status, visible_text=test_result.status)

        if test_result.assigned_to is not None:
            self.select_item_from_dropdown(TestCaseLocators.case_add_result_assigned_to, visible_text=test_result.assigned_to)

        if test_result.version is not None:
            self.clear_element_data(TestCaseLocators.case_add_result_version)
            self.send_keys_to_element(TestCaseLocators.case_add_result_version, test_result.version)

        if test_result.elapsed is not None:
            self.clear_element_data(TestCaseLocators.case_add_result_elapsed)
            self.send_keys_to_element(TestCaseLocators.case_add_result_elapsed, test_result.elapsed)

        if test_result.defects is not None:
            self.clear_element_data(TestCaseLocators.case_add_result_defects)
            self.send_keys_to_element(TestCaseLocators.case_add_result_defects, test_result.defects)

        self.click_element(TestCaseLocators.case_add_result_submit)

    def validate_test_result(self, test_result:TestResult):
        # testresult = self.find_element_by_locator_and_value(By.ID, TestCaseLocators.case_change.format(test_result.id))
        # edit_test_result = self.find_nested_element(testresult, TestCaseLocators.case_edit_change)
        # self.click_nested_element(edit_test_result, (By.CSS_SELECTOR, "a"))
        self.click_element(TestCaseLocators.case_edit)

        if test_result.comment is not None:
            self.validate_element_text(TestCaseLocators.case_add_result_comment, test_result.comment)

        if test_result.status is not None:
            self.validate_selected_option_text_on_element(TestCaseLocators.case_add_result_status, test_result.status)

        if test_result.assigned_to is not None:
            self.validate_selected_option_text_on_element(TestCaseLocators.case_add_result_assigned_to, test_result.assigned_to)

        if test_result.version is not None:
            self.validate_element_text(TestCaseLocators.case_add_result_version, test_result.version)

        if test_result.elapsed is not None:
            self.validate_element_text(TestCaseLocators.case_add_result_elapsed, test_result.elapsed)

        if test_result.defects is not None:
            self.validate_element_text(TestCaseLocators.case_add_result_defects, test_result.defects)

        self.click_element(TestCaseLocators.case_add_result_close)

    def validate_top_test_result_comment(self, test_url, result_id, text):
        self.open_page(test_url)
        test_result = self.find_element_by_locator_and_value(By.ID, TestCaseLocators.case_change.format(result_id))
        self.validate_nested_element_text(test_result, TestCaseLocators.case_column_comment, text)

    def open_add_result_dialog(self):
        self.click_element(TestCaseLocators.case_add_result)

    def verify_add_and_push_defect_links_are_visible(self):
        dialog = self.find_element_by_locator(TestCaseLocators.case_add_result_dialog)
        self.find_nested_element(dialog, TestCaseLocators.case_add_defect)
        push_defect_link = self.find_element_by_locator(TestCaseLocators.case_push_defect_link)
        self.find_nested_element(push_defect_link, TestCaseLocators.case_push_defect)

    def click_push_defect_and_verify_dialog(self):
        push_defect_link = self.find_element_by_locator(TestCaseLocators.case_push_defect_link)
        push_defect_btn = self.find_nested_element(push_defect_link, TestCaseLocators.case_push_defect)
        push_defect_btn.click()
        self.wait_for_element_to_be_visible(TestCaseLocators.case_push_defect_dialog)
        dialog = self.find_element_by_locator(TestCaseLocators.case_push_defect_dialog)
        ui_dialog_title = self.find_element_by_locator(TestCaseLocators.case_push_defect_dialog_title)
        assert ui_dialog_title.text == 'Push Defect'
        self.find_nested_element(dialog, GeneralLocators.cancel).click()

    def click_add_defect_and_verify_redirection(self):
        dialog = self.find_element_by_locator(TestCaseLocators.case_add_result_dialog)
        add_defect_link = self.find_nested_element(dialog, TestCaseLocators.case_add_defect)

        try:
            add_defect_link.click()
            time.sleep(1.5)
            assert self.get_windows_count() > 1
            self.switch_to_window(1)
            self.close_tab()
        finally:
            self.switch_to_window(0)

    def verify_edit_result_visibility(self, change_id, visibility:bool):
        test_result = self.find_element_by_locator_and_value(By.ID, TestCaseLocators.case_change.format(change_id))
        assert self.validate_nested_element_visibility(test_result, TestCaseLocators.case_edit_change) == visibility
