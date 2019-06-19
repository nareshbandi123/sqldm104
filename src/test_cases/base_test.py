import pytest
from src.common import decode_data, merge_configs, read_config
from src.helpers.api_client import APIClient
from src.helpers.driver_manager import DriverManager as driver_manager, DriverType, DriverOptions
from src.helpers.prepare_data import PrepareData
from src.models.api.config import Config as APIConfig
from src.models.api.config_group import ConfigGroup
from src.models.api.project import Project
from src.pages.api.api_page import APIPage
from src.pages.login_page import LoginPage
from src.pages.administration.users_roles_page import UsersRolesPage
from src.pages.administration.project_page import ProjectPage


class Base:

    @classmethod
    def setup_database(cls, settings):
        data = cls.data
        config = data.database
        dbtype = config['dbtype']
        if dbtype == 'mssql':
            from src.helpers.database import execute_mssql_code as execute_sql
            setup_sql = settings.database.mssql.setup
            teardown_sql = settings.database.mssql.teardown
            dump_file = settings.database.mssql.dump_file if 'dump_file' in settings.database.mssql else False
        elif dbtype == 'mysql' or dbtype == 'local':
            from src.helpers.database import execute_mysql_code as execute_sql
            setup_sql = settings.database.mysql.setup
            teardown_sql = settings.database.mysql.teardown
            dump_file = settings.database.mysql.dump_file if 'dump_file' in settings.database.mysql else False
        elif dbtype == 'hosted':
            from src.helpers.database import execute_mysql_code as execute_sql
            setup_sql = settings.database.hosted.setup
            teardown_sql = settings.database.hosted.teardown
            dump_file = settings.database.hosted.dump_file if 'dump_file' in settings.database.hosted else False
        else:
            raise Exception("Unknown database type {}".format(dbtype))

        cls._database_config = config
        cls._execute_sql = execute_sql
        cls._teardown_sql = teardown_sql

        if setup_sql:
            execute_sql(setup_sql, config)

        if dump_file:
            with open(dump_file) as dump:
                dump_lines = dump.readlines()
                if dbtype == 'mssql':
                    dump_lines.insert(1, 'SET IDENTITY_INSERT audit_log ON;')
                execute_sql(dump_lines, config)

    @classmethod
    def teardown_database(cls):
        config = cls._database_config
        execute_sql = cls._execute_sql
        teardown_sql = cls._teardown_sql

        if teardown_sql:
            execute_sql(teardown_sql, config)

    @classmethod
    def execute_sql_query(cls, sql_string, return_result=False):
        return cls.execute_sql_queries([sql_string], return_result)

    @classmethod
    def execute_sql_queries(cls, sql_strings, return_result=False):
        config = cls._database_config
        execute_sql = cls._execute_sql

        return execute_sql(sql_strings, config, return_result)

    @classmethod
    def get_setting_value(cls, setting_name):
        res = cls.execute_sql_query("select value from settings where name = '" + setting_name + "';", return_result=True)
        if len(res) and len(res[0]):
            return res[0][0]
        else:
            return None

    @classmethod
    def remove_setting(cls, setting_name):
        res = cls.execute_sql_query("delete from settings where name = '" + setting_name + "';")


class BaseTest(Base):

    @classmethod
    def setup_class(cls):
        # Get test data
        cls.data = merge_configs('~/testrail.json', '../config/data.json')

        # capabilities = read_config('../config/defaultCapabilities.json')
        options = DriverOptions()
        try:
            # pytest.config is an AttributeError if called outside a test run, e.g. from the interactive interpreter
            browserName = pytest.config.getoption('browser')
            # gridURL  = pytest.config.getoption('gridurl')
            if pytest.config.getoption('headless', default=None) is not None:
                options.attrs['headless'] = True
        except AttributeError:
            browserName = 'firefox'

        # Prepare browser
        cls.driver = driver_manager.get_driver(browserName=DriverType.get_driver_type(browserName),
                                               options = options,
                                               capabilities=None,
                                               commandExecutor=None)
        driver_manager.start_service(cls.driver, cls.data.server_name)
        cls.login = LoginPage(cls.driver)

    @classmethod
    def teardown_class(cls):
        driver_manager.quit_driver(cls.driver)


class APIBaseTest(Base):

    suite_mode = 1

    @classmethod
    def setup_class(cls):
        cls.data = merge_configs('~/testrail.json', '../config/data.json')
        cls.client = APIClient(cls.data)
        cls.projects_created = []

        options = DriverOptions()
        try:
            browserName = pytest.config.getoption('browser')
            if pytest.config.getoption('headless', default=None) is not None:
                options.attrs['headless'] = True
        except AttributeError:
            browserName = 'firefox'

        # Prepare browser
        cls.driver = driver_manager.get_driver(browserName=DriverType.get_driver_type(browserName),
                                               options=options,
                                               capabilities=None,
                                               commandExecutor=None)
        driver_manager.start_service(cls.driver, cls.data.server_name)

        cls.prepare_data = PrepareData(cls.driver)
        cls.login = LoginPage(cls.driver)
        cls.api = APIPage()

        cls.check_api_enabled()

        # add project
        project = Project(name="API Test Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=cls.suite_mode)
        project_created = cls.client.add_project(project)
        cls.projects_created.append(project_created)
        cls.project = project_created

    @classmethod
    def add_configs(cls):
        cls.groups_configs = {
            'OS': ["Win", "Mac", "Unix"],
            'Browsers': ["IE", "Chrome", "Safari"]
        }
        cls.config_ids = []
        cls.config_group_ids = []
        for group_name, configs in cls.groups_configs.items():
            group = cls.client.add_config_group(cls.project.id, ConfigGroup(name=group_name))
            for config in configs:
                config = cls.client.add_config(group.id, APIConfig(name=config))
                cls.config_ids.append(config.id)
                cls.config_group_ids.append(group.id)

    @classmethod
    def teardown_class(cls):
        driver_manager.quit_driver(cls.driver)
        for project in cls.projects_created:
            try:
                cls.client.delete_project(project)
            except:
                # We want to try and delete all projects
                # even if some error.
                pass

    @classmethod
    def check_api_enabled(cls):
        cls.login.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.prepare_data.enable_api()

    @classmethod
    def add_user_with_permissions(cls, permission="Read-only"):
        cls.users = read_config('../config/users.json')
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.users_overview_url = cls.data.server_name + cls.users.overview_url

        cls.user = decode_data(str(cls.users.regular_user))
        cls.users_roles.open_page(cls.users_overview_url)
        cls.users_roles.add_user(cls.user)

        cls.users_roles.select_user(cls.user.full_name)
        cls.users_roles.open_access_tab()
        cls.users_roles.change_role_for_user(permission)

        return cls.user

    @classmethod
    def add_user_with_project_permissions(cls, project_id:int, permission="Read-only"):
        cls.project = read_config('../config/project.json')
        cls.projects = ProjectPage(cls.driver)
        cls.edit_project_url = cls.data.server_name + cls.project.edit_project_url + str(project_id)
        cls.users = read_config('../config/users.json')
        cls.users_roles = UsersRolesPage(cls.driver)
        cls.users_overview_url = cls.data.server_name + cls.users.overview_url

        cls.user = decode_data(str(cls.users.tester_user))
        cls.users_roles.open_page(cls.users_overview_url)
        user_id = cls.users_roles.add_user(cls.user)

        cls.projects.open_page(cls.edit_project_url)
        cls.projects.open_access_tab()
        cls.projects.change_role_for_user(user_id, permission)

        return cls.user

    @classmethod
    def delete_user(cls):
        cls.users_roles.open_page(cls.users_overview_url)
        cls.users_roles.forget_user(cls.user.full_name)
