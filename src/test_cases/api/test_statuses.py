import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.status import Status

@pytest.mark.api
class TestStatusesAPI(APIBaseTest):

    @pytest.mark.testrail(id=4089)
    def test_c4089_get_statuses(self):
        statuses = self.client.get_statuses()
        expected = [
            Status(label="Passed", name="passed", is_final=True, is_system=True, is_untested=False),
            Status(label="Blocked", name="blocked", is_final=True, is_system=True, is_untested=False),
            Status(label="Untested", name="untested", is_final=False, is_system=True, is_untested=True),
            Status(label="Retest", name="retest", is_final=False, is_system=True, is_untested=False),
            Status(label="Failed", name="failed", is_final=True, is_system=True, is_untested=False),
        ]
        status_dict = {status.name: status for status in statuses}
        for expected_status in statuses:
            actual = status_dict[expected_status.name]
            assert actual.name == expected_status.name
            assert actual.label == expected_status.label
            assert actual.is_final == expected_status.is_final
            assert actual.is_system == expected_status.is_system
            assert actual.is_untested == expected_status.is_untested