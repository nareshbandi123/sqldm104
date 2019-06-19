import pytest
from src.common import read_config
from src.models.api.result_field import ResultField
from src.test_cases.base_test import APIBaseTest

@pytest.mark.api
class TestResultFieldsAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        config = read_config('../config/api_result_fields.json')
        cls.setup_database(config)

    @classmethod
    def teardown_class(cls):
        cls.teardown_database()
        super().teardown_class()

    @pytest.mark.testrail(id=4090)
    def test_c4090_get_result_fields(self):
        result_fields = self.client.get_result_fields()
        expected = ResultField(
            name='some field',
            label='Foo',
            include_all=True,
            template_ids=[],
            configs=[],
            system_name='custom_some_field',
            is_active=True,
            type_id=5,
        )

        result_field_dict = {result_field.name: result_field for result_field in result_fields}
        actual_result_field = result_field_dict['some field']
        # The display order can vary on different systems so we don't test it
        actual_result_field.display_order = expected.display_order
        # This checks all fields including configs
        assert actual_result_field == expected
