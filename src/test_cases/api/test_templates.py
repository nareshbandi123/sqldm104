import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.template import Template


@pytest.mark.api
class TestTemplatesAPI(APIBaseTest):

    @pytest.mark.testrail(id=4088)
    def test_c4088_get_templates(self):
        templates = self.client.get_templates(self.project.id)
        template_dict = {template.name: template for template in templates}

        expected_templates = [
            Template(name="Test Case (Text)", is_default=True),
            Template(name="Test Case (Steps)", is_default=False),
            Template(name="Exploratory Session", is_default=False),
        ]
        for expected in expected_templates:
            actual = template_dict[expected.name]
            assert actual.name == expected.name
            assert actual.is_default == expected.is_default
