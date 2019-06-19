import pytest
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.milestone import Milestone


@pytest.mark.api
class TestMilestonesAPI(APIBaseTest):

    @pytest.mark.testrail(id=4029)
    def test_c4029_add_milestone(self):
        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created = self.client.add_milestone(milestone, self.project.id)

        assert created.name == milestone.name
        assert created.description == milestone.description

    @pytest.mark.testrail(id=4030)
    def test_c4030_get_milestones(self):
        milestones = self.client.get_milestones(self.project.id)
        milestone_ids = set(milestone.id for milestone in milestones)

        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created = self.client.add_milestone(milestone, self.project.id)

        assert created.id not in milestone_ids
        updated_milestones = self.client.get_milestones(self.project.id)
        updated_milestone_ids = set(milestone.id for milestone in updated_milestones)
        assert created.id in updated_milestone_ids
        assert len(updated_milestone_ids) == len(milestone_ids) + 1

    @pytest.mark.testrail(id=4031)
    def test_c4031_get_milestone(self):
        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created = self.client.add_milestone(milestone, self.project.id)

        fetched = self.client.get_milestone(created.id)
        assert fetched.name == milestone.name
        assert fetched.description == milestone.description

    @pytest.mark.testrail(id=4032)
    def test_c4032_update_milestone(self):
        original = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created = self.client.add_milestone(original, self.project.id)

        created.is_started = True
        created.is_completed = True
        created.name = "A New Name"
        created.description = "A new description"
        updated = self.client.update_milestone(created)

        assert updated.name == created.name
        assert updated.description == created.description
        assert updated.is_started
        assert updated.is_completed

        milestone = self.client.get_milestone(created.id)

        assert milestone.name == updated.name
        assert milestone.description == updated.description
        assert milestone.is_started
        assert milestone.is_completed

    @pytest.mark.testrail(id=4115)
    def test_c4115_delete_milestone(self):
        milestone = Milestone(name="A New Milestone", description="This is a description of a milestone")
        created = self.client.add_milestone(milestone, self.project.id)

        milestones = self.client.get_milestones(self.project.id)
        milestone_ids = set(milestone.id for milestone in milestones)

        assert created.id in milestone_ids

        self.client.delete_milestone(created)

        updated_milestones = self.client.get_milestones(self.project.id)
        updated_milestone_ids = set(milestone.id for milestone in updated_milestones)

        assert created.id not in updated_milestone_ids
        assert len(updated_milestones) == len(milestones) - 1

    def test_milestone_no_project(self):
        project_ids = [project.id for project in self.client.get_projects()]
        missing = max(project_ids) + 1

        with pytest.raises(APIError) as e_info:
            self.client.get_milestones(missing)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_missing_milestone(self):
        with pytest.raises(APIError) as e_info:
            # A milestone that definitely won't exist
            self.client.get_milestone(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :milestone_id is not a valid milestone.'

    def test_add_milestone_missing_name(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_milestone(Milestone(name=None), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :name is a required field.'

    def test_add_milestone_invalid_parent(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_milestone(Milestone(name='Foo', parent_id=2 ** 31), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :parent_id is not a valid milestone.'

    def test_add_milestone_invalid_due_on(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_milestone(Milestone(name='Foo', due_on='never'), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :due_on is not a valid integer.'

    def test_add_milestone_invalid_start_on(self):
        with pytest.raises(APIError) as e_info:
            self.client.add_milestone(Milestone(name='Foo', start_on='never'), self.project.id)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :start_on is not a valid integer.'
