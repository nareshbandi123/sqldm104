import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.priority import Priority

@pytest.mark.api
class TestPrioritiesAPI(APIBaseTest):

    @pytest.mark.testrail(id=4091)
    def test_c4091_get_priorities(self):
        priorities = self.client.get_priorities()
        expected = [
            Priority(name="Low", short_name="Low", is_default=False, priority=1),
            Priority(name="Medium", short_name="Medium", is_default=True, priority=2),
            Priority(name="High", short_name="High", is_default=False, priority=3),
            Priority(name="Critical", short_name="Critical", is_default=False, priority=4),
        ]
        priority_dict = {priority.name: priority for priority in priorities}
        for expected_priority in expected:
            actual = priority_dict[expected_priority.name]
            assert actual.name == expected_priority.name
            assert actual.short_name == expected_priority.short_name
            assert actual.is_default == expected_priority.is_default
            assert actual.priority == expected_priority.priority