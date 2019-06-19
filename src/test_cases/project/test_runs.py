import pytest
from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config, merge_configs
from src.models.administration.user import User
import src.pages.project.suite_page as suite_page
import src.pages.login_page as login_page
import src.pages.administration.project_page as project_page
import src.pages.project.testcases_page as test_cases_page
import src.pages.project.sections_page as section_page
import src.pages.project.plans_page as plans_page
import src.pages.project.runs_page as runs_page
import src.pages.project.cases_page as cases_page
from src.pages.project import milestones_page
from src.pages.project import results_page
from src.pages.project import testcases_page
from src.pages.administration.users_roles_page import UsersRolesPage
from src.helpers.prepare_data import PrepareData
from src.helpers.driver_manager import DriverType, DriverManager

@pytest.mark.skip(reason="Everest - not working!")
class TestRunsSkipped:

    @classmethod
    def setup_class(cls):
        # Get test data
        cls.data = merge_configs('~/testrail.json', '../config/data.json')
        cls.p = read_config('../config/project.json')
        cls.runs = read_config('../config/runs.json')
        cls.users = read_config('../config/users.json')
        cls.t = read_config('../config/tests.json')
        cls.plans = read_config('../config/plans.json')

        # Prepare browser
        cls.driver = DriverManager.get_driver(DriverType.FIREFOX)

        cls.driver.maximize_window()
        cls.driver.get(cls.data.server_name)
        cls.driver.implicitly_wait(10)

        # Prepare page objects
        cls.suite = suite_page.SuitePage(cls.driver)
        cls.login = login_page.LoginPage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.tests = test_cases_page.TestCasesPage(cls.driver)
        cls.section = section_page.SectionsPage(cls.driver)
        cls.plan = plans_page.PlansPage(cls.driver)
        cls.run = runs_page.RunsPage(cls.driver)
        cls.cases = cases_page.CasesPage(cls.driver)
        cls.prepare_data = PrepareData(cls.driver)
        cls.users_overview_url = cls.data.server_name + cls.users.overview_url

        # Perquisites for tests execution
        cls.prepare_for_testing(cls)

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data(cls)
        cls.driver.delete_all_cookies()
        cls.driver.quit()

    def setup_method(self):
        self.suite.open_page(self.data.server_name)

    def teardown_method(self):
        self.suite.open_page(self.data.server_name)

    def prepare_for_testing(self):
        self.suite.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)
        self.prepare_data.delete_existing_users(self.users_overview_url, self.users.messages.msg_success_updated_user)
        self.users_to_add = self.prepare_data.add_multiple_users(self.users.add, self.data.server_name + self.users.add_multiple_users_url, self.users.messages.msg_success_added_all_users)
        self.project_id = self.prepare_data.add_single_repo_project(self.data.server_name + self.p.add_project_url, self.p.project_info.project_name)
        self.suite_id = self.prepare_data.add_section_with_test_cases_inline(self.data.server_name + self.p.project_overview_url + self.project_id, 30)
        self.run_id = self.prepare_data.add_run_outside_plan(self.data.server_name + self.runs.overview_url + self.project_id, self.runs.run, self.runs.messages.msg_success_added_test_run)
        self.plan_id, self.plan_run_id = self.prepare_data.add_plan_with_run(self.data.server_name + self.runs.overview_url + self.project_id, self.plans.add_plan, self.plans.messages.msg_success_added_plan)

    def delete_prepared_data(self):
        projects_overview_url = (self.data.server_name + self.p.overview_url)
        message = self.p.messages.msg_success_deleted_project
        self.project.open_page(projects_overview_url)
        self.project.delete_project(self.p.project_info.project_name)
        self.project.validate_success_message(message)
        self.users_roles.open_page(self.users_overview_url)
        self.users_roles.forget_all_added_users(self.users.messages.msg_success_updated_user)

    @pytest.mark.run(order=1)
    def test_edit_run_no_changes(self):
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        self.run.edit_assignee_and_save_run(None)
        self.suite.validate_success_message(self.runs.messages.msg_success_edited_test_run)
        self.run.validate_run_assignee("")

    @pytest.mark.run(order=2)
    def test_edit_run_add_assignee_random_user(self):
        assignee_name = self.users.add[2].full_name

        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        self.run.edit_assignee_and_save_run(assignee_name)
        self.suite.validate_success_message(self.runs.messages.msg_success_edited_test_run)
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        self.run.validate_run_assignee(assignee_name)
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.cases.validate_all_tests_assignee(assignee_name)

    @pytest.mark.run(order=3)
    def test_edit_run_add_assignee_me(self):
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        assignee_name = "Me"
        self.run.edit_assignee_and_save_run(assignee_name)
        self.suite.validate_success_message(self.runs.messages.msg_success_edited_test_run)
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        self.run.validate_run_assignee(self.data.login.full_name)
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.cases.validate_all_tests_assignee(self.data.login.full_name)

    @pytest.mark.run(order=4)
    def test_edit_run_different_asignees_set_on_cases_add_general_assignee(self):
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.cases.add_assignee_to_cases(self.users_to_add[0:3])
        self.cases.validate_assignees_to_cases(self.users_to_add[0:3])
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        assignee_name = self.users.add[3].full_name
        self.run.edit_assignee_and_save_run(assignee_name)
        self.suite.validate_success_message(self.runs.messages.msg_success_edited_test_run)
        self.suite.open_page(self.data.server_name + self.runs.edit_url + self.run_id)
        self.run.validate_run_assignee(assignee_name)
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.cases.validate_all_tests_assignee(assignee_name)

    @pytest.mark.run(order=5)
    def test_edit_run_general_asignee_set_add_different_assignees_to_cases(self):
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.run_id)
        self.cases.add_assignee_to_cases(self.users_to_add[0:3])
        self.cases.validate_assignees_to_cases(self.users_to_add[0:3])

    @pytest.mark.run(order=6)
    def test_add_different_assignees_to_run_in_plan(self):
        for user in self.users_to_add[0:3]:
            self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
            self.plan.add_assignee_to_run_in_plan(user)
            self.driver.implicitly_wait(3)
            self.suite.validate_success_message(self.plans.messages.msg_success_edited_plan)
            self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
            self.plan.validate_run_assignee_in_plan(user)

    @pytest.mark.run(order=7)
    def test_select_cases_for_run_in_plan(self):
        user = self.users_to_add[3]
        self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
        self.plan.add_assignee_and_cases_to_run_in_plan(user, 2)
        self.driver.implicitly_wait(3)
        self.suite.validate_success_message(self.plans.messages.msg_success_edited_plan)
        self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
        self.plan.validate_run_assignee_in_plan(user)
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.plan_run_id)
        self.cases.validate_cases_for_run(user, 2)

    @pytest.mark.run(order=8, depends="test_select_testcases_for_run_in_plan")
    def test_select_all_cases_for_run_in_plan(self):
        user = self.users_to_add[2]
        self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
        self.plan.add_assignee_and_include_all_cases_for_run_in_plan(user)
        self.driver.implicitly_wait(3)
        self.suite.validate_success_message(self.plans.messages.msg_success_edited_plan)
        self.suite.open_page(self.data.server_name + self.plans.edit_url + self.plan_id)
        self.plan.validate_run_assignee_in_plan(user)
        self.suite.open_page(self.data.server_name + self.runs.run_view_url + self.plan_run_id)
        self.cases.validate_cases_for_run(user, 3)


class TestRuns(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.r = read_config('../config/runs.json')
        cls.runs = runs_page.RunsPage(cls.driver)

        cls.p = read_config('../config/project.json')
        cls.project = project_page.ProjectPage(cls.driver)

        cls.t = read_config('../config/tests.json')
        cls.tests = testcases_page.TestCasesPage(cls.driver)

        cls.u = read_config('../config/users.json')
        cls.users = UsersRolesPage(cls.driver)

        cls.m = read_config("../config/milestones.json")
        cls.miles = milestones_page.MilestonesPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.runs.open_page(self.data.server_name)

    def teardown_method(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        edit_run_url = self.data.server_name + self.r.edit_url
        self.runs.open_page(runs_overview_url)
        all_runs = self.runs.all_run_ids()
        for run in all_runs:
            self.runs.open_page(edit_run_url + run)
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

        add_milestone_url = cls.data.server_name + cls.m.add_milestone_url.format(cls.project_id)
        milestone_message = cls.m.messages.msg_success_added_milestone
        milestone = cls.m.milestones[0]

        cls.miles.open_page(add_milestone_url)
        cls.miles.add_milestone(milestone.name, milestone.description)
        cls.miles.confirm_milestone(milestone_message)

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

    @pytest.mark.testrail(id=260)
    def test_c260_add_first_run(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        message = self.r.messages.msg_success_added_test_run

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(message)
        self.runs.verify_run(run.name, run.description)

        self.runs.open_page(runs_overview_url)
        self.runs.verify_run_link(run.name)

    @pytest.mark.testrail(id=261)
    def test_c261_add_subsequent_runs(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        message = self.r.messages.msg_success_added_test_run

        for run in self.r.runs:
            self.runs.open_page(runs_overview_url)
            self.runs.click_add_test_run()
            self.runs.add_data_to_run(run.name, run.description)
            self.runs.validate_success_message(message)
            self.runs.verify_run(run.name, run.description)

        self.runs.open_page(runs_overview_url)
        for run in self.r.runs:
            self.runs.verify_run_link(run.name)

    @pytest.mark.testrail(id=262)
    def test_c262_link_runs_to_milestone(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run_message = self.r.messages.msg_success_added_test_run
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        milestone = self.m.milestones[0]
        run = self.r.runs[0]

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.select_milestone(milestone.name)
        run_id = self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(run_message)
        run_url = self.data.server_name + self.r.run_view_url + run_id

        self.runs.open_page(milestone_overview_url)
        self.runs.assert_run_in_milestone(milestone.name, run.name, run_url)

    @pytest.mark.testrail(id=263)
    def test_c263_assign_to_own_user_account(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run_message = self.r.messages.msg_success_added_test_run
        run = self.r.runs[0]

        self.runs.open_page(runs_overview_url)

        self.runs.click_add_test_run()
        self.runs.assign_to("Me")
        run_id = self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(run_message)

        edit_run_url = self.data.server_name + self.r.edit_url + run_id
        self.runs.open_page(edit_run_url)
        self.runs.validate_run_assignee(self.data.login.full_name)

    @pytest.mark.testrail(id=264)
    def test_c264_assign_to_different_user_account(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run_message = self.r.messages.msg_success_added_test_run
        run = self.r.runs[0]
        full_name = self.r.add.user_full_name

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.assign_to(full_name)
        run_id = self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(run_message)

        edit_run_url = self.data.server_name + self.r.edit_url + run_id
        self.runs.open_page(edit_run_url)
        self.runs.validate_run_assignee(full_name)

    @pytest.mark.testrail(id=265)
    def test_c265_run_with_all_cases(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        message = self.r.messages.msg_success_added_test_run

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        run_id = self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(message)

        run_url = self.data.server_name + self.r.run_view_url + run_id
        self.runs.open_page(run_url)
        case_names = [case.title  for case in self.cases]
        self.runs.assert_cases_in_run(case_names)

    @pytest.mark.testrail(id=266)
    def test_c266_run_with_selected_cases(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        message = self.r.messages.msg_success_added_test_run
        case1 = self.cases[0]
        case2 = self.cases[2]

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.select_cases(case1.title, case2.title)
        run_id = self.runs.add_data_to_run(run.name, run.description)
        self.runs.validate_success_message(message)

        run_url = self.data.server_name + self.r.run_view_url + run_id
        self.runs.open_page(run_url)
        case_names = [case1.title, case2.title]
        self.runs.assert_cases_in_run(case_names)

    @pytest.mark.testrail(id=2177)
    def test_c2177_edit_test_run(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        original_run = self.r.runs[0]
        edited_run = self.r.runs[1]
        add_message = self.r.messages.msg_success_added_test_run
        edit_message = self.r.messages.msg_success_edited_test_run
        case1 = self.cases[0]
        case2 = self.cases[2]
        milestone_overview_url = self.data.server_name +  self.m.milestones_overview_url.format(self.project_id)
        milestone = self.m.milestones[0]

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        run_id = self.runs.add_data_to_run(original_run.name, original_run.description)
        self.runs.validate_success_message(add_message)
        view_run_url = self.data.server_name + self.r.run_view_url + run_id
        edit_run_url = self.data.server_name + self.r.edit_url + run_id

        self.runs.open_page(edit_run_url)
        self.runs.edit_run(edited_run)
        self.runs.select_cases(case1.title, case2.title)
        self.runs.confirm_edit_run(edit_message)

        self.runs.open_page(view_run_url)
        self.runs.verify_run(edited_run.name, edited_run.description)
        self.runs.assert_cases_in_run([case1.title, case2.title])

        self.runs.open_page(milestone_overview_url)
        self.runs.assert_run_in_milestone(milestone.name, edited_run.name, view_run_url)

        self.runs.open_page(edit_run_url)
        self.runs.validate_run_assignee(edited_run.assigned_to)

    @pytest.mark.testrail(id=2178)
    def test_c2178_rerun_test_run(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        message = self.r.messages.msg_success_added_test_run
        case1 = self.cases[0]
        case2 = self.cases[2]

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.select_cases(case1.title, case2.title)
        self.runs.add_data_to_run(run.name, run.description)

        self.runs.rerun_run(message)
        self.runs.verify_run(run.name, run.description)
        self.runs.assert_cases_in_run([case1.title, case2.title])

    @pytest.mark.testrail(id=270)
    def test_c270_close_run(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        closed_message = self.r.messages.msg_success_closed_test_run
        not_allowed_message = self.r.messages.msg_edit_not_allowed
        run = self.r.runs[0]

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        run_id = self.runs.add_data_to_run(run.name, run.description)

        view_run_url = self.data.server_name + self.r.run_view_url + run_id
        edit_run_url = self.data.server_name + self.r.edit_url + run_id
        self.runs.open_page(edit_run_url)
        self.runs.close_run()
        self.runs.validate_success_message(closed_message)

        self.runs.open_page(edit_run_url)
        self.runs.check_page(view_run_url)
        self.runs.validate_error_message(not_allowed_message)
        self.runs.assert_no_edit_link()

    @pytest.mark.testrail(id=274)
    def test_c274_delete_test_run(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        deleted_message = self.r.messages.msg_success_deleted_test_run

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        run_id = self.runs.add_data_to_run(run.name, run.description)

        view_run_url = self.data.server_name + self.r.run_view_url + run_id
        edit_run_url = self.data.server_name + self.r.edit_url + run_id
        self.runs.open_page(edit_run_url)
        self.runs.delete_run()
        self.runs.validate_success_message(deleted_message)

        self.runs.open_page(runs_overview_url)
        self.runs.assert_run_deleted(run_id)

    @pytest.mark.testrail(id=290)
    def test_c290_grid_add_column(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        column_type = self.r.add.add_column_type

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.add_data_to_run(run.name, run.description)

        self.runs.add_column(column_type)
        self.runs.assert_column_exists(column_type)

        self.runs.delete_column(column_type)

    @pytest.mark.testrail(id=292)
    def test_c292_grid_edit_column_selection(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        column_type = self.r.add.add_column_type
        column_type2 = self.r.add.second_add_column_type

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.add_data_to_run(run.name, run.description)

        self.runs.add_column(column_type)
        self.runs.add_column(column_type2)

        self.runs.edit_column(column_type2)
        self.runs.assert_column_position_and_width(column_type2, position=3, width=200)

        self.runs.delete_column(column_type)
        self.runs.delete_column(column_type2)

    @pytest.mark.testrail(id=293)
    def test_c293_grid_delete_column(self):
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        column_type = self.r.add.add_column_type

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.add_data_to_run(run.name, run.description)

        self.runs.add_column(column_type)
        self.runs.delete_column(column_type)
        self.runs.assert_column_absent(column_type)

    @pytest.mark.testrail(id=287)
    def test_c287_rerun_with_status_selection(self):
        results = results_page.ResultsPage(self.driver)
        result_data = read_config('../config/results.json')
        runs_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        run = self.r.runs[0]
        passed, failed, retest = result_data.statuses[:3]
        case1, case2, case3 = self.cases
        message = self.r.messages.msg_success_added_test_run

        self.runs.open_page(runs_overview_url)
        self.runs.click_add_test_run()
        self.runs.add_data_to_run(run.name, run.description)

        results.expand_case(case1.title)
        results.add_result_with_status(passed)
        results.expand_case(case2.title)
        results.add_result_with_status(failed)
        results.expand_case(case3.title)
        results.add_result_with_status(retest)

        self.runs.rerun_run(message, statuses=(failed, retest))
        self.runs.verify_run(run.name, run.description)
        self.runs.assert_cases_in_run([case2.title, case3.title])


if __name__ == "__main__":
    pytest.main()

