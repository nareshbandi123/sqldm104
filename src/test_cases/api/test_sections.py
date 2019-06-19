import pytest
from src.test_cases.base_test import APIBaseTest
from src.models.api.section import Section


@pytest.mark.api
class TestSectionsAPI(APIBaseTest):

    @pytest.mark.testrail(id=4025)
    def test_c4025_add_section(self):
        section = Section(name="New section", description="A section description")
        created = self.client.add_section(section, self.project.id)

        assert created.name == section.name
        assert created.description == section.description

    @pytest.mark.testrail(id=4026)
    def test_c4026_get_sections(self):
        sections = self.client.get_sections(self.project.id)
        section_ids = set(section.id for section in sections)

        section = Section(name="New section", description="A section description")
        created = self.client.add_section(section, self.project.id)

        assert created.id not in section_ids
        updated_sections = self.client.get_sections(self.project.id)
        updated_section_ids = set(section.id for section in updated_sections)
        assert created.id in updated_section_ids
        assert len(updated_sections) == len(sections) + 1

    @pytest.mark.testrail(id=4027)
    def test_c4027_get_section(self):
        section = Section(name="New section", description="A section description")
        created = self.client.add_section(section, self.project.id)

        fetched = self.client.get_section(created.id)
        assert fetched.name == section.name
        assert fetched.description == section.description

    @pytest.mark.testrail(id=4028)
    def test_c4028_update_section(self):
        original = Section(name="New section", description="A section description")
        created = self.client.add_section(original, self.project.id)

        created.name = "A New Name"
        created.description = "An updated description"
        updated = self.client.update_section(created)

        assert updated.name == created.name
        assert updated.description == created.description

        section = self.client.get_section(created.id)

        assert section.name == updated.name
        assert section.description == updated.description

    @pytest.mark.testrail(id=4114)
    def test_c4114_delete_section(self):
        section = Section(name="New section", description="A section description")
        created = self.client.add_section(section, self.project.id)

        sections = self.client.get_sections(self.project.id)
        section_ids = set(section.id for section in sections)

        assert created.id in section_ids

        self.client.delete_section(created)

        updated_sections = self.client.get_sections(self.project.id)
        updated_section_ids = set(section.id for section in updated_sections)

        assert created.id not in updated_section_ids
        assert len(updated_sections) == len(sections) - 1
