import pytest
from src.helpers.api_client import APIError
from src.test_cases.base_test import APIBaseTest
from src.models.api.config import Config
from src.models.api.config_group import ConfigGroup


@pytest.mark.api
class TestConfigsAPI(APIBaseTest):

    def teardown_method(self):
        groups = self.client.get_configs(self.project.id)
        for group in groups:
            self.client.delete_config_group(group.id)

    @pytest.mark.testrail(id=4052)
    def test_c4052_add_config_group(self):
        group = ConfigGroup(name="Browsers")
        created = self.client.add_config_group(self.project.id, group)

        assert created.name == group.name

    @pytest.mark.testrail(id=4053)
    def test_c4053_add_config(self):
        group = ConfigGroup(name="Browsers")
        group = self.client.add_config_group(self.project.id, group)

        config = Config(name="Firefox")
        created = self.client.add_config(group.id, config)

        assert created.name == config.name
        assert created.group_id == group.id

    @pytest.mark.testrail(id=4054)
    def test_c4054_update_config_group(self):
        group = ConfigGroup(name="Browsers")
        group = self.client.add_config_group(self.project.id, group)

        group.name = "Something other than browsers"
        updated = self.client.update_config_group(group)

        assert updated.name == group.name

    @pytest.mark.testrail(id=4055)
    def test_c4055_update_config(self):
        group = ConfigGroup(name="Browsers")
        group = self.client.add_config_group(self.project.id, group)

        original = Config(name="Firefox")
        created = self.client.add_config(group.id, original)

        created.name = "Opera"
        updated = self.client.update_config(created)

        assert updated.name == created.name
        assert updated.id == created.id

    @pytest.mark.testrail(id=4056)
    def test_c4056_get_configs(self):
        # This adds two config groups with three configs each
        self.add_configs()

        groups = self.client.get_configs(self.project.id)

        expected = self.groups_configs
        assert len(groups) == len(expected)
        for group in groups:
            assert group.project_id == self.project.id
            config_names = set(expected[group.name])
            assert set(config.name for config in group.configs) == config_names
            for config in group.configs:
                assert config.group_id == group.id
            del expected[group.name]

        assert len(expected) == 0

    @pytest.mark.testrail(id=5835)
    def test_c5835_delete_config_group(self):
        group = ConfigGroup(name="Browsers")
        created = self.client.add_config_group(self.project.id, group)

        groups = self.client.get_configs(self.project.id)
        group_ids = set(group.id for group in groups)

        assert created.id in group_ids

        self.client.delete_config_group(created.id)

        updated_groups = self.client.get_configs(self.project.id)
        updated_group_ids = set(group.id for group in updated_groups)

        assert created.id not in updated_group_ids

    @pytest.mark.testrail(id=5834)
    def test_c5834_delete_config(self):
        group = ConfigGroup(name="Browsers")
        group = self.client.add_config_group(self.project.id, group)

        config = Config(name="Firefox")
        created = self.client.add_config(group.id, config)

        self.client.delete_config(created.id)

        updated_group = self.client.get_config_group(group.id)
        assert len(updated_group.configs) == 0

    def test_get_configs_missing_project(self):
        with pytest.raises(APIError) as e_info:
            self.client.get_configs(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :project_id is not a valid or accessible project.'

    def test_add_config_missing_group(self):
        config = Config(name="Firefox")
        with pytest.raises(APIError) as e_info:
            self.client.add_config(2 ** 31, config)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :config_group_id is not a valid configuration group.'

    def test_add_group_missing_name(self):
        group = ConfigGroup(name=None)
        with pytest.raises(APIError) as e_info:
            self.client.add_config_group(self.project.id, group)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :name is a required field.'

    def test_add_config_missing_name(self):
        group = ConfigGroup(name="Browsers")
        group = self.client.add_config_group(self.project.id, group)

        config = Config(name=None)
        with pytest.raises(APIError) as e_info:
            self.client.add_config(group.id, config)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :name is a required field.'

    def test_delete_config_missing_config(self):
        with pytest.raises(APIError) as e_info:
            self.client.delete_config(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :config_id is not a valid configuration.'

    def test_delete_config_group_missing_group(self):
        with pytest.raises(APIError) as e_info:
            self.client.delete_config_group(2 ** 31)

        error = e_info.value
        assert error.status_code == 400
        assert error.error == 'Field :config_group_id is not a valid configuration group.'
