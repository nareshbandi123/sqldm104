from selenium.webdriver.common.by import By


class SuiteLocator(object):

    # Overview
    empty_title = (By.CLASS_NAME, "empty-title")
    empty_body = (By.CLASS_NAME, "empty-body")

    suite_row = "suite-"
    suite_row_edit = (By.LINK_TEXT, "Edit")
    suite_row_run_test =(By.LINK_TEXT, "Run Test")
    suite_row_test_runs = (By.LINK_TEXT, "Test Runs")
    test_run_tab = (By.LINK_TEXT, 'Test Runs & Results')
    suite_row_summary_desc = (By.CLASS_NAME, "summary-description")

    # Add/edit Suite
    form = (By.ID, "form")
    suite_name = (By.ID, "name")
    suite_description = (By.ID, "description")
    add = (By.CLASS_NAME, "button-left")
    delete_suite = (By.CLASS_NAME, "text-delete")

    # Suite details
    suite_title = (By.CLASS_NAME, "content-header-title")
    success_message = (By.CLASS_NAME, "message-success")
    button_edit = (By.CLASS_NAME, "button-edit")
    group_block = (By.ID, "groups")

    # Runs
    run_edit_link = (By.LINK_TEXT, 'Edit')
    run_close_link = (By.LINK_TEXT, "Close this test run")
    apply_button = (By.XPATH, '//button[contains(text(), "Save Test Run"')

    # Columns
    columns_dialog = (By.ID, "selectColumns-global")
    add_column = (By.ID, "selectColumnsAdd")
    column_items = (By.ID, "addColumnItems")
    add_column_submit = (By.ID, "addColumnSubmit")
    update_columns = (By.ID, "selectColumnsSubmit")
    columns_headers = (By.CSS_SELECTOR, "tr.header.sectionRow")

    @classmethod
    def column_header(cls, name):
        xpath = "//th[contains(., '{}')]".format(name)
        return By.XPATH, xpath

    @classmethod
    def column_row_by_name(cls, name):
        xpath = ".//tr[contains(., '{}')]".format(name)
        return By.XPATH, xpath

