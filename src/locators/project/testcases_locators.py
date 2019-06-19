from selenium.webdriver.common.by import By


class TestCaseLocators(object):

    addCase_inline = (By.LINK_TEXT, "Add Case")
    addCase = (By.ID, "addCase")
    inlineSectionAddCase = "inlineSectionAddCase-"
    case_title_inline = (By.NAME, "title")
    case_confirm_inline = (By.CLASS_NAME, "submit")
    case_cancel_inline = (By.CLASS_NAME, "cancel")
    add_first_testcase = (By.LINK_TEXT, "Add Test Case")
    case_edit = (By.LINK_TEXT, "Edit")
    case_delete = (By.LINK_TEXT, "Delete this test case")

    column_id = (By.CLASS_NAME, "id")
    column_title = (By.CLASS_NAME, "title")

    # Test Case (add/edit)
    case_title = (By.ID, "title")
    case_section = (By.ID, "section_id")
    case_template = (By.ID, "template_id")
    case_type = (By.ID, "type_id")
    case_priority = (By.ID, "priority_id")
    case_estimate = (By.ID, "estimate")
    case_refs = (By.ID, "refs")
    case_custom_automation_type = (By.ID, "custom_automation_type")
    case_custom_preconds = (By.ID, "custom_preconds")
    case_custom_steps = (By.ID, "custom_steps")
    case_custom_expected = (By.ID, "custom_expected")
    case_accept = (By.ID, "accept")
    case_accept_and_next = (By.ID, "accept_and_next")
    case_title_edit = (By.ID, 'editCaseTitle')
    case_edit_title_submit = (By.ID, 'editCaseSubmit')
    case_attachments = (By.ID, "caseDropzone")
    attachment_description = (By.CSS_SELECTOR, "div.attachment-description")
    delete_attachment = (By.CLASS_NAME, 'attachmentImage')
    first_test_case = (By.CSS_SELECTOR, '.caseRow span.title')

    @classmethod
    def edit_title_image(self, title):
        xpath = ".//td/a[contains(., '{}')]/following-sibling::a".format(title)
        return (By.XPATH, xpath)

    @classmethod
    def edit_case_image(self, title):
        xpath = ".//td[contains(., '{}')]/following-sibling::td/a".format(title)
        return (By.XPATH, xpath)

    @classmethod
    def row_containing_testcase(self, case_name):
        xpath = ".//tr[contains(@class, 'caseRow') and contains(., '{}')]".format(case_name)
        return (By.XPATH, xpath)

    case_dragger = (By.CLASS_NAME, "caseDraggable")
    drag_menu_copy = (By.ID, "casesDndCopy")
    drag_menu_move = (By.ID, "casesDndMove")


    @classmethod
    def drag_target_from_section_id(self, section_id):
        xpath = ".//div[@id='section-{}']//tr[contains(@class, 'header') and contains(@class, 'sectionRow')]".format(section_id)
        return (By.XPATH, xpath)


    # Test Case (overview)
    overview_id = (By.CLASS_NAME, "content-header-id")
    overview_title = (By.CLASS_NAME, "content-header-title")
    overview_type = (By.ID, "cell_type_id")
    overview_priority = (By.ID, "cell_priority_id")
    overview_estimate = (By.ID, "cell_estimate")
    overview_refs = (By.ID, "cell_refs")
    overview_custom_automation_type = (By.ID, "cell_custom_automation_type")
    overview_custom_preconds = (By.XPATH, "//*[@id='content-inner']/div[4]/div/p")
    overview_custom_steps = (By.XPATH, "//*[@id='content-inner']/div[6]/div/p")
    overview_custom_expected = (By.XPATH, "//*[@id='content-inner']/div[8]/div/p")

    # Test Runs
    case_in_test_run = (By.CSS_SELECTOR, '[id^=row-] a.link-noline')
    cases_in_test_run = (By.CLASS_NAME, "row")
    case_add_result = (By.ID, 'addResult')
    case_add_result_dialog = (By.ID, 'addResultDialog')
    case_add_result_status = (By.ID, 'addResultStatus')
    case_add_result_comment = (By.ID, 'addResultComment')
    case_add_result_assigned_to = (By.ID, 'addResultAssignTo')
    case_add_result_version = (By.ID, 'addResultVersion')
    case_add_result_elapsed = (By.ID, 'addResultElapsed')
    case_add_result_defects = (By.ID, 'addResultDefects')
    case_add_result_submit = (By.ID, 'addResultSubmit')
    case_add_result_close = (By.ID, 'addResultClose')
    resultsContainer = (By.ID, "resultsContainer")
    change_container = (By.CLASS_NAME, "change-container")
    case_changes = (By.CLASS_NAME, "change")
    change_top = (By.CLASS_NAME, "top")
    case_edit_change = (By.LINK_TEXT, 'Edit')
    case_change = 'testChange-{}'
    case_edit_change_id = 'editChange-{}'
    case_column_comment = (By.CSS_SELECTOR, '.change-column-content .content p')
    case_push_defect_link = (By.ID, 'pushDefectLink')
    case_push_defect = (By.LINK_TEXT, 'Push')
    case_add_defect = (By.LINK_TEXT, 'Add')
    case_push_defect_dialog = (By.ID, 'pushDefectDialog')
    case_push_defect_dialog_title = (By.ID, 'ui-dialog-title-pushDefectDialog')
