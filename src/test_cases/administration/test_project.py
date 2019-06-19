import pytest
from src.common import read_config
import src.pages.administration.project_page as project
from src.test_cases.base_test import BaseTest

class TestProject(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.project = read_config('../config/project.json')
        cls.project_page = project.ProjectPage(cls.driver)

        cls.prepare_for_testing(cls)
        # Removing existing projects if any to avoid mismatch of project status counts on dashboard.
        cls.delete_prepared_data(cls)

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data(cls)
        super().teardown_class()

    @pytest.mark.dependency(name="test_add_project_first_single_repo_success")
    @pytest.mark.run(order=1)
    def test_add_project_first_single_repo_success(self):
        add_project_url = (self.data.server_name + self.project.add_project_url)
        project_name = self.project.add.single_suite_name
        first_project_message = self.project.messages.msg_success_created_first_project

        self.project_page.open_page(add_project_url)
        self.project_page.add_single_repo_project(project_name)
        self.project_page.validate_first_project(first_project_message, project_name)

    @pytest.mark.run(order=2)
    def test_add_project_baseline_repo_success(self):
        add_project_url = (self.data.server_name + self.project.add_project_url)
        project_name = self.project.add.baseline_suite_name
        success_message =self.project.messages.msg_successfully_added_project

        self.project_page.open_page(add_project_url)
        self.project_page.add_baseline_repo_project(project_name)
        self.project_page.validate(success_message, project_name)

    @pytest.mark.run(order=3)
    def test_add_project_multi_repo_success(self):
        add_project_url = (self.data.server_name + self.project.add_project_url)
        project_name = self.project.add.multi_suite_name
        success_message = self.project.messages.msg_successfully_added_project

        self.project_page.open_page(add_project_url)
        self.project_page.add_multi_repo_project(project_name)
        self.project_page.validate(success_message, project_name)

    @pytest.mark.dependency(depends=["test_add_project_first_single_repo_success"])
    @pytest.mark.dependency(name="test_add_announcement_to_existing_project_success")
    @pytest.mark.run(order=4)
    def test_add_announcement_to_existing_project_success(self):
        projects_overview_url = (self.data.server_name + self.project.overview_url)

        self.project_page.open_page(projects_overview_url)
        self.project_page.open_project_for_editing(self.project.add.single_suite_name)
        self.project_page.edit_project_announcement(self.project.add.announcement)
        self.project_page.validate(self.project.messages.msg_successfully_edited_project, self.project.add.single_suite_name)

    @pytest.mark.dependency(depends=["test_add_announcement_to_existing_project_success"])
    @pytest.mark.run(order=5)
    def test_show_announcement_on_project_overview_success(self):
        projects_overview_url = (self.data.server_name + self.project.overview_url)

        self.project_page.open_page(projects_overview_url)
        self.project_page.open_project_for_editing(self.project.add.single_suite_name)
        self.project_page.enable_showing_announcement_in_overview()
        self.project_page.validate(self.project.messages.msg_successfully_edited_project, self.project.add.single_suite_name)
        project_id = self.project_page.get_project_id(self.project.add.single_suite_name)
        self.project_page.open_page(self.data.server_name + self.project.project_overview_url + project_id)
        self.project_page.validate_announcement_shown_in_overview(self.project.add.announcement)


    @pytest.mark.dependency(depends=["test_add_project_first_single_repo_success"])
    @pytest.mark.run(order=6)
    def test_edit_project_name_success(self):
        projects_overview_url = (self.data.server_name + self.project.overview_url)
        project_name = self.project.add.single_suite_name
        project_name_edited = self.project.add.edited_project_name
        success_message = self.project.messages.msg_successfully_edited_project

        self.project_page.open_page(projects_overview_url)
        self.project_page.open_project_for_editing(project_name)
        self.project_page.edit_project_name(project_name_edited)
        self.project_page.validate(success_message, project_name_edited)

    def prepare_for_testing(self):
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.project.overview_url)
        self.project_page.open_page(projects_overview_url)
        self.project_page.delete_existing_projects()

if __name__ == "__main__":
    pytest.main()