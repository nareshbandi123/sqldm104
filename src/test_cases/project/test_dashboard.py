import pytest
from src.test_cases.base_test import BaseTest
from src.common import read_config
import src.pages.project.sections_page as section_page
import src.pages.administration.project_page as project_page


class TestDashboard(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.p = read_config('../config/project.json')
        cls.setup_database(cls.p)

        cls.section = section_page.SectionsPage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing(cls)
        # Removing existing projects if any to avoid mismatch of project status counts on dashboard.
        cls.delete_prepared_data(cls)

    def prepare_for_testing(self):
        self.section.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        self.teardown_database()
        self.project.open_page(projects_overview_url)
        # self.project.delete_existing_projects()

    def test_project_0_active_0_completed(self):
        active = completed = 0
        self.section.open_page(self.data.server_name + self.data.dashboard_url)
        self.project.active_completed_count_check(completed, active)

    @pytest.mark.parametrize("completed, active", [(1, 2),(25, 10),(26, 51)])
    def test_project_active_completed_count(self, completed, active):
        try:
            add_project_url = (self.data.server_name + self.p.add_project_url)

            self.project.create_projects(completed, active, add_project_url)
            self.project.make_projects_completed(completed)
            self.section.open_page(self.data.server_name + self.data.dashboard_url)
            self.project.active_completed_count_check(completed,active)
        finally:
            self.delete_prepared_data()

if __name__ == "__main__":
    pytest.main()
