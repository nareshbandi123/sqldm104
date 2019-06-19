import pytest
from src.test_cases.base_test import BaseTest
from src.common import read_config
from src.pages.administration import project_page
from src.pages.project import milestones_page
from src.pages.project import runs_page
from src.pages.project import suite_page


class TestMilestones(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.m = read_config('../config/milestones.json')
        cls.p = read_config('../config/project.json')
        cls.r = read_config('../config/runs.json')

        cls.project = project_page.ProjectPage(cls.driver)
        cls.miles = milestones_page.MilestonesPage(cls.driver)
        cls.runs = runs_page.RunsPage(cls.driver)
        cls.suite = suite_page.SuitePage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.miles.open_page(self.data.server_name)

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.miles.open_page(cls.data.server_name)
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

    @pytest.mark.testrail(id=247)
    @pytest.mark.dependency(name="test_add_milestone")
    def test_add_milestone(self):
        add_milestone_url = self.data.server_name +  self.m.add_milestone_url.format(self.project_id)
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        milestone = self.m.milestones[0]
        message = self.m.messages.msg_success_added_milestone
        self.miles.open_page(add_milestone_url)
        self.miles.add_milestone(milestone.name, milestone.description)
        self.miles.confirm_milestone(message)
        self.miles.check_page(milestone_overview_url)
        self.miles.validate_milestone(milestone.name, milestone.description)

    @pytest.mark.testrail(id=248)
    @pytest.mark.dependency(name="test_add_subsequent_milestones", depends=["test_add_milestone"])
    def test_add_subsequent_milestones(self):
        add_milestone_url = self.data.server_name +  self.m.add_milestone_url.format(self.project_id)
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        project_overview_url = (self.data.server_name + self.p.project_overview_url + self.project_id)
        message = self.m.messages.msg_success_added_milestone

        milestones = self.m.milestones[1:]
        self.miles.add_multiple_milestones(milestones, add_milestone_url, milestone_overview_url, message)

        self.miles.open_page(milestone_overview_url)
        names = [milestone.name for milestone in self.m.milestones]
        links = self.miles.get_milestone_links(names)

        self.miles.open_page(project_overview_url)
        self.miles.verify_milestone_links_exist(names, links)

    @pytest.mark.testrail(id=249)
    def test_milestone_calendar(self):
        add_milestone_url = self.data.server_name +  self.m.add_milestone_url.format(self.project_id)
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        message = self.m.messages.msg_success_added_milestone
        milestone = self.m.milestone_with_calendar

        self.miles.open_page(add_milestone_url)
        self.miles.add_milestone(milestone.name, milestone.description)
        start_date_string = self.miles.select_start_date()
        due_date_string = self.miles.select_end_date()
        self.miles.confirm_milestone(message)
        self.miles.check_page(milestone_overview_url)

        self.miles.confirm_start_date(milestone.name, start_date_string)
        self.miles.confirm_due_date(milestone.name, due_date_string)

    @pytest.mark.testrail(id=254)
    @pytest.mark.dependency(depends=["test_add_subsequent_milestones"])
    def test_delete_milestone_no_linked_runs(self):
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        milestone = self.m.milestones[-2]
        message = self.m.messages.msg_success_deleted_milestone

        self.miles.open_page(milestone_overview_url)
        self.miles.delete_milestone(milestone.name, message)

    @pytest.mark.testrail(id=253)
    @pytest.mark.dependency(name="test_link_milestone_to_run", depends=["test_add_milestone"])
    def test_link_milestone_to_run(self):
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        add_suite_url = self.data.server_name + self.p.suites.add_url + self.project_id
        run_name = self.r.runs[0].name
        run_description = self.r.runs[0].description
        suite_name = self.p.suites.add[1].name
        suite_description = self.p.suites.add[1].description
        milestone_name = self.m.milestones[0].name

        self.suite.open_page(add_suite_url)
        self.suite.add_data_to_suite(suite_name, suite_description)

        self.miles.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.confirm_suite()
        self.runs.add_data_to_run_with_milestone(run_name, run_description, milestone_name)

        self.miles.open_page(milestone_overview_url)
        self.miles.verify_milestone_has_active_run(milestone_name)

    @pytest.mark.testrail(id=255)
    @pytest.mark.dependency(depends=["test_link_milestone_to_run"])
    def test_delete_milestone_with_linked_run(self):
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        milestone = self.m.milestones[0]
        message = self.m.messages.msg_success_deleted_milestone

        self.miles.open_page(milestone_overview_url)
        self.miles.delete_milestone(milestone.name, message)
