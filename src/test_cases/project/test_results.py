import os
import pytest
import time

from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config
from src.models.administration.user import User
import src.pages.administration.project_page as project_page
import src.pages.project.runs_page as runs_page
from src.pages.project import results_page
from src.pages.project import testcases_page
from src.models.project.test_cases import TestResult
from src.helpers.prepare_data import PrepareData
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.project.runs_page import RunsPage
from src.pages.administration.integration_page import IntegrationPage
import src.pages.project.sections_page as section_page
import src.pages.project.testcases_page as cases_page

class TestResults(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.result_data = read_config('../config/results.json')
        cls.results = results_page.ResultsPage(cls.driver)

        cls.r = read_config('../config/runs.json')
        cls.runs = runs_page.RunsPage(cls.driver)

        cls.p = read_config('../config/project.json')
        cls.project = project_page.ProjectPage(cls.driver)

        cls.t = read_config('../config/tests.json')
        cls.tests = testcases_page.TestCasesPage(cls.driver)

        cls.u = read_config('../config/users.json')
        cls.users = UsersRolesPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.runs.open_page(self.data.server_name)
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.run_id = self.runs.add_data_to_run(run.name, run.description)
        self.view_run_url = self.data.server_name + self.r.run_view_url + self.run_id
        self.results.open_page(self.view_run_url)

    def teardown_method(self):
        edit_run_url = self.data.server_name + self.r.edit_url + self.run_id
        self.runs.open_page(edit_run_url)
        self.runs.delete_run()

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        cls.project_id = cls.project.add_single_repo_project(cls.p.project_info.project_name)

        case1 = decode_data(str(cls.t.cases[0]))
        case2 = decode_data(str(cls.t.cases[1]))
        case3 = decode_data(str(cls.t.cases[2]))

        cls.tests.open_page(cls.data.server_name + cls.r.overview_url + cls.project_id)
        cls.tests.add_tests(case1, case2, case3)
        cls.cases = [case1, case2, case3]

        full_name = cls.r.add.user_full_name
        email_address = cls.r.add.user_email_address
        password = cls.r.add.user_password
        user = User(full_name, email_address, password)
        cls.users.open_page(cls.data.server_name + cls.u.overview_url)
        cls.users.add_user(user)

    @classmethod
    def delete_prepared_data(cls):
        projects_overview_url = (cls.data.server_name + cls.p.overview_url)
        message = cls.p.messages.msg_success_deleted_project

        cls.project.open_page(projects_overview_url)
        cls.project.delete_project(cls.p.project_info.project_name)
        cls.project.validate_success_message(message)

        full_name = cls.r.add.user_full_name
        cls.users.open_page(cls.data.server_name + cls.u.overview_url)
        cls.users.forget_user(full_name)

    @pytest.mark.testrail(id=365)
    def test_c365_add_first_result(self):
        status = self.result_data.statuses[0]
        case = self.cases[0]

        self.results.expand_case(case.title)
        self.results.add_result_with_status(status)

        self.results.assert_status(case.title, status)

    @pytest.mark.testrail(id=366)
    def test_c366_add_subsequent_results(self):
        status = self.result_data.statuses[0]

        for case in self.cases:
            self.results.expand_case(case.title)
            self.results.add_result_with_status(status)

        for case in self.cases:
            self.results.assert_status(case.title, status)

    @pytest.mark.testrail(ids=[367, 368, 369, 370])
    @pytest.mark.parametrize('status', read_config('../config/results.json').statuses)
    def test_c367_c368_c369_c370_statuses(self, status):
        case = self.cases[0]

        self.results.expand_case(case.title)
        self.results.add_result_with_status(status)

        self.results.assert_status(case.title, status)

    @pytest.mark.testrail(id=371)
    def test_c371_add_result_with_attachment(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        attachment_path = os.path.abspath('../data/text_file.txt')
        attachment_title = os.path.basename(attachment_path)
        attachment_description = self.result_data.text_attachment_description

        self.results.expand_case(case.title)
        self.results.add_result_with_dropzone_attachment(status, attachment_path)
        self.results.assert_attachment_title_and_description(attachment_title, attachment_description)

    @pytest.mark.testrail(id=376)
    def test_c376_add_result_with_image(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]

        attachment_path = os.path.abspath('../data/python-image.png')
        attachment_title = os.path.basename(attachment_path)
        self.results.add_result_with_image_attachment(status, attachment_path)

        self.results.assert_image_attachment(attachment_path)

    @pytest.mark.testrail(id=374)
    def test_c374_edit_test_result(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        comment = self.result_data.comment

        self.results.expand_case(case.title)
        self.results.add_result_with_status(status)
        self.results.edit_result(comment)
        self.results.assert_comment(comment)

    @pytest.mark.testrail(id=380)
    def test_c380_assign_to_user_account(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        user = self.data.login.full_name

        self.results.expand_case(case.title)
        self.results.add_result_with_status_no_confirm(status)
        self.results.assign_to("Me")
        self.results.confirm_add_result()

        self.results.assert_assigned_to(user)

    @pytest.mark.testrail(id=381)
    def test_c381_assign_to_different_user(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        user = self.r.add.user_full_name

        self.results.expand_case(case.title)
        self.results.add_result_with_status_no_confirm(status)
        self.results.assign_to(user)
        self.results.confirm_add_result()

        self.results.assert_assigned_to(user)

    @pytest.mark.testrail(id=383)
    def test_c383_add_comment(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        comment = self.result_data.comment

        self.results.expand_case(case.title)
        self.results.add_result_with_comment(status, comment)
        self.results.assert_comment(comment)

    @pytest.mark.testrail(id=384)
    def test_c384_edit_comment(self):
        case = self.cases[0]
        status = self.result_data.statuses[0]
        comment = self.result_data.comment
        edited = self.result_data.comment_edited

        self.results.expand_case(case.title)
        self.results.add_result_with_comment(status, comment)
        self.results.edit_result(edited)
        self.results.assert_comment(edited)

class TestModifyTestResults(BaseTest):

    @classmethod
    def setup_class(cls):
        # Get test data
        super().setup_class()

        cls.p = read_config('../config/project.json')
        cls.t = read_config("../config/tests.json")
        cls.users = read_config('../config/users.json')
        cls.site_settings = read_config('../config/site_settings.json')
        cls.runs = read_config('../config/runs.json')
        cls.plugin = read_config('../config/plugin.json')

        # Prepare page objects
        cls.section = section_page.SectionsPage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)
        cls.tests = cases_page.TestCasesPage(cls.driver)
        cls.run = RunsPage(cls.driver)
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.prepare_data = PrepareData(cls.driver)
        cls.integration = IntegrationPage(cls.driver)

        # Perquisites for tests execution
        cls.project_overview = cls.data.server_name + cls.p.project_overview_url
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.prepare_data.login_as_admin()
        self.case_name = self.prepare_data.add_test_case_inline(self.project_overview + self.project_id, self.p.sections.first_section)
        self.prepare_data.login_as_tester()
        self.run_url = self.data.server_name + self.runs.run_view_url + self.run_id
        self.test_url = self.tests.open_test_case_in_run(self.run_url, self.case_name)

    def teardown_method(self):
        self.tests.open_page(self.data.server_name)

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.setup_database(cls.t)
        cls.project.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        cls.project_id = cls.project.add_single_repo_project(cls.p.project_info.project_name)
        cls.prepare_data.add_first_section(cls.project_overview + cls.project_id)
        cls.run_id = cls.prepare_data.add_run_outside_plan(cls.project_overview + cls.project_id,cls.runs.runs[0],cls.runs.messages.msg_success_added_test_run)
        cls.prepare_data.add_tester_user()
        cls.prepare_data.add_tester_user_with_modify_test_results_permission()
        cls.prepare_data.add_lead_user()
        cls.prepare_data.prepare_jira_integration()

    @classmethod
    def delete_prepared_data(cls):
        cls.prepare_data.login_as_admin()
        cls.integration.open_page(cls.data.server_name + cls.plugin.integration_url)
        cls.integration.clear_integration_settings()
        cls.teardown_database()

    def login_as_tester_with_modify_permissions(self):
        self.driver.delete_all_cookies()
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.users.tester_user.email_address, self.users.tester_user.password)

    @pytest.mark.testrail(id=5845)
    def test_lead_cant_modify_test_results_by_default(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))
        edit_result = decode_data(str(self.runs.test_results.edit[0]))

        try:
            edit_result.id = self.tests.add_result(new_result)
            self.prepare_data.login_as_lead_user()
            self.run.open_page(self.test_url)
            self.tests.verify_edit_result_visibility(change_id=edit_result.id, visibility=False)
        finally:
            self.prepare_data.login_as_tester()

    @pytest.mark.testrail(id=5844)
    def test_check_admin_cant_modify_test_results_by_default(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))
        edit_result = decode_data(str(self.runs.test_results.edit[0]))

        try:
            edit_result.id = self.tests.add_result(new_result)
            self.prepare_data.login_as_admin()
            self.run.open_page(self.test_url)
            self.tests.verify_edit_result_visibility(change_id=edit_result.id, visibility=False)
        finally:
            self.prepare_data.login_as_tester()

    @pytest.mark.testrail(id=5736)
    def test_check_tester_can_modify_all_test_result_within_editing_period(self):
        first_result = decode_data(str(self.runs.test_results.add[0]))
        second_result = decode_data(str(self.runs.test_results.add[1]))

        first_result.id = self.tests.add_result(first_result)
        second_result.id = self.tests.add_result(second_result)
        self.prepare_data.login_as_tester()
        self.run.open_page(self.test_url)
        self.tests.verify_edit_result_visibility(change_id=first_result.id, visibility=True)
        self.tests.verify_edit_result_visibility(change_id=second_result.id, visibility=True)

    def test_check_tester_can_modify_own_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))
        edit_result = decode_data(str(self.runs.test_results.edit[1]))

        edit_result.id = self.tests.add_result(new_result)
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        # Added sleep as sometimes in this case driver are erroring on getting access to element after reload
        time.sleep(3)
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=5715)
    def test_check_tester_can_modify_own_test_result_status(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))
        edit_result = TestResult(status=self.runs.test_results.edit[0].status)

        edit_result.id = self.tests.add_result(new_result)
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=5716)
    def test_check_tests_can_modify_own_test_result_assigned_to(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))
        edit_result = TestResult(assigned_to=self.runs.test_results.edit[0].assigned_to)

        edit_result.id = self.tests.add_result(new_result)
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=5670)
    def test_check_tester_cant_modify_test_results_without_modify_permission(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))

        self.prepare_data.login_as_lead_user()
        self.test_url = self.tests.open_test_case_in_run(self.run_url, self.case_name)
        new_result.id = self.tests.add_result(new_result)
        self.prepare_data.login_as_tester()
        self.run.open_page(self.test_url)
        self.tests.verify_edit_result_visibility(change_id=new_result.id, visibility=False)

    @pytest.mark.testrail(id=5731)
    def test_check_tester_can_push_defects_to_own_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))

        new_result.id = self.tests.add_result(new_result)
        self.tests.open_test_result(change_id=new_result.id)
        self.tests.click_push_defect_and_verify_dialog()

    @pytest.mark.testrail(id=5730)
    def test_check_tester_can_add_defects_to_own_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[0]))

        new_result.id = self.tests.add_result(new_result)
        self.tests.open_test_result(change_id=new_result.id)
        self.tests.click_add_defect_and_verify_redirection()

    @pytest.mark.testrail(id=5671)
    def test_check_tester_with_modify_permission_can_modify_another_user_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))
        edit_result = decode_data(str(self.runs.test_results.edit[1]))

        edit_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=7470)
    def test_check_tester_with_modify_permissions_can_modify_all_test_result_within_editing_period(self):
        first_result = decode_data(str(self.runs.test_results.add[0]))
        second_result = decode_data(str(self.runs.test_results.add[1]))

        first_result.id = self.tests.add_result(first_result)
        second_result.id = self.tests.add_result(second_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        third_result_id = self.tests.add_result(first_result)
        self.tests.verify_edit_result_visibility(change_id=first_result.id, visibility=True)
        self.tests.verify_edit_result_visibility(change_id=second_result.id, visibility=True)
        self.tests.verify_edit_result_visibility(change_id=third_result_id, visibility=True)

    @pytest.mark.testrail(id=5673)
    def test_check_tester_with_modify_permission_can_modify_another_user_test_result_status(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))
        edit_result = TestResult(status=self.runs.test_results.edit[0].status)

        edit_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=5674)
    def test_check_tester_with_modify_permission_can_modify_another_user_test_result_assignee_set_others(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))
        edit_result = TestResult(assigned_to=self.users.lead_user.full_name)

        edit_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        self.tests.validate_test_result(edit_result)

    def test_check_tester_with_modify_permission_can_modify_another_user_test_result_assignee_set_myself(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))
        edit_result = TestResult(assigned_to=self.users.tester_user.full_name)

        edit_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.edit_test_result(edit_result)
        edit_result.assigned_to = "Me"
        self.tests.validate_test_result(edit_result)

    @pytest.mark.testrail(id=5675)
    def test_user_with_modify_permission_can_add_defect_to_existing_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))

        new_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.open_test_result(change_id=new_result.id)
        self.tests.click_add_defect_and_verify_redirection()

    @pytest.mark.testrail(id=5676)
    def test_user_with_modify_permission_can_push_defect_to_existing_test_result(self):
        new_result = decode_data(str(self.runs.test_results.add[1]))

        new_result.id = self.tests.add_result(new_result)
        self.login_as_tester_with_modify_permissions()
        self.run.open_page(self.test_url)
        self.tests.open_test_result(change_id=new_result.id)
        self.tests.click_push_defect_and_verify_dialog()
