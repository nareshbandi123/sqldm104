import pytest
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.case import Case
from src.models.api.milestone import Milestone
from src.models.api.run import Run
from src.models.api.result import Result
from src.models.api.section import Section


class Statuses:
    passed = 1
    blocked = 2
    untested = 3
    retest = 4
    failed = 5


@pytest.mark.api
class TestRunsAndResultsAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        section = Section(name="Some Section")
        created = cls.client.add_section(section, cls.project.id)
        cls.section = created
        cls.cases = []
        for title in ["Case 1", "Case 2", "Case 3"]:
            case = Case(title=title, type_id=7, priority_id=2, estimate="10m")
            case = cls.client.add_case(case, cls.section.id)
            cls.cases.append(case)

    def teardown_method(self):
        for run in self.client.get_runs(self.project.id):
            try:
                self.client.delete_run(run)
            except APIError:
                # closed runs can't be deleted
                pass

    @pytest.mark.testrail(id=4057)
    def test_c4057_add_run(self):
        run = Run(name="A Test Run", description="This is a test run", include_all=True)
        created = self.client.add_run(run, self.project.id)

        assert created.name == run.name
        assert created.description == run.description
        assert created.include_all
        assert not created.is_completed
        assert created.project_id == self.project.id
        assert created.passed_count == 0
        assert created.retest_count == 0
        assert created.blocked_count == 0
        assert created.failed_count == 0
        assert created.untested_count == 3

    @pytest.mark.testrail(id=4068)
    def test_c4068_get_run(self):
        original = Run(name="A Test Run", description="This is a test run", include_all=True)
        created = self.client.add_run(original, self.project.id)

        run = self.client.get_run(created.id)
        assert run.id == created.id
        assert run.name == created.name
        assert run.description == created.description
        assert run.include_all

    @pytest.mark.testrail(id=4069)
    def test_c4069_get_runs(self):
        runs = {}
        run_names = ["Test Run 1", "Test Run 2", "Test Run 3"]
        for name in run_names:
            run = Run(name=name, include_all=True)
            run = self.client.add_run(run, self.project.id)
            runs[name] = run

        created = self.client.get_runs(self.project.id)
        assert len(created) == len(runs)
        assert set(run.name for run in created) == set(run_names)
        created_dict = {run.name:run for run in created}
        for name in run_names:
            original = runs[name]
            created_run = created_dict[name]

            assert created_run.name == original.name
            assert created_run.include_all
            assert not created_run.is_completed
            assert created_run.project_id == self.project.id
            assert created_run.passed_count == 0
            assert created_run.retest_count == 0
            assert created_run.blocked_count == 0
            assert created_run.failed_count == 0
            assert created_run.untested_count == 3

    @pytest.mark.testrail(id=4070)
    def test_c4070_update_run(self):
        original = Run(name="A Test Run", description="This is a test run", include_all=True)
        created = self.client.add_run(original, self.project.id)

        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        milestone = self.client.add_milestone(milestone, self.project.id)

        created.name = "A New Name"
        created.description = "A different description"
        created.milestone_id = milestone.id
        created.include_all = False
        created.case_ids = [case.id for case in self.cases][:2]
        run = self.client.update_run(created)

        assert run.name == created.name
        assert run.description == created.description
        assert run.milestone_id == created.milestone_id
        assert not run.include_all
        assert run.untested_count == 2

    @pytest.mark.testrail(id=4112)
    def test_c4112_add_run_empty_run(self):
        original = Run(name="A Test Run", description="This is a test run", include_all=False)
        created = self.client.add_run(original, self.project.id)

        assert created.passed_count == 0
        assert created.retest_count == 0
        assert created.blocked_count == 0
        assert created.failed_count == 0
        assert created.untested_count == 0

    @pytest.mark.testrail(id=5776)
    def test_c5776_delete_run(self):
        original = Run(name="A Test Run", description="This is a test run", include_all=True)
        created = self.client.add_run(original, self.project.id)
        runs = self.client.get_runs(self.project.id)

        assert created.id in set(run.id for run in runs)

        self.client.delete_run(created)
        updated_runs = self.client.get_runs(self.project.id)

        assert created.id not in set(run.id for run in updated_runs)

    @pytest.mark.testrail(id=5833)
    def test_c5833_close_run(self):
        original = Run(name="A Test Run", description="This is a test run", include_all=True)
        created_run = self.client.add_run(original, self.project.id)

        updated_run = self.client.close_run(created_run)
        assert updated_run.is_completed
        assert updated_run.completed_on > 0

    @pytest.mark.testrail(id=4073)
    def test_c4073_add_result(self):
        case_id = self.cases[0].id
        original_run = Run(name="A Test Run", case_ids=[case_id], include_all=False)
        created_run = self.client.add_run(original_run, self.project.id)

        tests = self.client.get_tests(created_run.id)
        assert len(tests) == 1
        test_id = tests[0].id

        result = Result(status_id=Statuses.passed, elapsed="1m 45s")
        created = self.client.add_result(result, test_id)

        assert created.elapsed == result.elapsed
        assert created.status_id == Statuses.passed
        assert created.test_id == test_id

    @pytest.mark.testrail(id=4074)
    def test_c4074_add_result_for_case(self):
        case_id = self.cases[1].id
        original_run = Run(name="A Test Run", include_all=True)
        created_run = self.client.add_run(original_run, self.project.id)

        result = Result(status_id=Statuses.failed, elapsed="1m 45s")
        created_result = self.client.add_result_for_case(result, created_run.id, case_id)

        assert created_result.status_id == Statuses.failed
        assert created_result.elapsed == result.elapsed
        test_id = created_result.test_id

        test = self.client.get_test(test_id)
        assert test.case_id == case_id
        assert test.status_id == Statuses.failed

    @pytest.mark.testrail(id=4075)
    def test_c4075_add_results(self):
        original_run = Run(name="A Test Run", include_all=True)
        created_run = self.client.add_run(original_run, self.project.id)

        tests = self.client.get_tests(created_run.id)

        results = []
        statuses = [Statuses.passed, Statuses.failed, Statuses.blocked]
        expected_results = {}
        for status, test in zip(statuses, tests):
            results.append(Result(status_id=status, test_id=test.id))
            expected_results[test.id] = status
        created_results = self.client.add_results(results, created_run.id)

        assert len(created_results) == len(results)
        assert {result.test_id: result.status_id for result in created_results} == expected_results

    @pytest.mark.testrail(id=4076)
    def test_c4076_add_results_for_cases(self):
        original_run = Run(name="A Test Run", include_all=True)
        created_run = self.client.add_run(original_run, self.project.id)

        results = []
        statuses = [Statuses.passed, Statuses.failed, Statuses.blocked]
        expected_results = {}
        for status, case in zip(statuses, self.cases):
            results.append(Result(status_id=status, case_id=case.id))
            expected_results[case.id] = status

        created_results = self.client.add_results_for_cases(results, created_run.id)

        assert len(created_results) == len(results)

        tests = self.client.get_tests(created_run.id)

        assert {test.case_id: test.status_id for test in tests} == expected_results
        test_dict = {test.id: test.status_id for test in tests}
        assert {result.test_id: result.status_id for result in created_results} == test_dict

    @pytest.mark.testrail(id=4077)
    def test_c4077_get_results(self):
        case_id = self.cases[1].id
        original_run = Run(name="A Test Run", case_ids=[case_id], include_all=False)
        created_run = self.client.add_run(original_run, self.project.id)

        tests = self.client.get_tests(created_run.id)
        assert len(tests) == 1
        test_id = tests[0].id

        statuses = [Statuses.failed, Statuses.failed, Statuses.retest, Statuses.passed]
        original_results = []
        expected_results = {}
        for index, status in enumerate(statuses):
            comment = f"Result number {index}"
            result = Result(status_id=status, test_id=test_id, comment=comment)
            original_results.append(result)
            expected_results[comment] = result

        self.client.add_results(original_results, created_run.id)

        results = self.client.get_results(test_id)
        assert len(results) == len(expected_results)
        for result in results:
            expected = expected_results.pop(result.comment)
            assert result.status_id == expected.status_id
            assert result.test_id == expected.test_id
            assert result.comment == expected.comment

    @pytest.mark.testrail(id=4078)
    def test_c4078_get_results_for_case(self):
        case_id = self.cases[2].id
        original_run = Run(name="A Test Run", case_ids=[case_id], include_all=False)
        created_run = self.client.add_run(original_run, self.project.id)

        statuses = [Statuses.retest, Statuses.failed, Statuses.retest, Statuses.passed]
        original_results = []
        expected_results = {}
        for index, status in enumerate(statuses):
            comment = f"Result number {index}"
            result = Result(status_id=status, comment=comment, case_id=case_id)
            original_results.append(result)
            expected_results[comment] = result

        self.client.add_results_for_cases(original_results, created_run.id)

        results = self.client.get_results_for_case(created_run.id, case_id)
        assert len(results) == len(expected_results)
        for result in results:
            expected = expected_results.pop(result.comment)
            assert result.status_id == expected.status_id
            assert result.comment == expected.comment

    @pytest.mark.testrail(id=4079)
    def test_c4079_get_results_for_run(self):
        original_run = Run(name="A Test Run", include_all=True)
        created_run = self.client.add_run(original_run, self.project.id)

        statuses = [Statuses.retest, Statuses.failed, Statuses.retest, Statuses.passed]
        original_results = []
        expected_results = {}
        counter = 0
        for status in statuses:
            for case in self.cases:
                comment = f"Result number {counter}"
                counter += 1
                result = Result(status_id=status, comment=comment, case_id=case.id)
                original_results.append(result)
                expected_results[comment] = result

        self.client.add_results_for_cases(original_results, created_run.id)

        results = self.client.get_results_for_run(created_run.id)
        assert len(results) == len(expected_results)
        for result in results:
            expected = expected_results.pop(result.comment)
            assert result.status_id == expected.status_id
            assert result.comment == expected.comment

    @pytest.mark.testrail(id=9362)
    @pytest.mark.parametrize("params, result", [
        ({'limit': 5}, 5),
        ({'limit': 2}, 2)
    ])
    def test_c9362_get_runs_with_valid_limit(self, params, result):
        created_runs = []
        try:
            for item in range(10):
                run = Run(name=f"Test Run {item}")
                resp = self.client.add_run(run, self.project.id)
                created_runs.append(resp)

            runs = self.client.get_runs(self.project.id, **params)
            assert len(runs) == result
        finally:
            for item in created_runs:
                self.client.delete_run(item)

    @pytest.mark.testrail(id=9363)
    @pytest.mark.parametrize("params, result", [
        ({'limit': -1}, [400, "Field :limit is not a valid natural number."]),
        ({'limit': 0}, [400, "Field :limit is too small (minimum 1)."]),
        ({'limit': 251}, [400, "Field :limit is too large (maximum 250)."])
    ])
    def test_c9363_get_runs_limit_out_of_range(self, params, result):
        created_runs = []
        try:
            for item in range(10):
                run = Run(name=f"Test Run {item}")
                resp = self.client.add_run(run, self.project.id)
                created_runs.append(resp)

            with pytest.raises(APIError) as e_info:
                self.client.get_runs(self.project.id, **params)
            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            for item in created_runs:
                self.client.delete_run(item)

    @pytest.mark.testrail(id=9364)
    @pytest.mark.parametrize("params, result", [
        ({'limit': '"'}, [400, 'Invalid characters in GET: [limit] [\"]']),
        ({'limit': 'o'}, [400, "Field :limit is not a valid natural number."])
    ])
    def test_c9364_get_runs_limit_char(self, params, result):
        created_runs = []
        try:
            for item in range(3):
                run = Run(name=f"Test Run {item}")
                resp = self.client.add_run(run, self.project.id)
                created_runs.append(resp)

            with pytest.raises(APIError) as e_info:
                self.client.get_runs(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            for item in created_runs:
                self.client.delete_run(item)

    @pytest.mark.testrail(id=9365)
    @pytest.mark.parametrize("params, result", [
        ({'offset': 2}, ['2', None]),
        ({'offset': 3}, ['1', None])
    ])
    def test_c9365_get_runs_with_offset(self, params, result):
        created_runs = []
        try:
            for item in range(5):
                run = Run(name=f"Test Run {item}")
                resp = self.client.add_run(run, self.project.id)
                created_runs.append(resp)

            runs_len = len(self.client.get_runs(self.project.id))
            runs_with_params = self.client.get_runs(self.project.id, **params)

            result[1] = runs_len - int(params['offset'])

            assert result[0] in runs_with_params[0].name
            assert len(runs_with_params) == result[1]
        finally:
            for item in created_runs:
                self.client.delete_run(item)

    @pytest.mark.testrail(id=9366)
    @pytest.mark.parametrize("params, result", [
        ({'offset': -1}, [400, "Field :offset is not a valid natural number."]),
        ({'offset': 'o'}, [400, "Field :offset is not a valid natural number."]),
        ({'offset': '\"'}, [400, 'Invalid characters in GET: [offset] [\"]'])
    ])
    def test_c9366_get_runs_invalid_offset(self, params, result):
        created_runs = []
        try:
            for item in range(5):
                run = Run(name=f"Test Run {item}")
                resp = self.client.add_run(run, self.project.id)
                created_runs.append(resp)

            with pytest.raises(APIError) as e_info:
                self.client.get_runs(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            for item in created_runs:
                self.client.delete_run(item)
