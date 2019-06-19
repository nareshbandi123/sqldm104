import pytest
from src.test_cases.base_test import BaseTest
from src.common import read_config
from src.pages.project import runs_page
from src.pages.project import sections_page
from src.pages.project import suite_page
from src.pages.administration import project_page


class SectionsBase(BaseTest):

    single_repo = True

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.p = read_config('../config/project.json')
        cls.r = read_config('../config/runs.json')

        # Prepare page objects
        cls.section = sections_page.SectionsPage(cls.driver)
        cls.project = project_page.ProjectPage(cls.driver)
        cls.run = runs_page.RunsPage(cls.driver)

        # Perquisites for tests execution
        cls.prepare_for_testing()

    @classmethod
    def teardown_class(cls):
        cls.delete_prepared_data()
        super().teardown_class()

    def setup_method(self):
        self.section.open_page(self.data.server_name)

    @classmethod
    def prepare_for_testing(cls):
        add_project_url = (cls.data.server_name + cls.p.add_project_url)

        cls.section.open_page(cls.data.server_name)
        cls.login.simple_login(cls.data.login.username, cls.data.login.password)
        cls.project.open_page(add_project_url)
        if cls.single_repo:
            cls.project_id = cls.project.add_single_repo_project(cls.p.project_info.project_name)
        else:
            cls.project_id = cls.project.add_multi_repo_project(cls.p.project_info.project_name)

    @classmethod
    def delete_prepared_data(cls):
        projects_overview_url = (cls.data.server_name + cls.p.overview_url)
        message = cls.p.messages.msg_success_deleted_project

        cls.project.open_page(projects_overview_url)
        cls.project.delete_project(cls.p.project_info.project_name)
        cls.project.validate_success_message(message)


class TestSections(SectionsBase):

    single_repo = True

    @pytest.mark.testrail(id=202)
    @pytest.mark.dependency(name="test_add_first_section")
    def test_add_first_section(self):
        self.section.open_page(self.data.server_name + self.p.project_overview_url + self.project_id)
        suite_id = self.section.open_test_cases()
        self.section.add_first_section(self.p.sections.first_section)
        self.section.press_add_section_button()
        self.section.retrieve_id_from_group(self.p.sections.first_section)

    @pytest.mark.testrail(id=206)
    @pytest.mark.dependency(depends=["test_add_first_section"])
    def test_edit_section_name(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        new_name = self.p.sections.renamed_section
        self.section.open_page(project_overview_url)
        suite_id = self.section.open_test_cases()
        self.section.edit_first_section_name(new_name)
        self.section.verify_new_section_name(new_name)

    @pytest.mark.testrail(id=207)
    @pytest.mark.dependency(depends=["test_add_first_section"])
    def test_delete_section(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        section_name = self.p.sections.deleted_section
        section_description = self.p.sections.deleted_section_description

        self.section.open_page(project_overview_url)
        self.section.add_subsequent_section(section_name, section_description)
        self.section.assert_section_count(2)

        self.section.delete_section(section_name)
        self.section.assert_section_count(1)

    @pytest.mark.testrail(id=208)
    @pytest.mark.dependency(depends=["test_add_first_section"])
    def test_delete_section_with_cases(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        section_name = self.p.sections.deleted_section
        section_description = self.p.sections.deleted_section_description
        case_name = self.p.add.case_name

        self.section.open_page(project_overview_url)
        self.section.add_subsequent_section(section_name, section_description)

        self.section.add_case_to_section(section_name, case_name)
        self.section.delete_section(section_name)
        self.section.assert_section_count(1)

    @pytest.mark.testrail(id=212)
    @pytest.mark.dependency(depends=["test_add_first_section"])
    def test_delete_section_with_active_run(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        run_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        section_name = self.p.sections.section_name
        section_description = self.p.sections.section_description
        run_name = self.r.runs[0].name
        case_name = self.p.add.case_name

        self.section.open_page(project_overview_url)
        self.section.add_subsequent_section(section_name, section_description)
        self.section.add_case_to_section(section_name, case_name)

        self.section.open_page(run_overview_url)
        self.run.add_run_with_case_in_section(section_name, run_name)

        self.section.open_test_cases()
        self.section.delete_section(section_name)
        self.section.assert_section_count(1)

    @pytest.mark.testrail(id=213)
    @pytest.mark.dependency(depends=["test_add_first_section"])
    def test_delete_section_with_closed_and_active_runs(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        run_overview_url = self.data.server_name + self.r.overview_url + self.project_id
        section_name = self.p.sections.section_name
        section_description = self.p.sections.section_description
        case_name = self.p.add.case_name
        first_run_name = self.r.runs[0].name
        second_run_name = self.r.runs[1].name

        self.section.open_page(project_overview_url)
        self.section.add_subsequent_section(section_name, section_description)
        self.section.add_case_to_section(section_name, case_name)

        self.section.open_page(run_overview_url)
        self.run.add_run_with_case_in_section(section_name, first_run_name)

        self.run.open_page(run_overview_url)
        second_run_id = self.run.add_run_with_case_in_section(section_name, second_run_name)

        self.run.open_page(self.data.server_name + self.r.edit_url + second_run_id)
        self.run.close_run()

        self.section.open_test_cases()
        self.section.delete_section(section_name)
        self.section.assert_section_count(1)


class TestSectionsMultiRepo(SectionsBase):

    single_repo = False

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.suite = suite_page.SuitePage(cls.driver)

    @pytest.mark.testrail(id=211)
    @pytest.mark.run(order=1)
    def test_delete_section_from_suite(self):
        suite_name = self.p.suites.add[0].name
        suite_description = self.p.suites.add[0].description
        section_name = self.p.sections.first_section
        self.suite.open_page(self.data.server_name + self.p.suites.add_url + self.project_id)
        self.suite.add_data_to_suite(suite_name, suite_description)

        self.section.add_first_section(section_name)
        self.section.press_add_section_button()
        self.section.assert_section_count(1)

        self.section.delete_section(section_name)
        self.section.assert_section_count(0)


class TestSectionCopyMove(SectionsBase):

    single_repo = True

    def setup_method(self):
        super().setup_method()

        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        self.section.open_page(project_overview_url)
        self.section.open_test_cases()
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section
        case_name = self.p.add.case_name

        self.section.add_first_section(first_section)
        self.section.press_add_section_button()
        self.section.add_case_to_section(first_section, case_name)

        self.section.add_subsequent_section(second_section)
        self.section.add_case_to_section(second_section, case_name)

    def teardown_method(self):
        # Deleting sections deletes subsections, so we delete in a loop fetching
        # a fresh list of sections each time.
        while True:
            sections = self.section.fetch_section_names()
            if not sections:
                break
            next_section = sections.pop()
            self.section.delete_section(next_section)

    @pytest.mark.testrail(id=209)
    def test_c209_section_move(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        self.section.open_page(project_overview_url)
        self.section.open_test_cases()
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section

        self.section.move_section(first_section, second_section)
        self.section.verify_subsection(second_section, first_section)
        self.section.assert_section_count(2)

    @pytest.mark.testrail(id=210)
    def test_c210_section_copy(self):
        project_overview_url = self.data.server_name + self.p.project_overview_url + self.project_id
        self.section.open_page(project_overview_url)
        self.section.open_test_cases()
        first_section = self.p.sections.first_section
        second_section = self.p.sections.second_section

        self.section.copy_section(first_section, second_section)
        self.section.verify_subsection(second_section, first_section)
        self.section.assert_section_count(3)


if __name__ == "__main__":
    pytest.main()