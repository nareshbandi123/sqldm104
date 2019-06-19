from datetime import datetime
import os
import sys
import time

import pytest
from _pytest.terminal import TerminalReporter
from _pytest.runner import pytest_runtest_makereport as _makereport

from src.common import merge_configs, Config
from src.helpers.api_client import APIClient
from src.models.api.result import Result
from src.models.api.run import Run

sys.path.append(os.path.abspath('..'))

ROOT_DIR = os.getcwd()
TEST_REPORTS_DIR = ROOT_DIR + "/test_reports"
LOG_DIR = TEST_REPORTS_DIR + "/logs/"
SCREENSHOTS_DIR = TEST_REPORTS_DIR + "/screenshots/"


def pytest_addoption(parser):
    parser.addoption(
        "--server", action="store", default='hosted', help="specify linux, windows or hosted server and use the appropriate configuration"
    )
    parser.addoption(
        "--headless", action='store_true', default='true', help="use headless browser for tests"
    )
    parser.addoption(
        "--servername", action='store', dest="servername", help="URL where the TestRail instance is running"
    )
    parser.addoption(
        "--gridurl", action='store', dest="gridurl", help="URL where the selenium grid runs"
    )
    parser.addoption(
        "--browser", action='store', dest="browser", default='firefox', help="Browser to use"
    )
    parser.addoption(
        "--report-tests", action='store_true', dest="reporttests", default=False, help="Report test results with TestRail"
    )

    # Not impelmented yet
    # parser.addoption(
    #     "--maximize", action='store',   dest="maximize", help="Maximize browser by default"
    # )
    # parser.addoption(
    #     "--capsfile", action='store',   dest="capsfile", help="File to load capabilities from"
    # )

@pytest.fixture(scope='function', autouse=True)
def make_screenshot_on_failure(request):
    driver = request.cls.driver
    """Application setup and teardown fixture."""

    def teardown():
        """Save a screenshot if test failed."""
        try:
            if request.node.rep_call.failed:
                make_screenshots_dir()
                driver.get_screenshot_as_file(format_screenshot_name())
        except AttributeError:
            # possible in an interrupted test run
            pass

    request.addfinalizer(teardown)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    """Helper function to obtain test run status"""
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)


def format_screenshot_name():
    test_path = os.environ.get('PYTEST_CURRENT_TEST').split(" ").pop(0).replace(':', '-')
    full_name = test_path.split(os.sep).pop()
    timestamp = time.strftime("%Y%m%d-%H:%M")
    file_path = "".join([SCREENSHOTS_DIR, full_name, timestamp, ".png"])
    return file_path


def make_screenshots_dir():
    """ Make a screenshots directory """
    if not os.path.exists(SCREENSHOTS_DIR):
        os.makedirs(SCREENSHOTS_DIR)


def get_case_ids(item):
    # Return the case ids a test is marked with, or None
    # A test will be marked with pytest.mark.testrail(id=XXX) for a single id or
    # pytest.mark.testrail(ids=[1, 2, 3]) for multiple ids
    markers = item.keywords.get('pytestmark')
    if markers is None:
        return

    ids = []
    for marker in markers:
        if marker.name == 'testrail':
            case_id = marker.kwargs.get('id')
            if case_id is not None:
                return [case_id]
            return marker.kwargs.get('ids')
    return


@pytest.mark.trylast
def pytest_configure(config):
    report = config.option.reporttests

    if report:
        standard_reporter = config.pluginmanager.getplugin('terminalreporter')
        new_reporter = Reporter(standard_reporter, config)

        config.pluginmanager.unregister(standard_reporter)
        config.pluginmanager.register(new_reporter, 'terminalreporter')


class Statuses:

    PASSED = 1
    FAILED = 5
    SKIPPED = 1
    XFAIL = 1

    @classmethod
    def get(cls, name):
        return getattr(cls, name.upper(), cls.FAILED)


class Reporter(TerminalReporter):
    def __init__(self, reporter, config):
        super().__init__(reporter.config)
        self._data = merge_configs('~/testrail.json', '../config/data.json')
        self._server = config.getoption('server') or self._data.servers.default
        self._project_name = self._data.report.project

        report_server = self._data.report.server_name
        user = self._data.report.username
        password = self._data.report.password
        config = Config({"server_name": report_server, "api_url": self._data.api_url})
        config["login"] = Config({"username": user, "password": password})
        self._client = APIClient(config)

        projects = self._client.get_projects()
        reporting_project = None
        for project in projects:
            if project.name == self._data.report.project:
                reporting_project = project
                break
        if reporting_project is None:
            raise Exception("Project {!r} for test reporting not found!".format(self._data.report.project))

        self._project = reporting_project

        statuses = self._client.get_statuses()
        for status in statuses:
            if status.name == 'skipped':
                Statuses.SKIPPED = status.id
            elif status.name == 'xfail':
                Statuses.XFAIL = status.id

    def pytest_collection_finish(self, session):
        # Called when test collection has finished. We can start the test run on the server.
        super().pytest_collection_finish(session)
        ids = []
        for item in session.items:
            these = get_case_ids(item)
            if not these:
                continue
            ids.extend(these)
        cases = self._client.get_cases(self._project.id)
        case_ids = {case.id for case in cases}

        # The case ids in this test run (from test names) that have a corresponding case in the project
        matching = [id for id in ids if id in case_ids]
        # Create a run just for matching tests
        date = datetime.now().strftime("%B %d %Y %H:%M:%S")
        run = Run(
            name='Test run ({}): Project: "{}": {}'.format(self._server, self._project_name, date),
            description="",
            include_all=False,
            case_ids=matching,
        )
        run = self._client.add_run(run, self._project.id)
        self._run = run
        self._matching = set(matching)

    def pytest_runtest_makereport(self, item, call):
        # This provides access to test markers in pytest_runtest_logreport
        report = _makereport(item, call)
        report.keywords = dict(item.keywords)
        return report

    def pytest_runtest_logreport(self, report):
        super().pytest_runtest_logreport(report)
        result = None
        test_name = report.location[2]
        message = "Test: {}\n\nOutcome: {!r}, When: {!r}".format(test_name, report.outcome, report.when)
        # Note: an elapsed of 0.00 will cause an error, so we use the bigger of duration and 0.01
        elapsed = '{:.2f}s'.format(max(report.duration, 0.01))
        case_ids = get_case_ids(report)
        if case_ids is None:
            # No case id or doesn't match the project
            return
        valid_ids = []
        for id in case_ids:
            if id in self._matching:
                valid_ids.append(id)
        if not valid_ids:
            # No ids from this project
            return

        if report.outcome != 'passed':
            message += '\n\n'
            message += str(report.longrepr)
            result = Result(
                status_id=Statuses.get(report.outcome),
                comment=message,
                elapsed=elapsed,
            )
        elif report.when == 'call':
            # We only record a pass for the test itself, fails are
            # also recorded in setup and teardown.
            result = Result(
                status_id=Statuses.PASSED,
                comment=message,
                elapsed=elapsed,
            )

        if result is not None:
            for case_id in valid_ids:
                self._client.add_result_for_case(result, self._run.id, case_id)

    def pytest_sessionfinish(self, exitstatus):
        super().pytest_sessionfinish(exitstatus)
        # self._client.close_run(self._run)

