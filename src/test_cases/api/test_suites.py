import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.suite import Suite


@pytest.mark.api
class TestSuitesAPI(APIBaseTest):

    suite_mode = 3

    def teardown_method(self):
        for suite in self.client.get_suites(self.project.id):
            self.client.delete_suite(suite)

    @pytest.mark.testrail(id=4081)
    def test_c4081_add_suite(self):
        suite = Suite(name="A Test Suite", description="A suite description")
        created = self.client.add_suite(suite, self.project.id)

        assert created.name == suite.name
        assert created.description == suite.description
        assert not created.is_completed
        assert not created.is_master
        assert not created.is_baseline
        assert created.project_id == self.project.id

    @pytest.mark.testrail(id=4082)
    def test_c4082_get_suite(self):
        original = Suite(name="A Test Suite", description="A suite description")
        created = self.client.add_suite(original, self.project.id)

        suite = self.client.get_suite(created.id)

        assert suite.name == created.name
        assert suite.description == created.description
        assert suite.is_completed == created.is_completed
        assert suite.is_master == created.is_master
        assert suite.is_baseline == created.is_baseline
        assert suite.project_id == self.project.id
        assert suite.id == created.id

    @pytest.mark.testrail(id=4083)
    def test_c4083_get_suites(self):
        suites = self.client.get_suites(self.project.id)

        suite = Suite(name="A Test Suite", description="A suite description")
        created = self.client.add_suite(suite, self.project.id)

        suite_ids = {suite.id for suite in suites}
        assert created.id not in suite_ids

        updated_suites = self.client.get_suites(self.project.id)
        updated_suite_ids = {suite.id for suite in updated_suites}
        assert created.id in updated_suite_ids

    @pytest.mark.testrail(id=4084)
    def test_c4084_update_suite(self):
        original = Suite(name="A Test Suite", description="A suite description")
        created = self.client.add_suite(original, self.project.id)

        created.name = "A New Name"
        created.description = "An updated description"
        updated = self.client.update_suite(created)

        assert updated.name == created.name
        assert updated.description == created.description

    @pytest.mark.testrail(id=5778)
    def test_c5778_delete_suite(self):
        suite = Suite(name="A Test Suite", description="A suite description")
        created = self.client.add_suite(suite, self.project.id)

        suites = self.client.get_suites(self.project.id)
        suite_ids = {suite.id for suite in suites}
        assert created.id in suite_ids

        self.client.delete_suite(created)

        updated_suites = self.client.get_suites(self.project.id)
        updated_suite_ids = {suite.id for suite in updated_suites}
        assert created.id not in updated_suite_ids