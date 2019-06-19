import pytest
from src.common import decode_data, read_config
import src.pages.project.suite_page as suite_page
import src.pages.administration.project_page as project_page
import src.pages.administration.integration_page as integration_page
from src.test_cases.base_test import BaseTest


class TestPlugins(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        # Get test data
        cls.p = read_config('../config/project.json')
        cls.youtrack = read_config("../config/plugin.json")

        # Prepare page objects
        cls.suite = suite_page.SuitePage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)
        cls.integration = integration_page.IntegrationPage(cls.driver)

        # Perquisites for tests executions
        cls.prepare_for_testing(cls)

    def setup_method(self):
        self.suite.open_page(self.data.server_name)

    def teardown_method(self):
        self.delete_prepared_data()

    def prepare_for_testing(self):
        add_project_url = (self.data.server_name + self.p.add_project_url)

        self.suite.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.project.open_page(add_project_url)
        self.project_id = self.project.add_single_repo_project(self.p.project_info.project_name)

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project

        self.project.open_page(projects_overview_url)
        self.project.delete_project(self.p.project_info.project_name)
        self.project.validate_success_message(message)
        self.integration.open_page(self.data.server_name + self.youtrack.integration_url)
        self.integration.clear_integration_settings()

    @pytest.mark.testrail(id=5259)
    @pytest.mark.run(order=1)
    def test_add_youtrack_integration_success(self):
        yt = decode_data(str(self.youtrack.youtrack))
        yt.user_variable_username = decode_data(str(self.youtrack.youtrack.user_variable_username))
        yt.user_variable_password = decode_data(str(self.youtrack.youtrack.user_variable_password))
        message = self.youtrack.messages.success_updated_integration_settings
        self.integration.open_page(self.data.server_name + self.youtrack.integration_url)
        self.integration.add_defects_data(yt)
        self.integration.add_user_variable(yt.user_variable_username)
        self.integration.add_user_variable(yt.user_variable_password)
        self.integration.save_settings()
        self.integration.check_success_message(message)

    @pytest.mark.testrail(id=5255)
    @pytest.mark.skip(reason="Design")
    def test_push_issue_to_youtrack_success(self):
        print ("to do")

    @pytest.mark.skip(reason="Design")
    def test_quick_view_issue_to_youtrack_success(self):
        print ("to do")

    @pytest.mark.testrail(id=5257)
    @pytest.mark.skip(reason="Design")
    def test_view_issue_on_youtrack_success(self):
        print ("to do")


if __name__ == "__main__":
    pytest.main()
