import pytest
import json

from src.common import make_client
from src.helpers.api_client import APIError
from src.pages.api.api_page import APIPage
from src.common import read_config
from src.models.api.case import Case
from src.models.api.project import Project
from src.models.api.result import Result
from src.models.api.run import Run
from src.models.api.section import Section
from src.test_cases.base_test import APIBaseTest


@pytest.mark.api
class TestAttachmentsAPI(APIBaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.attachments = read_config('../config/attachments.json')

        cls.api_page = APIPage()
        cls.prepare_test_case()

    @classmethod
    def prepare_test_case(cls):
        cls.projects_created = []

        # add project
        added_project = Project(name="New Project", announcement="Some announcement",
                          show_announcement=False, suite_mode=1)
        project_created = cls.client.add_project(added_project)
        cls.projects_created.append(project_created)
        cls.project_new = project_created

        # add Section
        section = Section(name="Test Section")
        section_created = cls.client.add_section(section, project_created.id)
        cls.section = section_created

        # add test case
        case = Case(title="Test Case")
        cls.case = cls.client.add_case(case, section_created.id)

        # add test Run
        run = Run(name="Test Run")
        cls.run = cls.client.add_run(run, project_created.id)

    @pytest.mark.testrail(id=9367)
    def test_get_attachments_for_test_with_empty_response(self):
        tests = self.client.get_tests(self.run.id)
        self.api_page.assert_exists(tests)

        attachments = self.client.get_attachments_for_test(tests[0].id)
        self.api_page.assert_length(attachments, 0)
        self.api_page.check_response_is_empty_list(attachments)

    @pytest.mark.testrail(id=5687)
    @pytest.mark.run(name='test_add_attachment_to_result_success')
    def test_add_attachment_to_result_success(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        from pathlib import Path, PurePosixPath
        filename = PurePosixPath('../data/file.txt')
        # will be converted to valid one on Windows
        file_path = str(Path(filename))

        files = {'attachment': open(file_path, 'rb')}
        response = self.client.add_attachment_to_result(files, result_added.id)

        self.api_page.assert_field_in_object("attachment_id", response[0])

        attachment_content = self.client.get_attachment(response[0].attachment_id)
        file_content = open(file_path, 'rb').read().decode("utf-8")
        self.api_page.assert_equality(attachment_content, str(file_content))

    @pytest.mark.testrail(id=5688)
    @pytest.mark.run(name='test_add_attachment_to_result_for_case_success')
    def test_add_attachment_to_result_for_case_success(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        from pathlib import Path, PurePosixPath
        filename = PurePosixPath('../data/logo.png')
        # will be converted to valid one on Windows
        file_path = str(Path(filename))

        files = {'attachment': open(file_path, 'rb')}
        response = self.client.add_attachment_to_result_for_case(files, result_added.id, self.case.id)

        self.api_page.assert_field_in_object("attachment_id", response[0])

        attachment_content = self.client.get_attachment(response[0].attachment_id)
        self.api_page.assert_object(attachment_content)

    @pytest.mark.testrail(id=5691)
    @pytest.mark.run(depends=['test_add_attachment_to_result_for_case_success', 'test_add_attachment_to_result_success'])
    def test_get_results_check_attachment_id_in_response(self):
        tests = self.client.get_tests(self.run.id)

        results = self.client.get_results(tests[0].id)
        for result in results:
            self.api_page.assert_exists(result.attachment_ids)

    @pytest.mark.testrail(id=5694)
    @pytest.mark.run(depends=['test_add_attachment_to_result_for_case_success', 'test_add_attachment_to_result_success'])
    def test_get_results_for_case_check_attachment_id_in_response(self):
        results = self.client.get_results_for_case(self.run.id, self.case.id)

        for result in results:
            self.api_page.assert_exists(result.attachment_ids)

    @pytest.mark.testrail(id=5695)
    @pytest.mark.run(depends=['test_add_attachment_to_result_for_case_success', 'test_add_attachment_to_result_success'])
    def test_get_results_for_run_check_attachment_id_in_response(self):
        results = self.client.get_results_for_run(self.run.id)

        for result in results:
            self.api_page.assert_exists(result.attachment_ids)

    @pytest.mark.testrail(id=9368)
    def test_get_attachment_with_id_0(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachment, [0],
            400, self.attachments.errors.field_attachment_id_not_valid_attachment
        )

    @pytest.mark.testrail(id=9369)
    def test_get_non_existing_attachment(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachment, [99999],
            400, self.attachments.errors.field_attachment_id_not_valid_attachment
        )

    @pytest.mark.testrail(id=9370)
    def test_get_attachments_for_case_with_id_0(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachments_for_case, [0],
            400, self.attachments.errors.field_case_id_not_valid
        )

    @pytest.mark.testrail(id=9371)
    def test_get_attachments_for_case_unknown_case_ID(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachments_for_case, [99999],
            400, self.attachments.errors.field_case_id_not_valid
        )

    @pytest.mark.testrail(id=5696)
    @pytest.mark.run(depends=['test_add_attachment_to_result_for_case_success', 'test_add_attachment_to_result_success'])
    def test_get_attachments_for_case_success(self):
        attachments = self.client.get_attachments_for_case(self.case.id)
        self.api_page.assert_exists(attachments)
        self.api_page.assert_length(attachments, 1)
        self.api_page.validate_attachments(
            attachments,
            self.attachments.attachment_content.case1
        )

    @pytest.mark.testrail(id=9372)
    def test_get_attachments_for_case_check_authentication(self):
        valid_username = self.client.client.username
        try:
            self.client.client.username = "Anonymous"

            self.api_page.expect_to_raise_exception(
                self.client.get_attachments_for_case, [self.case.id],
                401,
                self.attachments.errors.authentication_failed,
                self.attachments.errors.maximum_number_of_failed_login_attempts_has_been_reached
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    @pytest.mark.testrail(id=9373)
    def test_get_attachments_for_test_with_id_0(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachments_for_test, [0],
            400, self.attachments.errors.field_test_id_not_valid
        )

    @pytest.mark.testrail(id=9374)
    def test_get_attachments_for_test_unknown_test_ID(self):
        self.api_page.expect_to_raise_exception(
            self.client.get_attachments_for_test, [99999],
            400, self.attachments.errors.field_test_id_not_valid
        )

    @pytest.mark.testrail(id=5697)
    def test_get_attachments_for_test_success(self):
        tests = self.client.get_tests(self.run.id)
        self.api_page.assert_exists(tests)

        attachments = self.client.get_attachments_for_test(tests[0].id)
        self.api_page.assert_length(attachments, 2)
        self.api_page.validate_attachments(
            attachments,
            self.attachments.attachment_content.case2
        )

    @pytest.mark.testrail(id=9375)
    @pytest.mark.run(depends="test_add_to_result")
    def test_delete_attachment_check_authentication(self):
        valid_username = self.client.client.username
        try:
            tests = self.client.get_tests(self.run.id)
            attachments = self.client.get_attachments_for_test(tests[0].id)
            self.api_page.assert_exists(attachments)

            attachment_id = attachments[0]['id']

            self.client.client.username = "Anonymous"
            self.api_page.expect_to_raise_exception(
                self.client.delete_attachment, [attachment_id],
                401,
                self.attachments.errors.authentication_failed,
                self.attachments.errors.maximum_number_of_failed_login_attempts_has_been_reached
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    @pytest.mark.testrail(id=9376)
    @pytest.mark.run(depends="test_add_to_result")
    def test_get_attachments_for_test_check_authentication(self):
        valid_username = self.client.client.username
        try:
            tests = self.client.get_tests(self.run.id)
            self.client.client.username = "Anonymous"
            self.api_page.expect_to_raise_exception(
                self.client.get_attachments_for_test, [tests[0].id],
                401,
                self.attachments.errors.authentication_failed,
                self.attachments.errors.maximum_number_of_failed_login_attempts_has_been_reached
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    @pytest.mark.testrail(id=9377)
    @pytest.mark.run(depends="test_add_to_result")
    def test_get_attachment_check_authentication(self):
        valid_username = self.client.client.username
        try:
            tests = self.client.get_tests(self.run.id)
            self.client.client.username = "Anonymous"
            self.api_page.expect_to_raise_exception(
                self.client.get_attachment, [1],
                401,
                self.attachments.errors.authentication_failed,
                self.attachments.errors.maximum_number_of_failed_login_attempts_has_been_reached
            )
        finally:
            # restore valid auth user
            self.client.client.username = valid_username

    @pytest.mark.testrail(id=5710)
    @pytest.mark.run(depends="test_add_to_result")
    def test_delete_attachment_success(self):
        tests = self.client.get_tests(self.run.id)
        attachments = self.client.get_attachments_for_test(tests[0].id)
        self.api_page.assert_exists(attachments)

        attachment_id = attachments[0]['id']
        resp = self.client.delete_attachment(attachment_id)
        self.api_page.check_response_is_empty(resp)

        attachments = self.client.get_attachments_for_test(tests[0].id)
        for attachment in attachments:
            self.api_page.assert_not_equal(attachment['id'], attachment_id)

    @pytest.mark.testrail(id=9378)
    def test_delete_attachment_invalid_attachment(self):
        self.api_page.expect_to_raise_exception(
            self.client.delete_attachment, ["ABC"],
            400, self.attachments.errors.field_attachment_id_not_valid
        )

    @pytest.mark.testrail(id=9379)
    def test_delete_attachment_non_existing_attachment(self):
        self.api_page.expect_to_raise_exception(
            self.client.delete_attachment, [99999],
            400, self.attachments.errors.field_attachment_id_not_valid_attachment
        )

    @pytest.mark.testrail(id=9380)
    def test_delete_attachment_with_id_0(self):
        self.api_page.expect_to_raise_exception(
            self.client.delete_attachment, [0],
            400, self.attachments.errors.field_attachment_id_not_valid_attachment
        )

    @pytest.mark.testrail(id=9381)
    @pytest.mark.run(depends="test_delete_attachment_success")
    def test_get_attachments_for_case_without_attachments(self):
        attachments = self.client.get_attachments_for_case(self.case.id)
        self.api_page.check_response_is_empty_list(attachments)

    @pytest.mark.testrail(id=5688)
    @pytest.mark.parametrize('attachment_file, exp_response_code', [
        ("file.txt,report.json,disallowed.js,disallowed.sql", 200),
    ])
    def test_add_attachment_to_result_for_case_multiple_success(self, attachment_file, exp_response_code):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        attachment_files_list = attachment_file.split(",")
        for file in attachment_files_list:
            response, act_response_code = self.client.add_attachment_to_result_for_case(
                {'attachment': self.api_page.generate_attachment(f'{file}')}, result_added.id, self.case.id)
            self.api_page.assert_equality(exp_response_code, act_response_code)
            self.api_page.assert_field_in_object("attachment_id", response)

        attachment_content = self.client.get_attachments_for_case(self.case.id)
        self.api_page.assert_attachment_content_names_in_attachment_file(attachment_content, attachment_file)

    @pytest.mark.testrail(id=5687)
    @pytest.mark.parametrize('attachment_file, exp_response_code', [
        # ('logo.png', 200),
        # ('mypic.jpg', 200),
        # jpg/png are not able to be checked
        ('report.json', 200),
        ('report.xml', 200),
        ('file.txt', 200),
        ('disallowed.js', 200),
        ('disallowed.sql', 200),
        ('disallowed.exe', 200),
        ('disallowed.php', 200),
    ])
    def test_add_attachment_to_result_multiple_success(self, attachment_file, exp_response_code):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        response, act_response_code = self.client.add_attachment_to_result(
            {'attachment': self.api_page.generate_attachment(f'{attachment_file}')}, result_added.id)
        self.api_page.assert_equality(exp_response_code, act_response_code)
        self.api_page.assert_field_in_object("attachment_id", response)

        attachment_content = self.client.get_attachment(response.attachment_id)
        if 'json' in attachment_file:
                file_content = self.api_page.generate_attachment(f'{attachment_file}').read().decode("utf-8")
                self.api_page.assert_equality(json.dumps(attachment_content), file_content)
        else:
            file_content = self.api_page.generate_attachment(f'{attachment_file}').read().decode("utf-8")
            self.api_page.assert_equality(attachment_content, str(file_content))

    @pytest.mark.skip(reason='old functionality')
    @pytest.mark.parametrize('attachment_file, exp_response_code', [
        ('disallowed.js', 400),
        ('disallowed.sql', 400),
        ('disallowed.exe', 400),
        ('disallowed.php', 400),
    ])
    def test_add_attachment_to_result_invalid_attachment(self, attachment_file, exp_response_code):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        attachment = self.api_page.generate_attachment(f'{attachment_file}')

        response, act_response_code = self.client.add_attachment_to_result({'attachment': attachment}, result_added.id, check_errors=False)
        self.api_page.assert_equality(exp_response_code, act_response_code)
        self.api_page.assert_equality(response['error'], self.attachments.errors.restricted_to_upload_malicious_file)

    @pytest.mark.testrail(id=5688)
    @pytest.mark.parametrize('attachment_file, exp_response_code', [
        # ('logo.png', 200),
        # ('mypic.jpg', 200),
        # jpg/png are not able to be checked
        ('report.json', 200),
        ('report.xml', 200),
        ('file.txt', 200),
        ('disallowed.js', 200),
        ('disallowed.sql', 200),
        ('disallowed.exe', 200),
        ('disallowed.php', 200),
    ])
    def test_add_attachment_to_result_for_case_success_valid_file_extensions(self, attachment_file, exp_response_code):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        response, act_response_code = self.client.add_attachment_to_result_for_case(
            {'attachment': self.api_page.generate_attachment(f'{attachment_file}')}, result_added.id, self.case.id)

        self.api_page.assert_equality(exp_response_code, act_response_code)

        self.api_page.assert_field_in_object("attachment_id", response)

        attachment_content = self.client.get_attachment(response.attachment_id)

        if 'json' in attachment_file:
                file_content = self.api_page.generate_attachment(f'{attachment_file}').read().decode("utf-8")
                self.api_page.assert_equality(json.dumps(attachment_content), file_content)
        else:
            file_content = self.api_page.generate_attachment(f'{attachment_file}').read().decode("utf-8")
            self.api_page.assert_equality(attachment_content, str(file_content))

    @pytest.mark.skip(reason='old functionality')
    @pytest.mark.parametrize('attachment_file, exp_response_code', [
        ('disallowed.js', 400),
        ('disallowed.sql', 400),
        ('disallowed.exe', 400),
        ('disallowed.php', 400),
    ])
    def test_add_attachment_to_result_for_case_invalid_attachment(self, attachment_file, exp_response_code):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        attachment = self.api_page.generate_attachment(f'{attachment_file}')

        response, act_response_code = self.client.add_attachment_to_result_for_case({'attachment': attachment}, result_added.id, self.case.id, check_errors=False)
        self.api_page.assert_equality(exp_response_code, act_response_code)
        self.api_page.assert_equality(response['error'], self.attachments.errors.restricted_to_upload_malicious_file)

    @pytest.mark.skip(reason='old functionality')
    def test_add_attachment_to_result_with_invalid_attachments(self):
        result = Result(comment="comment in result", elapsed="2m", version="2")
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        attachment1 = self.api_page.generate_attachment('disallowed.js')
        attachment2 = self.api_page.generate_attachment('disallowed.sql')

        response, act_response_code = self.client.add_attachment_to_result_for_case({'attachment': attachment1}, result_added.id, self.case.id, check_errors=False)
        self.api_page.assert_equality(400, act_response_code)
        self.api_page.assert_equality(response['error'], self.attachments.errors.restricted_to_upload_malicious_file)

        response, act_response_code = self.client.add_attachment_to_result_for_case({'attachment': attachment2}, result_added.id, self.case.id, check_errors=False)
        self.api_page.assert_equality(400, act_response_code)
        self.api_page.assert_equality(response['error'], self.attachments.errors.restricted_to_upload_malicious_file)

    @pytest.mark.testrail(id=9382)
    def test_add_attachment_to_result_without_attachment(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        response, response_code = self.client.add_attachment_to_result(None, result_added.id, check_errors=False)
        self.api_page.assert_equality(response_code, 400)

    @pytest.mark.testrail(id=9383)
    def test_add_attachment_to_result_for_case_without_attachment(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        response, act_response_code = self.client.add_attachment_to_result_for_case(None, result_added.id, self.case.id, check_errors=False)
        self.api_page.assert_equality(act_response_code, 400)

    def test_add_attachment_to_result_no_access(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        with pytest.raises(APIError) as e_info:
            user = self.add_user_with_project_permissions(project_id=self.project_new.id, permission="No Access")
            make_client(user.email_address, user.password).add_attachment_to_result(
                {'attachment': 'content'},
                result_added.id
            )

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'The requested project does not exist or you do not have the permissions to access it.'

    def test_add_attachment_to_result_for_case_no_access(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        with pytest.raises(APIError) as e_info:
            user = self.add_user_with_project_permissions(project_id=self.project_new.id, permission="No Access")
            make_client(user.email_address, user.password).add_attachment_to_result_for_case(
                {'attachment': 'content'},
                result_added.id,
                self.case.id
            )

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'The requested project does not exist or you do not have the permissions to access it.'

    def test_add_attachment_to_result_read_only(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        with pytest.raises(APIError) as e_info:
            user = self.add_user_with_permissions(permission="Read-only")
            make_client(user.email_address, user.password).add_attachment_to_result(
                {'attachment': 'content'},
                result_added.id
            )

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to add attachments (insufficient permissions).'

    def test_add_attachment_to_result_for_case_read_only(self):
        result = Result(comment="comment in result", elapsed="2m", version="2", )
        result_added = self.client.add_result_for_case(result, self.run.id, self.case.id)

        with pytest.raises(APIError) as e_info:
            user = self.add_user_with_permissions(permission="Read-only")
            make_client(user.email_address, user.password).add_attachment_to_result_for_case(
                {'attachment': 'content'},
                result_added.id,
                self.case.id
            )

        error = e_info.value
        assert error.status_code == 403
        assert error.error == 'You are not allowed to add attachments (insufficient permissions).'
