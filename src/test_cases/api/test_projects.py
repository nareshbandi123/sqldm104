import pytest
from src.common import make_client
from src.helpers.api_client import APIError
from src.models.api.project import Project
from src.test_cases.base_test import APIBaseTest


@pytest.mark.api
class TestProjectsAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.add_user_with_permissions()
        cls.second_client = make_client(cls.user.email_address, cls.user.password)

    @classmethod
    def teardown_class(cls):
        cls.delete_user()
        super().teardown_class()

    @pytest.mark.testrail(id=4021)
    def test_c4021_add_project(self):
        project = Project(name="New Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=1)
        created = self.client.add_project(project)
        self.projects_created.append(created)

        assert created.name == "New Project"
        assert created.announcement == "Some announcement"
        assert created.show_announcement == False
        assert created.suite_mode == 1

        actual = self.client.get_project(created.id)
        assert actual == created

    @pytest.mark.testrail(id=4022)
    def test_c4022_get_projects(self):
        projects = self.client.get_projects()
        project_ids = set(proj.id for proj in projects)

        project = Project(name="New Project", announcement="Some announcement",
                              show_announcement=False, suite_mode=1)
        created = self.client.add_project(project)
        self.projects_created.append(created)
        assert created.id not in project_ids

        new_projects = self.client.get_projects()
        new_ids = set(proj.id for proj in new_projects)
        assert created.id in new_ids

    @pytest.mark.testrail(id=4113)
    def test_c4113_delete_project(self):
        project = Project(name="New Project", announcement="Some announcement",
                              show_announcement=False, suite_mode=1)
        created = self.client.add_project(project)

        self.client.delete_project(created)
        projects = self.client.get_projects()
        project_ids = set(proj.id for proj in projects)

        assert created.id not in project_ids

    @pytest.mark.testrail(id=4023)
    def test_c4023_get_project(self):
        original = Project(name="New Project", announcement="Some announcement",
                              show_announcement=False, suite_mode=1)
        created = self.client.add_project(original)
        self.projects_created.append(created)

        project = self.client.get_project(created.id)
        assert project.name == original.name
        assert project.announcement == original.announcement
        assert project.show_announcement == original.show_announcement
        assert project.suite_mode == original.suite_mode

    @pytest.mark.testrail(id=4024)
    def test_c4024_update_project(self):
        original = Project(name="New Project", announcement="Some announcement",
                               show_announcement=False, suite_mode=1)
        created = self.client.add_project(original)
        self.projects_created.append(created)

        created.name = "Updated name"
        created.is_completed = True
        updated = self.client.update_project(created)

        assert updated.name == "Updated name"
        assert updated.is_completed

        project = self.client.get_project(created.id)
        assert project.name == "Updated name"
        assert project.is_completed

    def test_delete_project_no_access(self):
        with pytest.raises(APIError) as e_info:
            self.second_client.delete_project(self.project)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to delete projects (requires administrator privileges).'

    def test_get_project_invalid_id(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_project(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_missing_endpoint(self):
        with pytest.raises(APIError) as e_info:
            self.client.client.send_get('non_existent_endpoint')

        error = e_info.value
        assert error.status_code == 404
        assert error.error == "Unknown method 'non_existent_endpoint'"

    def test_add_project_no_access(self):
        project = Project(name="New Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=1)

        with pytest.raises(APIError) as e_info:
            self.second_client.add_project(project)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to add projects (requires administrator privileges).'

    def test_update_project_no_access(self):
        project = Project(name="New Project", announcement="Some announcement",
                               show_announcement=False, suite_mode=1)
        project = self.client.add_project(project)
        self.projects_created.append(project)

        project.name = "Updated name"
        project.is_completed = True
        with pytest.raises(APIError) as e_info:
            self.second_client.update_project(project)

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to edit projects (requires administrator privileges).'
