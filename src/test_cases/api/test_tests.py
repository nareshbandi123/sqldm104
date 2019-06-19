import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.case import Case
from src.models.api.run import Run
from src.models.api.section import Section


@pytest.mark.api
class TestTestsAPI(APIBaseTest):

    @pytest.mark.testrail(ids=[4071, 4072])
    def test_c4071_c4072_get_test_get_tests(self):
        # get_test and get_tests are also extensively exercised by test_runs_and_results
        section = Section(name="Some Section")
        section = self.client.add_section(section, self.project.id)
        cases = []
        for title in ["Case 1", "Case 2", "Case 3"]:
            case = Case(title=title, type_id=7, priority_id=2, estimate="10m")
            case = self.client.add_case(case, section.id)
            cases.append(case)

        run = Run(name="A Test Run", description="This is a test run", include_all=True)
        run = self.client.add_run(run, self.project.id)

        tests = self.client.get_tests(run.id)
        assert set(case.id for case in cases) == set(test.case_id for test in tests)

        for test in tests:
            assert test.priority_id == 2
            assert test.estimate == "10m"
            individual = self.client.get_test(test.id)
            # This checks all fields
            assert individual == test