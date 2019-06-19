import pytest
from src.test_cases.base_test import BaseTest
from src.common import decode_data, read_config
from src.models.administration.user import User
from src.pages.administration import project_page
from src.pages.administration import users_roles_page
from src.pages.project import milestones_page
from src.pages.project import plans_page
from src.pages.project import testcases_page


class TestPlans(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.p = read_config('../config/project.json')
        cls.r = read_config('../config/runs.json')
        cls.plan_data = read_config('../config/plans.json')
        cls.t = read_config('../config/tests.json')
        cls.u = read_config('../config/users.json')

        cls.project = project_page.ProjectPage(cls.driver)
        cls.plans = plans_page.PlansPage(cls.driver)
        cls.tests = testcases_page.TestCasesPage(cls.driver)
        cls.users = users_roles_page.UsersRolesPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.plans.open_page(self.data.server_name)

    def teardown_method(self):
        self.plans.open_page(self.data.server_name + self.r.overview_url + self.project_id)
        self.plans.delete_plans(self.plan_data.messages.msg_success_deleted_plan)

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.plans.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        cls.project_id = cls.project.add_single_repo_project(cls.p.project_info.project_name)

        case1 = decode_data(str(cls.t.cases[0]))
        case2 = decode_data(str(cls.t.cases[1]))
        case3 = decode_data(str(cls.t.cases[2]))

        cls.plans.open_page(cls.data.server_name + cls.r.overview_url + cls.project_id)
        cls.tests.add_tests(case1, case2, case3)
        cls.cases = [case1, case2, case3]

        full_name = cls.plan_data.add.user_full_name
        email_address = cls.plan_data.add.user_email_address
        password = cls.plan_data.add.user_password
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

        cls.users.open_page(cls.data.server_name + cls.u.overview_url)
        cls.users.forget_user(cls.plan_data.add.user_full_name)

    @pytest.mark.testrail(id=335)
    def test_add_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan

        self.plans.open_page(add_plan_url)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, message)
        plan_overview_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.check_page(plan_overview_url)
        self.plans.validate_plan(plan.name, plan.description)

    @pytest.mark.testrail(id=336)
    def test_add_subsequent_plans(self):
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan

        plans = self.plan_data.plans
        self.plans.add_multiple_plans(add_plan_url, plans, message)
        self.plans.assert_available_plans(plans)

    @pytest.mark.testrail(id=341)
    def test_link_milestone_to_plan(self):
        milestone_data = read_config("../config/milestones.json")
        miles = milestones_page.MilestonesPage(self.driver)

        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        plan_message = self.plan_data.messages.msg_success_added_plan

        add_milestone_url = self.data.server_name +  milestone_data.add_milestone_url.format(self.project_id)
        milestone_overview_url = self.data.server_name +  milestone_data.milestones_overview_url.format(self.project_id)
        milestone = milestone_data.milestones[0]
        milestone_message = milestone_data.messages.msg_success_added_milestone

        miles.open_page(add_milestone_url)
        miles.add_milestone(milestone.name, milestone.description)
        miles.confirm_milestone(milestone_message)

        self.plans.open_page(add_plan_url)
        self.plans.select_milestone(milestone.name)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, plan_message)
        plan_overview_url = self.data.server_name + self.plan_data.view_url + plan_id

        self.plans.open_page(milestone_overview_url)
        self.plans.assert_plan_in_milestone(milestone.name, plan.name, plan_overview_url)

    @pytest.mark.testrail(id=2176)
    def test_c2176_delete_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        plans_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        delete_message = self.plan_data.messages.msg_success_deleted_plan

        self.plans.open_page(add_plan_url)
        self.plans.add_data_to_plan(plan.name, plan.description, add_message)
        self.plans.open_page(plans_overview_url)
        self.plans.delete_plan(plan.name, delete_message)
        self.plans.assert_available_plans([])

    @pytest.mark.testrail(id=342)
    def test_c342_select_cases(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan

        case1, case2 = self.cases[:2]

        self.plans.open_page(add_plan_url)
        self.plans.select_cases(case1.title, case2.title)
        _, run_id = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)
        self.plans.open_page(run_url.format(run_id))
        self.plans.assert_cases_in_run(case1.title, case2.title)

    @pytest.mark.testrail(id=1170)
    def test_c1170_runs_with_different_assignees_adding_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan

        first_user = self.data.login.full_name
        second_user = self.plan_data.add.user_full_name

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        self.plans.add_assignee_to_run_in_plan(first_user, 1, confirm_plan=False)
        self.plans.add_assignee_to_run_in_plan(second_user, 2, confirm_plan=False)
        self.plans.validate_run_assignee_in_plan(first_user, 1)
        self.plans.validate_run_assignee_in_plan(second_user, 2)
        self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

    @pytest.mark.testrail(id=1175)
    def test_c1175_runs_with_different_assignees_editing_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan

        first_user = self.data.login.full_name
        second_user = self.plan_data.add.user_full_name

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.add_assignee_to_run_in_plan(first_user, 1, confirm_plan=False)
        self.plans.add_assignee_to_run_in_plan(second_user, 2, confirm_plan=False)
        self.plans.validate_run_assignee_in_plan(first_user, 1)
        self.plans.validate_run_assignee_in_plan(second_user, 2)
        self.plans.confirm_edit_plan(edit_message)

    @pytest.mark.testrail(id=337)
    def test_c337_load_rerun_existing_plan(self):
        plan1 = self.plan_data.plans[0]
        plan2 = self.plan_data.plans[1]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan
        case1 = self.cases[0]
        case2 = self.cases[2]

        self.plans.open_page(add_plan_url)
        self.plans.select_cases(case1.title, case2.title)
        plan_id, _ = self.plans.add_data_to_plan(plan1.name, plan1.description, add_message, add_runs=False)
        _, run_id = self.plans.rerun_plan_with_new_name(plan2.name, add_message)
        self.plans.validate_plan(plan2.name)

        self.plans.open_page(run_url.format(run_id))
        self.plans.assert_cases_in_run(case1.title, case2.title)

    @pytest.mark.testrail(id=1172)
    def test_c1172_separate_runs_separate_cases_adding_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan

        case1, case2 = self.cases[:2]
        case3 = self.cases[2]

        self.plans.open_page(add_plan_url)
        self.plans.select_cases(case1.title, case2.title)
        self.plans.select_cases(case1.title, case3.title, run_number=2)
        self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()
        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_cases_in_run(case1.title, case2.title)
        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_cases_in_run(case1.title, case3.title)

    @pytest.mark.testrail(id=1174)
    def test_c1174_separate_runs_separate_cases_editing_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan

        case1, case2 = self.cases[:2]
        case3 = self.cases[2]

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.select_cases(case1.title, case2.title, add_run=False)
        self.plans.select_cases(case1.title, case3.title, run_number=2, add_run=False)
        self.plans.confirm_edit_plan(edit_message)

        self.plans.open_page(view_plan_url)
        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()
        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_cases_in_run(case1.title, case2.title)
        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_cases_in_run(case1.title, case3.title)

    @pytest.mark.testrail(id=2172)
    def test_c2172_add_runs_to_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan
        run_names = self.plan_data.add.run_names

        self.plans.open_page(add_plan_url)
        for run_name in run_names:
            self.plans.add_run_with_name(run_name)
        self.plans.add_data_to_plan(plan.name, plan.description, message, add_runs=False)
        self.plans.verify_run_names(run_names)

    @pytest.mark.testrail(id=2173)
    @pytest.mark.dependency(name="test_c2173_add_configurations")
    def test_c2173_add_configurations(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan
        configuration_group = self.plan_data.add.configuration_group
        configuration_options = self.plan_data.add.configuration_options
        selected_options = self.plan_data.add.configuration_selected_options

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(1)
        self.plans.add_configuration(configuration_group, configuration_options)
        self.plans.select_configuration_options(selected_options)
        self.plans.assert_selected_configuration_options(selected_options)
        self.plans.add_data_to_plan(plan.name, plan.description, message, add_runs=False)
        self.plans.assert_runs_match_configurations(selected_options)

    @pytest.mark.testrail(id=1171)
    def test_c1171_descriptions_changes_adding_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan
        description_1 = self.plan_data.add.run_description_1
        description_2 = self.plan_data.add.run_description_2

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        self.plans.add_run_description(description_1, run_number=1)
        self.plans.add_run_description(description_2, run_number=2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.check_page(view_plan_url)

        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()
        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_run_description(description_1)
        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_run_description(description_2)

    @pytest.mark.testrail(id=1173)
    def test_c1173_descriptions_changes_editing_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        run_url = self.data.server_name + self.plan_data.run_view_url
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan
        description_1 = self.plan_data.add.run_description_1
        description_2 = self.plan_data.add.run_description_2

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        self.plans.check_page(view_plan_url)

        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()

        self.plans.open_page(edit_plan_url)
        self.plans.add_run_description(description_1, run_number=1)
        self.plans.add_run_description(description_2, run_number=2)
        self.plans.confirm_edit_plan(edit_message)

        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_run_description(description_1)
        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_run_description(description_2)

    @pytest.mark.testrail(id=344)
    def test_c344_plan_runs_cannot_be_edited(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan

        self.plans.open_page(add_plan_url)
        _, run_id = self.plans.add_data_to_plan(plan.name, plan.description, message)
        run_view_url = self.data.server_name + self.plan_data.run_view_url.format(run_id)
        run_edit_url = self.data.server_name + self.plan_data.run_edit_url.format(run_id)
        self.plans.open_page(run_edit_url)
        # This should redirect to the view url
        self.plans.check_page(run_view_url)
        self.plans.assert_no_edit_link()

    @pytest.mark.testrail(id=355)
    def test_c345_plan_runs_cannot_be_closed(self):
        # Note that plans can only be deleted through the edit page, and we've
        # already confirmed that child runs of plans cannot be edited.
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan

        self.plans.open_page(add_plan_url)
        _, run_id = self.plans.add_data_to_plan(plan.name, plan.description, message)
        run_view_url = self.data.server_name + self.plan_data.run_view_url.format(run_id)
        self.plans.open_page(run_view_url)
        self.plans.assert_no_close_link()

    @pytest.mark.testrail(id=2169)
    def test_c2169_edit_plan(self):
        plan1 = self.plan_data.plans[0]
        plan2 = self.plan_data.plans[1]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan

        self.plans.open_page(add_plan_url)
        plan_id, _ = self.plans.add_data_to_plan(plan1.name, plan1.description, add_message)
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id

        self.plans.open_page(edit_plan_url)
        self.plans.edit_plan(plan2.name, plan2.description)
        self.plans.confirm_edit_plan(edit_message)

        self.plans.open_page(view_plan_url)
        self.plans.validate_plan(plan2.name, plan2.description)

    @pytest.mark.testrail(id=2170)
    def test_c2170_edit_runs_in_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan
        run_url = self.data.server_name + self.plan_data.run_view_url
        description_1 = self.plan_data.add.run_description_1
        description_2 = self.plan_data.add.run_description_2
        run_name_1 = self.plan_data.add.run_names[0]
        run_name_2 = self.plan_data.add.run_names[1]

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)
        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()
        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id

        self.plans.open_page(edit_plan_url)
        self.plans.add_run_description(description_1, run_number=1)
        self.plans.add_run_description(description_2, run_number=2)
        self.plans.edit_run_name(run_name_1, run_number=1)
        self.plans.edit_run_name(run_name_2, run_number=2)
        self.plans.confirm_edit_plan(edit_message)

        self.plans.open_page(view_plan_url)
        self.plans.verify_run_names([run_name_1, run_name_2])

        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_run_description(description_1)
        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_run_description(description_2)

    @pytest.mark.testrail(id=2171)
    @pytest.mark.dependency(depends=["test_c2173_add_configurations"])
    def test_c2171_edit_configurations(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan
        configuration_group = self.plan_data.add.configuration_group
        configuration_options = self.plan_data.add.configuration_options
        selected_options = self.plan_data.add.configuration_selected_options
        alternate_options = self.plan_data.add.configuration_alternate_options

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(1)
        self.plans.open_configurations()
        self.plans.select_configuration_options(selected_options)
        self.plans.assert_selected_configuration_options(selected_options)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id

        self.plans.open_page(edit_plan_url)
        self.plans.open_configurations()
        self.plans.change_configuration_options(configuration_options, alternate_options)
        self.plans.confirm_edit_plan(edit_message, popup=True)
        self.plans.open_page(view_plan_url)
        self.plans.assert_runs_match_configurations(alternate_options)

    @pytest.mark.testrail(id=2174)
    def test_c2174_edit_test_case_selection_in_test_run(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        edit_message = self.plan_data.messages.msg_success_edited_plan
        run_url = self.data.server_name + self.plan_data.run_view_url

        case1, case2, case3 = self.cases

        self.plans.open_page(add_plan_url)
        self.plans.select_cases(case1.title, case2.title)
        plan_id, run_id = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.select_cases(case1.title, case3.title, add_run=False)
        self.plans.unselect_cases(case2.title)
        self.plans.confirm_edit_plan(edit_message)

        self.plans.open_page(run_url.format(run_id))
        self.plans.assert_cases_in_run(case1.title, case3.title)

    @pytest.mark.testrail(id=2175)
    def test_c2175_rerun_closed_plan(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        message = self.plan_data.messages.msg_success_added_plan
        run_name = self.plan_data.add.run_names[0]

        self.plans.open_page(add_plan_url)
        self.plans.add_run_with_name(run_name)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, message, add_runs=False)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.close_plan()

        self.plans.open_page(view_plan_url)
        self.plans.rerun_plan(message)
        self.plans.verify_run_names([run_name])
        self.plans.validate_plan(plan.name, plan.description)

    @pytest.mark.testrail(id=346)
    def test_c346_close_plan_check_no_edit(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        not_allowed_message  = self.plan_data.messages.msg_edit_not_allowed

        self.plans.open_page(add_plan_url)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message)

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.close_plan()

        self.plans.open_page(edit_plan_url)
        self.plans.check_page(view_plan_url)
        self.plans.check_error_message(not_allowed_message)
        self.plans.assert_no_edit_link()

    @pytest.mark.testrail(id=352)
    def test_c352_check_child_runs_are_closed(self):
        plan = self.plan_data.plans[0]
        add_plan_url = self.data.server_name + self.plan_data.add_url + self.project_id
        add_message = self.plan_data.messages.msg_success_added_plan
        completed_messsage = self.plan_data.messages.msg_run_completed
        run_url = self.data.server_name + self.plan_data.run_view_url

        self.plans.open_page(add_plan_url)
        self.plans.add_runs_to_plan(2)
        plan_id, _ = self.plans.add_data_to_plan(plan.name, plan.description, add_message, add_runs=False)
        run_1_id, run_2_id = self.plans.retrieve_multiple_run_ids_from_plan()

        edit_plan_url = self.data.server_name + self.plan_data.edit_url + plan_id
        view_plan_url = self.data.server_name + self.plan_data.view_url + plan_id
        self.plans.open_page(edit_plan_url)
        self.plans.close_plan()

        self.plans.open_page(run_url.format(run_1_id))
        self.plans.assert_run_closed(completed_messsage)

        self.plans.open_page(run_url.format(run_2_id))
        self.plans.assert_run_closed(completed_messsage)
