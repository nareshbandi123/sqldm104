import os
import sys
sys.path.append(os.path.abspath('../..'))

from locust import HttpLocust, TaskSet, task
from src.common import merge_configs
from src.helpers.api_client import APIClient, Client
from src.models.api.project import Project


class LocustClient(APIClient):
    def __init__(self, config, tasks):
        self.client = Client(config, tasks.client)


class Tasks(TaskSet):

    def on_start(self):
        data = merge_configs('~/testrail.json', '../../config/data.json', server=self.parent.host)
        self._client = LocustClient(data, self)

        project = Project(name="API Test Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=3)
        self._project = self._client.add_project(project)

    def on_stop(self):
        if hasattr(self, '_project'):
            self._client.delete_project(self._project)

    @task(100)
    def get_users(self):
        self._client.get_users()

    @task(100)
    def get_projects(self):
        self._client.get_projects()

    @task(1)
    def add_and_delete_project(self):
        project = Project(name="API Test Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=3)
        project = self._client.add_project(project)
        self._client.delete_project(project)


class GetUsers(HttpLocust):
    task_set = Tasks
