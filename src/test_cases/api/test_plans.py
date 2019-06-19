import pytest
from src.helpers.api_client import  APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.case import Case
from src.models.api.plan import Plan
from src.models.api.plan_entry import PlanEntry
from src.models.api.milestone import Milestone
from src.models.api.section import Section
from src.models.api.suite import Suite

@pytest.mark.api
class TestPlansAPI(APIBaseTest):

    suite_mode = 3

    @pytest.mark.testrail(id=4046)
    def test_c4046_add_plan(self):
        plan = Plan(name="A Test Plan", description="A description of a test plan")
        created = self.client.add_plan(plan, self.project.id)

        assert created.name == plan.name
        assert created.description == plan.description

    @pytest.mark.testrail(id=4048)
    def test_c4048_get_plan(self):
        plan = Plan(name="A Test Plan", description="A description of a test plan")
        created = self.client.add_plan(plan, self.project.id)

        fetched = self.client.get_plan(created.id)
        assert fetched.name == created.name
        assert fetched.description == created.description

    @pytest.mark.testrail(id=4049)
    def test_c4049_update_plan(self):
        original = Plan(name="A Test Plan", description="A description of a test plan")
        created = self.client.add_plan(original, self.project.id)

        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created_milestone = self.client.add_milestone(milestone, self.project.id)

        created.name = "A New Test Plan Name"
        created.description = "Something a bit different"
        created.milestone_id = created_milestone.id
        updated = self.client.update_plan(created)

        assert updated.name == created.name
        assert updated.description == created.description
        assert updated.milestone_id == created_milestone.id

        plan = self.client.get_plan(created.id)

        assert plan.name == updated.name
        assert plan.description == updated.description
        assert plan.milestone_id == updated.milestone_id

    @pytest.mark.testrail(id=4050)
    def test_c4050_get_plans(self):
        plans = self.client.get_plans(self.project.id)
        plan_ids = set(plan.id for plan in plans)

        plan = Plan(name="A New plan", description="This is a description of a plan")
        created = self.client.add_plan(plan, self.project.id)

        assert created.id not in plan_ids
        updated_plans = self.client.get_plans(self.project.id)
        updated_plan_ids = set(plan.id for plan in updated_plans)
        assert created.id in updated_plan_ids
        assert len(updated_plan_ids) == len(plan_ids) + 1

    @pytest.mark.testrail(id=4051)
    def test_c4051_close_plan(self):
        original = Plan(name="A Test Plan", description="A description of a test plan")
        created = self.client.add_plan(original, self.project.id)

        updated = self.client.close_plan(created)
        assert updated.is_completed
        assert updated.completed_on > 0

        plan = self.client.get_plan(created.id)
        assert plan.is_completed
        assert plan.completed_on > 0

    @pytest.mark.testrail(id=5775)
    def test_c5775_delete_plan(self):
        plan = Plan(name="A New plan", description="This is a description of a plan")
        created = self.client.add_plan(plan, self.project.id)

        plans = self.client.get_plans(self.project.id)
        plan_ids = set(plan.id for plan in plans)

        assert created.id in plan_ids

        self.client.delete_plan(created)

        updated_plans = self.client.get_plans(self.project.id)
        updated_plan_ids = set(plan.id for plan in updated_plans)

        assert created.id not in updated_plan_ids
        assert len(updated_plans) == len(plans) - 1

    @pytest.mark.testrail(id=4047)
    def test_c4047_add_plan_entry(self):
        self.add_configs()

        suite = Suite(name="Test Suite")
        suite = self.client.add_suite(suite, self.project.id)
        section = Section(name="Test Section", suite_id=suite.id)
        section = self.client.add_section(section, self.project.id)
        plan = Plan(name="Test Plan")
        plan = self.client.add_plan(plan, self.project.id)

        config_ids = self.config_ids[:2]
        def make_run(id):
            return dict(config_ids=[id], include_all=True)

        plan_entry = PlanEntry(
            suite_id=suite.id,
            include_all=True,
            config_ids=[self.config_ids[0], self.config_ids[1]],
            runs=[make_run(id) for id in config_ids],
            name="Windows",
        )
        plan_entry_added = self.client.add_plan_entry(plan.id, plan_entry)

        assert plan_entry_added.suite_id == plan_entry.suite_id
        assert plan_entry_added.name == plan_entry.name
        assert len(plan_entry_added.runs) == 2

        # The order the runs come back in is not the same order as we sent
        # them, so we just check they're both included
        for run in plan_entry_added.runs:
            config_ids = run['config_ids']
            assert len(config_ids) == 1
            config_id = config_ids[0]
            assert config_id in config_ids
            config_ids.remove(config_id)
            assert run['include_all']
            assert not run['is_completed']
            assert run['plan_id'] == plan.id

        assert len(config_ids) == 0

    @pytest.mark.testrail(id=5837)
    def test_c5837_delete_plan_entry(self):
        self.add_configs()

        suite = Suite(name="Test Suite")
        suite = self.client.add_suite(suite, self.project.id)
        section = Section(name="Test Section", suite_id=suite.id)
        section = self.client.add_section(section, self.project.id)
        plan = Plan(name="Test Plan")
        plan = self.client.add_plan(plan, self.project.id)

        config_id = self.config_ids[0]
        plan_entry = PlanEntry(
            suite_id=suite.id,
            include_all=True,
            config_ids=[config_id],
            runs=[dict(config_ids=[config_id], include_all=True)],
            name="Windows",
        )
        plan_entry_added = self.client.add_plan_entry(plan.id, plan_entry)

        plan = self.client.get_plan(plan.id)
        assert len(plan.entries) == 1
        assert plan.entries[0]["id"] == plan_entry_added.id

        self.client.delete_plan_entry(plan.id, plan_entry_added.id)

        updated_plan = self.client.get_plan(plan.id)
        assert len(updated_plan.entries) == 0

    @pytest.mark.testrail(id=5836)
    def test_c5836_update_plan_entry(self):
        self.add_configs()

        suite = Suite(name="Test Suite")
        suite = self.client.add_suite(suite, self.project.id)
        section = Section(name="Test Section", suite_id=suite.id)
        section = self.client.add_section(section, self.project.id)
        plan = Plan(name="Test Plan")
        plan = self.client.add_plan(plan, self.project.id)

        cases = []
        for title in ["Case 1", "Case 2", "Case 3"]:
            case = Case(title=title, type_id=7, priority_id=2, estimate="10m")
            case = self.client.add_case(case, section.id)
            cases.append(case)

        plan_entry = PlanEntry(
            suite_id=suite.id,
            include_all=True,
            name="Windows",
            description="A test run"
        )
        plan_entry = self.client.add_plan_entry(plan.id, plan_entry)

        plan_entry.name = "Linux"
        plan_entry.description = "A different test run"
        plan_entry.include_all = False
        plan_entry.case_ids = [case.id for case in cases[:2]]
        # Don't attempt to update runs
        plan_entry.runs = None

        updated_plan_entry = self.client.update_plan_entry(plan.id, plan_entry)
        assert updated_plan_entry.name == plan_entry.name
        assert not updated_plan_entry.include_all
        assert len(updated_plan_entry.runs) == 1
        assert updated_plan_entry.runs[0]["untested_count"] == 2
        assert updated_plan_entry.runs[0]["description"] == plan_entry.description

    def test_add_plan_no_name(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_plan(Plan(name=None), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :name is a required field.'

    def test_add_plan_missing_project(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_plan(Plan(name='Foo'), 2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_get_plan_missing_plan(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_plan(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :plan_id is not a valid test plan.'

    def test_add_plan_missing_milestone(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_plan(Plan(name='Foo', milestone_id=2 ** 31), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :milestone_id is not a valid milestone.'

    def test_get_plans_missing_project(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_plans(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_update_plan_missing_plan(self):
        plan = Plan(name='A Plan', id=2 ** 31)
        with pytest.raises(APIError) as e_info:
            self.client.update_plan(plan)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :plan_id is not a valid test plan.'

    def test_close_plan_missing_plan(self):
        plan = Plan(name='A Plan', id=2 ** 31)
        with pytest.raises(APIError) as e_info:
            self.client.close_plan(plan)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :plan_id is not a valid test plan.'

    def test_delete_plan_missing_plan(self):
        plan = Plan(name='A Plan', id=2 ** 31)
        with pytest.raises(APIError) as e_info:
            self.client.delete_plan(plan)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :plan_id is not a valid test plan.'

    def test_delete_plan_entry_missing_entry(self):
        plan = Plan(name='A Plan')
        plan = self.client.add_plan(plan, self.project.id)
        with pytest.raises(APIError) as e_info:
            self.client.delete_plan_entry(plan.id, 2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :entry_id is not a valid test plan entry.'
