import os
import pytest

import src.pages.administration.project_page as project_page
import src.pages.project.sections_page as section_page
import src.pages.project.testcases_page as cases_page
from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config


class TestCaseBase(BaseTest):

    @classmethod
    def setup_class(cls):
        # Get test data
        super().setup_class()

        cls.p = read_config('../config/project.json')
        cls.t = read_config("../config/tests.json")

        # Prepare page objects
        cls.section = section_page.SectionsPage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)
        cls.tests = cases_page.TestCasesPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.section.open_page(self.data.server_name + self.p.suites.view_url + self.suite_id)

    def teardown_method(self):
        self.section.open_page(self.data.server_name)

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.project.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        cls.project_id = cls.project.add_single_repo_project(cls.p.project_info.project_name)
        cls.project.open_page(cls.data.server_name + cls.p.project_overview_url + cls.project_id)
        cls.suite_id = cls.section.open_test_cases()

    @classmethod
    def delete_prepared_data(cls):
        projects_overview_url = (cls.data.server_name + cls.p.overview_url)
        message = cls.p.messages.msg_success_deleted_project

        cls.project.open_page(projects_overview_url)
        cls.project.delete_project(cls.p.project_info.project_name)
        cls.project.validate_success_message(message)


class TestTestCases(TestCaseBase):

    @pytest.mark.testrail(ids=[220, 224])
    @pytest.mark.dependency(name="test_add_first_test_case_success")
    @pytest.mark.run(order=1)
    def test_add_first_test_case_success(self):
        test_case = decode_data(str(self.t.cases[0]))
        message = self.t.messages.msg_success_added_test_case
        default_section_name = self.t.default_section_name

        self.tests.press_add_first_testcase_button()
        self.tests.insert_test_data_to_testcase_text(test_case)
        self.tests.confirm_test_case()
        test_case = self.tests.verify_test_case(test_case, message)
        self.tests.open_page(self.data.server_name + self.p.suites.view_url + self.suite_id)
        self.tests.validate_test_case_on_list(default_section_name, test_case)

    @pytest.mark.testrail(id=215)
    @pytest.mark.dependency(name="test_add_first_test_case_to_section", depends=["test_add_first_test_case_success"])
    @pytest.mark.run(order=2)
    def test_add_first_test_case_to_section(self):
        test_case = decode_data(str(self.t.cases[1]))
        message = self.t.messages.msg_success_added_test_case

        self.section.add_section(self.p.sections.section_name, self.p.sections.section_description)
        self.section.press_add_section_button()
        test_case.section = self.section.retrieve_id_from_group(self.p.sections.section_name)
        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(test_case)
        self.tests.confirm_test_case()
        test_case = self.tests.verify_test_case(test_case, message)
        self.tests.open_page(self.data.server_name + self.p.suites.view_url + self.suite_id)
        self.tests.validate_test_case_on_list(self.p.sections.section_name, test_case)

    @pytest.mark.testrail(id=216)
    @pytest.mark.dependency(depends=["test_add_first_test_case_success"])
    @pytest.mark.run(order=3)
    def test_add_subsequent_tests_to_section(self):
        cases = []
        cases.append(decode_data(str(self.t.cases[0])))
        cases.append(decode_data(str(self.t.cases[1])))
        cases.append(decode_data(str(self.t.cases[2])))
        cases.append(decode_data(str(self.t.cases[3])))
        message = self.t.messages.msg_success_added_test_case
        section = self.section.retrieve_id_from_group(self.p.sections.section_name)

        for case in cases:
            case.section = section
            self.tests.press_add_test_case_button()
            self.tests.insert_test_data_to_testcase_text(case)
            self.tests.confirm_test_case()
            case = self.tests.verify_test_case(case, message)
            self.tests.open_page(self.data.server_name + self.p.suites.view_url + self.suite_id)
            self.tests.validate_test_case_on_list(self.p.sections.section_name, case)

    @pytest.mark.dependency(name="test_add_first_test_to_section_inline", depends=["test_add_first_test_case_to_section"])
    @pytest.mark.run(order=3)
    def test_add_first_test_to_section_inline(self):
        case = decode_data(str(self.t.cases[0]))

        section, id = self.section.get_section(self.p.sections.section_name)
        case.section = self.section.retrieve_id_from_group(self.p.sections.section_name)
        self.tests.press_add_test_inline(str(case.section))
        self.tests.add_test_case_inline(str(case.section), case.title)
        self.tests.confirm_adding_testcase_inline(section)
        case.id = self.tests.validate_test_case_inline(self.p.sections.section_name, case)

    @pytest.mark.testrail(id=217)
    @pytest.mark.dependency(depends=["test_add_first_test_to_section_inline"])
    @pytest.mark.run(order=4)
    def test_add_subsequent_test_to_section_inline(self):
        cases = []
        cases.append(decode_data(str(self.t.cases[1])))
        cases.append(decode_data(str(self.t.cases[2])))
        cases.append(decode_data(str(self.t.cases[3])))

        section, id = self.section.get_section(self.p.sections.section_name)
        self.tests.press_add_test_inline(str(id))
        for case in cases:
            self.tests.add_test_case_inline(str(id), case.title)
            self.tests.confirm_adding_testcase_inline(section)
            case.id = self.tests.validate_test_case_inline(self.p.sections.section_name, case)

    @pytest.mark.testrail(id=232)
    @pytest.mark.dependency(depends=["test_add_first_test_to_section_inline"])
    @pytest.mark.run(order=5)
    def test_delete_case(self):
        test_case = decode_data(str(self.t.cases[3]))
        message = self.t.messages.msg_success_added_test_case
        default_section_name = self.t.default_section_name

        section, id = self.section.get_section(default_section_name)
        self.tests.press_add_test_inline(id)
        self.tests.add_test_case_inline(id, test_case.title)
        self.tests.confirm_adding_testcase_inline(section)

        self.tests.delete_test_case(test_case.title, self.t.messages.msg_success_deleted_test_case)


class TestAttachmentsAndCaseEdits(TestCaseBase):

    @pytest.mark.testrail(id=219)
    def test_c219_add_case_with_attachment(self):
        test_case = decode_data(str(self.t.cases[0]))
        attachment_path = os.path.abspath('../data/text_file.txt')

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(test_case)
        self.tests.add_attachment(attachment_path)
        self.tests.confirm_test_case()
        self.tests.verify_text_attachment(attachment_path)

    @pytest.mark.testrail(id=228)
    def test_c228_change_and_check_case_properties(self):
        original = decode_data(str(self.t.cases[0]))
        edited = decode_data(str(self.t.cases[1]))
        message = self.t.messages.msg_success_edited_test_case

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(original)
        self.tests.confirm_test_case()

        self.tests.edit_test_case(edited)
        self.tests.confirm_test_case()
        self.tests.verify_test_case(edited, message)

    @pytest.mark.testrail(id=229)
    def test_c229_add_attachment(self):
        case = decode_data(str(self.t.cases[0]))
        message = self.t.messages.msg_success_edited_test_case
        attachment_path = os.path.abspath('../data/text_file.txt')

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(case)
        self.tests.confirm_test_case()

        self.tests.add_attachment(attachment_path, with_edit=True)
        self.tests.confirm_test_case()
        self.tests.verify_text_attachment(attachment_path)

    @pytest.mark.testrail(id=230)
    def test_c230_delete_attachment(self):
        test_case = decode_data(str(self.t.cases[0]))
        attachment_path = os.path.abspath('../data/text_file.txt')
        message = self.t.messages.msg_success_edited_test_case

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(test_case)
        self.tests.add_attachment(attachment_path)
        self.tests.confirm_test_case()

        self.tests.delete_attachment('text_file.txt')
        self.tests.verify_no_attachment('text_file.txt', message)

    @pytest.mark.testrail(id=233)
    def test_c233_delete_last_case_in_section(self):
        case1 = decode_data(str(self.t.cases[1]))
        case2 = decode_data(str(self.t.cases[2]))
        case3 = decode_data(str(self.t.cases[3]))
        message = self.t.messages.msg_success_added_test_case
        del_message = self.t.messages.msg_success_deleted_test_case

        self.section.add_section(self.p.sections.section_name)
        self.section.press_add_section_button()
        section, id = self.section.get_section(self.p.sections.section_name)

        self.tests.press_add_test_inline(str(id))
        for case in case1, case2, case3:
            self.tests.add_test_case_inline(str(id), case.title)
            self.tests.confirm_adding_testcase_inline(section)

        self.tests.delete_test_case(case1.title, del_message)
        self.tests.delete_test_case(case2.title, del_message)
        self.tests.delete_test_case(case3.title, del_message)

    @pytest.mark.testrail(id=237)
    def test_c237_inline_edit_case_title(self):
        case = decode_data(str(self.t.cases[0]))
        case2 = decode_data(str(self.t.cases[1]))
        message = self.t.messages.msg_success_edited_test_case
        default_section_name = self.t.default_section_name

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(case)
        self.tests.confirm_test_case()

        self.section.open_test_cases()
        self.tests.edit_test_case_title_inline(default_section_name, case.title, case2.title)
        self.tests.validate_test_case_inline(default_section_name, case2)


class TestDragAndDrop(TestCaseBase):

    def setup_method(self):
        super().setup_method()
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        suite_overview_url = self.data.server_name + self.p.suites.view_url + self.suite_id
        case = decode_data(str(self.t.cases[0]))
        case2 = decode_data(str(self.t.cases[1]))
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section
        message = self.t.messages.msg_success_added_test_case

        self.section.open_page(project_overview_url)
        self.section.open_test_cases()

        self.section.add_first_section(first_section)
        self.section.press_add_section_button()
        self.section.add_subsequent_section(second_section)

        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(case)
        self.tests.confirm_test_case()
        self.tests.verify_test_case(case, message)

        self.section.open_page(suite_overview_url)
        self.tests.press_add_test_case_button()
        self.tests.insert_test_data_to_testcase_text(case2)
        self.tests.confirm_test_case()
        self.tests.verify_test_case(case2, message)
        self.section.open_page(suite_overview_url)

        self.cases = [case, case2]


    def teardown_method(self):
        # Deleting sections deletes subsections, so we delete in a loop fetching
        # a fresh list of sections each time.
        while True:
            sections = self.section.fetch_section_names()
            if not sections:
                break
            next_section = sections.pop()
            self.section.delete_section(next_section)

    @pytest.mark.testrail(id=242)
    def test_c242_move_case(self):
        case1, case2 = self.cases
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section

        section_id = self.section.retrieve_id_from_group(second_section)
        self.tests.move_case(case1.title, section_id)

        self.tests.validate_test_case_on_list(second_section, case1)
        self.tests.validate_test_case_on_list(first_section, case2)

    @pytest.mark.testrail(id=241)
    def test_c241_copy_case(self):
        case1, case2 = self.cases
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section

        section_id = self.section.retrieve_id_from_group(second_section)
        self.tests.copy_case(case2.title, section_id)

        self.tests.validate_test_case_on_list(first_section, case1)
        self.tests.validate_test_case_on_list(first_section, case2)
        case2.id = self.tests.validate_test_case_inline(second_section, case2)
        self.tests.check_test_case(second_section, case2)


if __name__ == "__main__":
    pytest.main()
