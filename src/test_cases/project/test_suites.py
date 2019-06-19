import pytest
from src.test_cases.base_test import BaseTest
from src.common import read_config
from src.pages.project import suite_page
from src.pages.administration import project_page


class TestSuites(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        # Get test data
        cls.p = read_config('../config/project.json')
        cls.runs = read_config('../config/runs.json')

        # Prepare page objects
        cls.suite = suite_page.SuitePage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.suite_id = None
        self.suite.open_page(self.data.server_name)

    def teardown_method(self):
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        if self.suite_id is not None:
            self.suite.open_page(suites)
            self.suite.edit_suite_list(self.suite_id)
            self.suite.delete_suite()

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.suite.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        cls.project_id = cls.project.add_multi_repo_project(cls.p.project_info.project_name)

    @classmethod
    def delete_prepared_data(cls):
        projects_overview_url = (cls.data.server_name + cls.p.overview_url)
        message = cls.p.messages.msg_success_deleted_project

        cls.project.open_page(projects_overview_url)
        cls.project.delete_project(cls.p.project_info.project_name)
        cls.project.validate_success_message(message)

    def add_suite_with_first_run(self):
        name = self.p.suites.edit.name
        description = self.p.suites.edit.description
        add_suite = self.data.server_name + self.p.suites.add_url + self.project_id
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id

        self.suite.open_page(add_suite)
        suite_id = self.suite.add_data_to_suite(name, description)
        self.suite.open_page(suites)

        self.suite.run_test_on_suite_list(suite_id)
        self.suite.add_test_run_from_suite()
        self.suite.validate_success_message(self.runs.messages.msg_success_added_test_run)
        self.suite.open_page(suites)
        self.suite.check_runs_number(suite_id, 1)
        return suite_id

    @pytest.mark.run(order=1)
    def test_page_when_no_suites(self):
        self.suite.open_page(self.data.server_name + self.p.suites.overview_url + self.project_id)
        self.suite.verify_page_with_no_suites(self.p.suites.messages.no_suite_title)

    @pytest.mark.testrail(id=173)
    @pytest.mark.run(order=2)
    def test_add_first_empty_suite(self):
        name = self.p.suites.add[0].name
        description = self.p.suites.add[0].description
        message = self.p.suites.messages.msg_success_added_suite
        empty_message = self.p.suites.messages.no_cases_in_suite_title

        self.suite.open_page(self.data.server_name + self.p.suites.add_url + self.project_id)
        self.suite.add_data_to_suite(name, description)
        self.suite.validate_empty_suite(name, description, message, empty_message)

    @pytest.mark.testrail(id=174)
    @pytest.mark.run(order=3)
    def test_add_second_empty_suite(self):
        name = self.p.suites.add[1].name
        description = self.p.suites.add[1].description
        message = self.p.suites.messages.msg_success_added_suite
        empty_message = self.p.suites.messages.no_cases_in_suite_title

        self.suite.open_page(self.data.server_name + self.p.suites.add_url + self.project_id)
        self.suite.add_data_to_suite(name, description)
        self.suite.validate_empty_suite(name, description, message, empty_message)

    @pytest.mark.testrail(ids=[178, 179])
    @pytest.mark.dependency(name="test_edit_suite")
    @pytest.mark.run(order=4)
    def test_edit_suite(self):
        name = self.p.suites.edit.name
        description = self.p.suites.edit.description
        edited_name = self.p.suites.edit.edited_name
        edited_desc = self.p.suites.edit.edited_description
        message = self.p.suites.messages.msg_success_edited_suite
        empty_message = self.p.suites.messages.no_cases_in_suite_title

        self.suite.open_page(self.data.server_name + self.p.suites.add_url + self.project_id)
        self.suite.add_data_to_suite(name, description)
        self.suite.edit_suite_details()
        self.suite.edit_suite(edited_name, edited_desc)
        self.suite.validate_empty_suite(edited_name, edited_desc, message, empty_message)

    @pytest.mark.testrail(id=180)
    @pytest.mark.dependency(depends=["test_edit_suite"])
    @pytest.mark.run(order=5)
    def test_delete_suite_without_runs(self):
        name = self.p.suites.edit.edited_name
        message = self.p.suites.messages.msg_success_deleted_suite

        self.suite.open_page(self.data.server_name + self.p.suites.overview_url + self.project_id)
        id = self.suite.get_suite_id(name)
        self.suite.edit_suite_list(id)
        self.suite.delete_suite()
        self.suite.validate_success_message(message)

    @pytest.mark.testrail(id=183)
    @pytest.mark.run(order=6)
    def test_add_run_to_suite_success_default_settings(self):
        message = self.p.suites.messages.msg_success_deleted_suite

        suite_id = self.add_suite_with_first_run()

        self.suite.edit_suite_list(suite_id)
        self.suite.delete_suite()
        self.suite.validate_success_message(message)

    @pytest.mark.testrail(id=181)
    @pytest.mark.run(order=7)
    def test_delete_suite_with_closed_run(self):
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        name = self.p.suites.edit.name
        message = self.p.suites.messages.msg_success_deleted_suite
        suite_id = self.add_suite_with_first_run()

        # Close the run
        self.suite.close_first_run(name)
        self.suite.open_page(suites)
        self.suite.check_runs_number(suite_id, 0)

        # Delete the suite
        self.suite.edit_suite_list(suite_id)
        self.suite.delete_suite()
        self.suite.validate_success_message(message)

    @pytest.mark.testrail(id=182)
    @pytest.mark.run(order=8)
    def test_delete_suite_with_closed_and_active_runs(self):
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        name = self.p.suites.edit.name
        message = self.p.suites.messages.msg_success_deleted_suite
        suite_id = self.add_suite_with_first_run()

        # Add a second run
        self.suite.run_test_on_suite_list(suite_id)
        self.suite.add_test_run_from_suite()
        self.suite.validate_success_message(self.runs.messages.msg_success_added_test_run)
        self.suite.open_page(suites)
        self.suite.check_runs_number(suite_id, 2)

        # Close one of the runs
        self.suite.close_first_run(name)
        self.suite.open_page(suites)
        self.suite.check_runs_number(suite_id, 1)

        # Delete the suite
        self.suite.edit_suite_list(suite_id)
        self.suite.delete_suite()
        self.suite.validate_success_message(message)

    @pytest.mark.testrail(id=191)
    def test_c191_grid_add_column(self):
        name = self.p.suites.edit.name
        column_type = self.p.suites.add_column_type
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        self.suite_id = self.add_suite_with_first_run()

        self.suite.open_page(suites)
        self.suite.open_suite(name)
        self.suite.add_case(self.p.add.case_name)
        self.suite.add_column(column_type)
        self.suite.assert_column_exists(column_type)

        self.suite.delete_column(column_type)

    @pytest.mark.testrail(id=192)
    def test_c192_grid_edit_column_selection(self):
        name = self.p.suites.edit.name
        column_type = self.p.suites.add_column_type
        column_type2 = self.p.suites.second_add_column_type

        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        self.suite_id = self.add_suite_with_first_run()

        self.suite.open_page(suites)
        self.suite.open_suite(name)
        self.suite.add_case(self.p.add.case_name)
        self.suite.add_column(column_type)
        self.suite.add_column(column_type2)

        self.suite.edit_column(column_type2)
        self.suite.assert_column_position_and_width(column_type2, position=4, width=200)

        self.suite.delete_column(column_type)
        self.suite.delete_column(column_type2)

    @pytest.mark.testrail(id=193)
    def test_c193_grid_delete_column(self):
        name = self.p.suites.edit.name
        column_type = self.p.suites.add_column_type
        suites = self.data.server_name + self.p.suites.overview_url + self.project_id
        self.suite_id = self.add_suite_with_first_run()

        self.suite.open_page(suites)
        self.suite.open_suite(name)
        self.suite.add_case(self.p.add.case_name)

        self.suite.add_column(column_type)
        self.suite.delete_column(column_type)
        self.suite.assert_column_absent(column_type)


if __name__ == "__main__":
    pytest.main()
