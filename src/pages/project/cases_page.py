from src.locators.project.cases_locators import CaseLocators
from src.pages.base_element import BasePageElement
from src.pages.base_page import BasePage


class CasesPage(BasePage, BasePageElement):

    def add_assignee_to_cases(self, users_names:list):
        test_cases = self.find_elements_by_locator(CaseLocators.case_assigned)
        for index, ele in enumerate(test_cases):
            self.case_add_assignee(ele, users_names[index])

    def validate_assignees_to_cases(self, users_names:list):
        validate_test_cases = self.find_elements_by_locator(CaseLocators.case_assigned)
        for index, ele in enumerate(validate_test_cases):
            self.case_validate_assignee(ele, users_names[index])

    def case_add_assignee(self, ele, name:str):
        ele.click()
        dialog = self.find_element_by_locator(CaseLocators.case_assign_dialog)
        self.select_option_text_on_nested_element(dialog, CaseLocators.case_assign_select, name)
        self.click_element(CaseLocators.case_assign_submit)
        self.wait_for_element_to_be_invisible(CaseLocators.case_assign_dialog)

    def case_validate_assignee(self, ele, name:str):
        name = name.split(" ")
        name = " ".join(name[0:len(name)-1]) + " " + name[-1][:1] + "." if len(name) > 1 else name[0]
        assert str(ele.text) == name

    def validate_all_tests_assignee(self, name:str):
        validate_test_cases = self.find_elements_by_locator(CaseLocators.case_assigned)
        for ele in validate_test_cases:
            self.case_validate_assignee(ele, name)

    def validate_cases_for_run(self, name, count):
        assert len(self.find_elements_by_locator(CaseLocators.case_assigned)) == count
        self.validate_all_tests_assignee(name)
