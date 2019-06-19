import pytest
from src.common import make_client
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.case import Case
from src.models.api.section import Section


@pytest.mark.api
class TestCasesAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        section = Section(name="Some Section")
        created = cls.client.add_section(section, cls.project.id)
        cls.section = created
        cls.add_user_with_permissions()
        cls.second_client = make_client(cls.user.email_address, cls.user.password)

    @classmethod
    def teardown_class(cls):
        cls.delete_user()
        super().teardown_class()

    @pytest.mark.testrail(id=4033)
    def test_c4033_add_case(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        created = self.client.add_case(case, self.section.id)

        assert created.title == case.title
        assert created.section_id == self.section.id
        assert created.type_id == case.type_id
        assert created.priority_id == case.priority_id
        assert created.estimate == case.estimate

    @pytest.mark.testrail(id=4043)
    def test_c4043_get_cases(self):
        cases = self.client.get_cases(self.project.id)
        case_ids = set(case.id for case in cases)

        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        created = self.client.add_case(case, self.section.id)

        assert created.id not in case_ids
        updated_cases = self.client.get_cases(self.project.id)
        updated_case_ids = set(case.id for case in updated_cases)
        assert created.id in updated_case_ids
        assert len(updated_cases) == len(cases) + 1

    @pytest.mark.testrail(id=4044)
    def test_4044_get_case(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        created = self.client.add_case(case, self.section.id)

        fetched = self.client.get_case(created.id)
        assert fetched.title == created.title
        assert fetched.section_id == self.section.id
        assert fetched.type_id == created.type_id
        assert fetched.priority_id == created.priority_id
        assert fetched.estimate == created.estimate

    @pytest.mark.testrail(id=4045)
    def test_4045_update_case(self):
        original = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        created = self.client.add_case(original, self.section.id)

        created.title = "A New Title"
        created.estimate = "5s"
        updated = self.client.update_case(created)

        assert updated.title == created.title
        assert updated.estimate == created.estimate

        case = self.client.get_case(created.id)
        assert case.title == updated.title
        assert case.estimate == updated.estimate

    @pytest.mark.testrail(id=5774)
    def test_c5774_delete_case(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        created = self.client.add_case(case, self.section.id)

        cases = self.client.get_cases(self.project.id)
        case_ids = set(case.id for case in cases)
        assert created.id in case_ids

        self.client.delete_case(created)
        updated_cases = self.client.get_cases(self.project.id)
        updated_case_ids = set(case.id for case in updated_cases)
        assert created.id not in updated_case_ids
        assert len(updated_cases) == len(cases) - 1

    @pytest.mark.testrail(id=4092)
    def test_c4092_get_case_types(self):
        case_types = self.client.get_case_types()
        case_type_names = set(case_type.name for case_type in case_types)

        expected_types = [
            'Acceptance', 'Accessibility', 'Automated',
            'Compatibility', 'Destructive', 'Functional',
            'Other', 'Performance', 'Regression',
            'Security', 'Smoke & Sanity', 'Usability'
        ]
        for expected_type in expected_types:
            assert expected_type in case_type_names

    def test_get_case_invalid_id(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_case(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :case_id is not a valid test case.'

    def test_get_cases_invalid_project(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_cases(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_add_case_invalid_type(self):
        case = Case(title="A New Case", type_id=9999, priority_id=2, estimate="10m")
        with pytest.raises(APIError) as e_info:
            self.client.add_case(case, self.section.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :type_id is not a valid case type.'

    def test_add_case_invalid_priority(self):
        case = Case(title="A New Case", type_id=7, priority_id=99999, estimate="10m")
        with pytest.raises(APIError) as e_info:
            self.client.add_case(case, self.section.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :priority_id is not a valid priority.'

    def test_add_case_missing_section(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        with pytest.raises(APIError) as e_info:
            self.client.add_case(case, 2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :section_id is not a valid section.'

    def test_add_case_invalid_estimate(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="XXX")
        with pytest.raises(APIError) as e_info:
            self.client.add_case(case, self.section.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :estimate is not in a valid time span format.'

    def test_add_case_no_access(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        with pytest.raises(APIError) as e_info:
            self.second_client.add_case(case, self.section.id)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to add test cases (insufficient permissions).'

    def test_delete_case_no_access(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        case = self.client.add_case(case, self.section.id)
        with pytest.raises(APIError) as e_info:
            self.second_client.delete_case(case)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to delete test cases (insufficient permissions).'

    @pytest.mark.xfail(reason="The error message is incorrect")
    def test_update_case_no_access(self):
        case = Case(title="A New Case", type_id=7, priority_id=2, estimate="10m")
        case = self.client.add_case(case, self.section.id)

        case.title = "A New Title"
        case.estimate = "5s"
        with pytest.raises(APIError) as e_info:
            self.second_client.update_case(case)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to edit test cases (insufficient permissions).'


    @pytest.mark.testrail(id=5850)
    @pytest.mark.parametrize("params, result", [
        ({'limit': 2}, 2)
    ])
    def test_c5850_get_cases_with_limit(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='10m')
            self.client.add_case(case, self.section.id)
            self.client.add_case(case, self.section.id)

            cases = self.client.get_cases(self.project.id, **params)
            assert len(cases) == result

            self.client.add_case(case, self.section.id)

            updated_cases = self.client.get_cases(self.project.id, **params)
            assert len(updated_cases) == result
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5849)
    @pytest.mark.parametrize("params, result", [
        ({'limit': 2}, 'First'),
        ({'limit': 2, 'offset': 1}, 'Second')
    ])
    def test_c5849_get_cases_with_limit_and_offset(self, params, result):
        try:
            case1 = Case(title='First new case', type_id=7, priority_id=2, estimate='10m')
            case2 = Case(title='Second new case', type_id=7, priority_id=2, estimate='10m')
            case3 = Case(title='Third new case', type_id=7, priority_id=2, estimate='10m')
            self.client.add_case(case1, self.section.id)
            self.client.add_case(case2, self.section.id)
            self.client.add_case(case3, self.section.id)
            cases = self.client.get_cases(self.project.id, **params)
            assert result in cases[0].title
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5848)
    @pytest.mark.parametrize("params", [
        ({'filter': 'łŻ∂ą'}),
        ({'filter': 'ś∆'})
    ])
    def test_c5848_get_cases_with_filter_utf8(self, params):
        try:
            case = Case(title='łŻ∂ąś∆īp', type_id=7, priority_id=2, estimate='10m')
            reference = self.client.add_case(case, self.section.id)
            result = reference

            cases = self.client.get_cases(self.project.id, **params)
            assert result in cases
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5949)
    @pytest.mark.parametrize("params, result", [
        ({'limit': 0}, (400, 'Field :limit is too small (minimum 1).')),
        ({'limit': 251}, (400, 'Field :limit is too large (maximum 250).'))
    ])
    def test_c5949_get_cases_beyond_limit_boundaries(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
            self.client.add_case(case, self.section.id)

            with pytest.raises(APIError) as e_info:
                self.client.get_cases(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5950)
    @pytest.mark.parametrize("params, result", [
        ({'limit': -1}, (400, 'Field :limit is not a valid natural number.'))
    ])
    def test_c5950_get_cases_limit_negative(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
            self.client.add_case(case, self.section.id)

            with pytest.raises(APIError) as e_info:
                self.client.get_cases(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5951)
    @pytest.mark.parametrize("params, result", [
        ({'limit': 'o'}, (400, 'Field :limit is not a valid natural number.'))
    ])
    def test_c5951_get_cases_limit_char(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
            self.client.add_case(case, self.section.id)

            with pytest.raises(APIError) as e_info:
                self.client.get_cases(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5952)
    @pytest.mark.parametrize("params, result", [
        ({'offset': -1}, (400, 'Field :offset is not a valid natural number.'))
    ])
    def test_c5952_get_cases_offset_negative(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
            self.client.add_case(case, self.section.id)

            with pytest.raises(APIError) as e_info:
                self.client.get_cases(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5953)
    @pytest.mark.parametrize("params, result", [
        ({'offset': "o"}, (400, 'Field :offset is not a valid natural number.'))
    ])
    def test_c5953_get_cases_offset_char(self, params, result):
        try:
            case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
            self.client.add_case(case, self.section.id)

            with pytest.raises(APIError) as e_info:
                self.client.get_cases(self.project.id, **params)

            error = e_info.value
            assert error.status_code == result[0]
            assert error.error == result[1]
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5851)
    @pytest.mark.parametrize("params, result", [
        ({'filter': "Second", 'limit': 4, 'offset': 1}, (4, "Second")),
        ({'filter': "First", 'limit': 20, 'offset': 5}, (5, 'First'))
    ])
    def test_c5851_get_cases_with_combined_params(self, params, result):
        try:
            cases = self.client.get_cases(self.project.id)

            for item in cases:
                self.client.delete_case(item)

            for x in range(0, 10):
                case1 = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
                self.client.add_case(case1, self.section.id)

                case2 = Case(title='Second new case', type_id=7, priority_id=2, estimate='2m')
                self.client.add_case(case2, self.section.id)

            cases = self.client.get_cases(self.project.id, **params)

            assert len(cases) == result[0]
            for item in cases:
                assert result[1] in item.title
        finally:
            to_delete = self.client.get_cases(self.project.id)
            for item in to_delete:
                self.client.delete_case(item)

    @pytest.mark.testrail(id=5954)
    @pytest.mark.parametrize("params, result", [
        ({'filter': 'First'}, []),
        ({'limit': 10}, []),
        ({'offset': 5}, []),
        ({'filter': 'First', 'limit': 10, 'offset': 2}, [])
    ])
    def test_c5954_get_tickets_with_params_no_tickets(self, params, result):
        cases = self.client.get_cases(self.project.id)

        for item in cases:
            self.client.delete_case(item)

        cases = self.client.get_cases(self.project.id, **params)
        assert cases == result

    @pytest.mark.testrail(id=5955)
    @pytest.mark.parametrize("params", [
        ({'offset': None}),
        ({'limit': 1, 'offset': None})
    ])
    def test_c5955_get_cases_offset_too_big(self, params):
        try:
            cases = self.client.get_cases(self.project.id)
            if len(cases) == 0:
                for x in range(0, 5):
                    case = Case(title='First new case', type_id=7, priority_id=2, estimate='2m')
                    self.client.add_case(case, self.section.id)

            cases = self.client.get_cases(self.project.id)

            result = ([] if 'limit' in params.keys() else cases)
            params['offset'] = len(cases)
            filtered_cases = self.client.get_cases(self.project.id, **params)
            assert filtered_cases == result
        finally:
            for item in cases:
                self.client.delete_case(item)
