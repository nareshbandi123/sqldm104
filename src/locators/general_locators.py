from selenium.webdriver.common.by import By


class GeneralLocators(object):

    #Top header
    user_dropdown = (By.CLASS_NAME, "dropdownLink")
    user_my_settings = (By.LINK_TEXT, "My Settings")
    user_logout = (By.LINK_TEXT, "Logout")

    tab1 = (By.CLASS_NAME, "tab1")
    tab2 = (By.CLASS_NAME, "tab2")
    tab3 = (By.CLASS_NAME, "tab3")
    message_success = (By.CLASS_NAME, "message-success")
    message_hint = (By.CLASS_NAME, "message-hint")
    message_error = (By.CLASS_NAME, "message-error")
    message_help = (By.CLASS_NAME, "message-help")

    file_inputs = (By.CSS_SELECTOR, 'input.dz-hidden-input')

    # Confirmation Pop-Up
    dialog = (By.CLASS_NAME, "ui-dialog")
    dialog_confirm = (By.CLASS_NAME, "dialog-confirm")
    dialog_message = (By.CLASS_NAME, "dialog-message")
    confirm = (By.CLASS_NAME, "checkbox")
    delete_checkbox = (By.CLASS_NAME, "deleteCheckbox")

    description = (By.ID, "description")
    form = (By.ID, "form")
    name = (By.ID, "name")
    label = (By.ID, "label")
    edit_link = (By.LINK_TEXT, "Edit")

    # Buttons
    button_group = (By.CLASS_NAME, "button-group")
    add = (By.CLASS_NAME, "button-left")
    ok = (By.CLASS_NAME, "button-ok")
    cancel_btn = (By.CLASS_NAME, "button-cancel")
    submit_button = (By.CSS_SELECTOR, "button[type='submit']")
    checkbox = (By.CSS_SELECTOR, "input[type='checkbox']")
    edit = (By.CLASS_NAME, "button-edit")

    cancel = (By.LINK_TEXT, "Cancel")

    blockUI = (By.CLASS_NAME, "blockUI")
    busy = (By.CLASS_NAME, "busy")
    submit = (By.CLASS_NAME, "submit")
    sidebar = (By.ID, "sidebar")

    #Project
    test_cases = (By.LINK_TEXT, "Test Cases")
    title_test_cases = "Test Cases"
    runs_and_results = (By.LINK_TEXT, "Test Runs & Results")

    # Columns
    columns_dialog = (By.ID, "selectColumns-global")
    add_column = (By.ID, "selectColumnsAdd")
    column_items = (By.ID, "addColumnItems")
    add_column_submit = (By.ID, "addColumnSubmit")
    update_columns = (By.ID, "selectColumnsSubmit")
    columns_headers = (By.CSS_SELECTOR, "tr.header")
    group_block = (By.ID, "groups")

    @classmethod
    def column_header(cls, name):
        xpath = "//th[contains(., '{}')]".format(name)
        return (By.XPATH, xpath)

    @classmethod
    def column_row_by_name(cls, name):
        xpath = ".//tr[contains(., '{}')]".format(name)
        return (By.XPATH, xpath)
