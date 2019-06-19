import pytest
from src.common import read_config
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.case_field import CaseField, CaseFieldContext, CaseFieldOptions

@pytest.mark.api
class TestCaseFieldsAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        config = read_config('../config/api_case_fields.json')
        cls.setup_database(config)

    @classmethod
    def teardown_class(cls):
        cls.teardown_database()
        super().teardown_class()

    @pytest.mark.testrail(id=5838)
    def test_c5838_get_case_fields(self):
        case_fields = self.client.get_case_fields()

        expected = [
            CaseField(
                name='automation_type',
                label='Automation Type',
                include_all=True,
                template_ids=[],
                configs=[{
                    "context": CaseFieldContext(is_global=True, project_ids=[]),
                    "options": CaseFieldOptions(is_required=False, default_value='0', items='0, None\n1, Ranorex'),
                }],
                system_name='custom_automation_type',
                is_active=True,
                type_id=6,
            ),
            CaseField(
                name='expected',
                label='Expected Result',
                description='The expected result after executing the test case.',
                include_all=False,
                template_ids=[1],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, default_value='', format='markdown', rows='7'),
                }],
                system_name='custom_expected',
                is_active=True,
                type_id=3,
            ),
            CaseField(
                name='goals',
                label='Goals',
                description='A detailed list of goals to cover as part of the exploratory sessions.',
                include_all=False,
                template_ids=[3],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, default_value='', format='markdown', rows='7'),
                }],
                system_name='custom_goals',
                is_active=True,
                type_id=3,
            ),
            CaseField(
                name='mission',
                label='Mission',
                description='A high-level overview of what to test and which areas to cover, usually just 1-2 sentences.',
                include_all=False,
                template_ids=[3],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, default_value='', format='markdown', rows='7'),
                }],
                system_name='custom_mission',
                is_active=True,
                type_id=3,
            ),
            CaseField(
                name='preconds',
                label='Preconditions',
                description='The preconditions of this test case. Reference other test cases with [C#] (e.g. [C17]).',
                include_all=False,
                template_ids=[1, 2],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, default_value='', format='markdown', rows='7'),
                }],
                system_name='custom_preconds',
                is_active=True,
                type_id=3,
            ),
            CaseField(
                name='steps',
                label='Steps',
                description='The required steps to execute the test case.',
                include_all=False,
                template_ids=[1],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, default_value='', format='markdown', rows='7'),
                }],
                system_name='custom_steps',
                is_active=True,
                type_id=3,
            ),
            CaseField(
                name='steps_separated',
                label='Steps',
                include_all=False,
                template_ids=[2],
                configs=[{
                    "context": CaseFieldContext(is_global=True),
                    "options": CaseFieldOptions(is_required=False, format='markdown', rows='5', has_expected=True),
                }],
                system_name='custom_steps_separated',
                is_active=True,
                type_id=10,
            )
        ]

        case_field_dict = {case_field.name: case_field for case_field in case_fields}
        for expected_case_field in expected:
            actual_case_field = case_field_dict[expected_case_field.name]
            # The display order can vary on different systems so we don't test it
            actual_case_field.display_order = expected_case_field.display_order
            # This checks all fields including configs
            assert actual_case_field == expected_case_field

    @pytest.mark.testrail(id=5839)
    def test_c5839_add_case_field(self):
        name = "some_field"
        case_field = CaseField(
            type="Dropdown",
            name=name,
            label='Some Field',
            description="This is a custom case field",
            include_all=True,
            template_ids=[],
            configs=[{
                "context": CaseFieldContext(is_global=False, project_ids=[self.project.id]),
                "options": CaseFieldOptions(is_required=False, default_value='1', items='1, First\n2, Second'),
            }],
        )

        created = self.client.add_case_field(case_field)
        assert created.name == name
        assert created.system_name == "custom_" + name
        assert created.type_id == 6
        assert created.label == case_field.label
        assert created.description == case_field.description
        assert created.is_multi == 0
        assert created.is_active == 1
        assert created.status_id == 1
        assert created.include_all == 1
        assert created.template_ids == []
        assert created.configs == [{
            "context": CaseFieldContext(is_global=False, project_ids=[self.project.id]),
            "options": CaseFieldOptions(
                is_required=False,
                default_value='1',
                items='1, First\n2, Second',
            )
        }]

    def test_add_case_field_invalid_type(self):
        case_field = CaseField(
            type="InvalidTypeXXX",
            name="some_field",
            label='Some Field',
        )

        with pytest.raises(APIError) as e_info:
            self.client.add_case_field(case_field)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Invalid or missing custom field type. Please check the Type field.'

    def test_add_case_field_missing_name(self):
        case_field = CaseField(
            type="Dropdown",
            name=None,
            label='Some Field',
        )

        with pytest.raises(APIError) as e_info:
            self.client.add_case_field(case_field)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == "Field 'name' is a required field."

    def test_add_case_field_missing_label(self):
        case_field = CaseField(
            type="Dropdown",
            name="some_field",
            label=None,
        )

        with pytest.raises(APIError) as e_info:
            self.client.add_case_field(case_field)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == "Field 'label' is a required field."

    @pytest.mark.xfail(reason='Wrong status code and message')
    def test_add_case_field_missing_invalid_name(self):
        case_field = CaseField(
            type="Dropdown",
            name="some field",
            label='Some Field',
        )

        with pytest.raises(APIError) as e_info:
            self.client.add_case_field(case_field)

        error = e_info.value
        assert error.status_code == 400
        # Uncomment the assert once the test starts passing
        #assert error.error == "Field :name is invalid."