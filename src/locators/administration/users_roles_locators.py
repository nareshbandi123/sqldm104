from selenium.webdriver.common.by import By


class UsersRolesLocator(object):
    # General Overview
    tab1 = (By.CLASS_NAME, "tab1")
    tab2 = (By.CLASS_NAME, "tab2")
    tab3 = (By.CLASS_NAME, "tab3")
    message_success = (By.CLASS_NAME, "message-success")
    message_hint = (By.CLASS_NAME, "message-hint")
    message_error = (By.CLASS_NAME, "message-error")

    edit_bulk_dropdown = (By.ID, "bulk-toolbar")
    edit_selected = (By.LINK_TEXT, "Edit selected")
    edit_all = (By.LINK_TEXT, "Edit all in view")
    add_user_button = (By.LINK_TEXT, "Add User")
    filter_users = (By.ID, "showSelection")

    # Users table
    users = (By.CSS_SELECTOR, "tr[id*='user-']")
    checkbox_selectall = (By.ID, "selectall")
    cn_users_row = "user-"
    cn_users_full_name = "user-name-col"
    checkbox_user = (By.CLASS_NAME, "source")
    users_name = (By.CLASS_NAME, "name")
    users_email = (By.ID, "email")
    users_login_type = (By.CLASS_NAME, "logintype")
    users_last_active = (By.CLASS_NAME, "last-active")
    users_full_name = (By.CLASS_NAME, "user-name-col")
    users_email_address = (By.CLASS_NAME, "email")
    users_status = (By.CLASS_NAME, "active")
    users_role = (By.CLASS_NAME, "role")

    # Add/Edit User
    # User tab
    full_name = (By.ID, "name")  # also used in group and role
    email_address = (By.ID, "email")
    email_notifications = (By.ID, "notifications")
    language = (By.ID, "language")
    locale = (By.ID, "locale")
    time_zone = (By.ID, "timezone")
    sso_checkbox = (By.ID, "is_sso_enabled")
    invite_user = (By.ID, "invite_yes")
    manually_specify_psw = (By.ID, "invite_no")
    add_user = (By.CLASS_NAME, "button-ok")
    cancel = (By.CLASS_NAME, "button-cancel")
    password = (By.ID, "password")
    confirm_password = (By.ID, "confirm")
    # Access tab
    role_id = (By.ID, "role_id")
    last_activity = (By.ID, "last_activity")
    is_active = (By.ID, "is_active")
    is_admin = (By.ID, "is_admin")
    # Side tab
    forget_user = (By.LINK_TEXT, "Forget this user")
    force_password_change = (By.LINK_TEXT, "Force Password Change")

    # Multiple Users
    multiple_users = (By.ID, "users")
    preview = (By.CLASS_NAME, "grid")
    user_preview = "userPreview-"
    user_dialog = "userDialog-"
    user_preview_id = (By.CLASS_NAME, "id")
    user_preview_name = (By.XPATH, "td[2]")
    user_preview_email = (By.XPATH, "td[3]")
    user_preview_new = (By.CLASS_NAME, "text-success")
    user_preview_error = (By.CLASS_NAME, "text-error")

    # Groups
    group_names = (By.CLASS_NAME, "checkbox-list-input")
    id_group_row = "group-"

    add_group = (By.CLASS_NAME, "button-left")
    group_name = (By.ID, "name")
    group_users = (By.CLASS_NAME, "checkbox-list-inner")

    # Roles
    is_default_role = (By.ID, "is_default")
    permission_attachments_addedit = (By.ID, "attachments_addedit")
    permission_attachments_delete = (By.ID, "attachments_delete")
    permission_cases_addedit = (By.ID, "cases_addedit")
    permission_cases_delete = (By.ID, "cases_delete")
    permission_configs_addedit = (By.ID, "configs_addedit")
    permission_configs_delete = (By.ID, "configs_delete")
    permission_milestones_addedit = (By.ID, "milestones_addedit")
    permission_milestones_delete = (By.ID, "milestones_delete")
    permission_runs_addedit = (By.ID, "runs_addedit")
    # runs_delete and runs_closed_delete have duplicate IDs ("runs_delete")
    # so we use XPATH to locate by value instead
    permission_runs_delete = (By.XPATH, "//input[@value='128']")
    permission_runs_close = (By.ID, "runs_close")
    permission_runs_closed_delete = (By.XPATH, "//input[@value='262144']")
    permission_reports_addedit = (By.ID, "reports_addedit")
    permission_reports_delete = (By.ID, "reports_delete")
    permission_reports_jobs_addedit = (By.ID, "report_jobs_addedit")
    permission_reports_jobs_delete = (By.ID, "report_jobs_delete")
    permission_suites_addedit = (By.ID, "suites_addedit")
    permission_suites_delete = (By.ID, "suites_delete")
    permission_results_addedit = (By.ID, "results_addedit")
    permission_results_modify = (By.ID, "results_modify")

    add_role = (By.CLASS_NAME, "button-left")

    # Users Table
    bulk_user_delete = (By.NAME, "delete")

    # Bulk update users
    bulk_email_notifications = (By.NAME, "notifications")
    bulk_language = (By.NAME, "language")
    bulk_locale = (By.NAME, "locale")
    bulk_timezone = (By.NAME, "timezone")
    bulk_sso = (By.NAME, "is_sso_enabled")
    bulk_role = (By.NAME, "role_id")
    bulk_status = (By.NAME, "is_active")
    bulk_is_administrator = (By.NAME, "is_admin")
    groups_various = (By.XPATH, "//label[@name='groups[]']//following::span[1]")

    bulk_groups = (By.ID, "groups")
    bulk_select_all_groups = (By.ID, "allcheckbox")
    bulk_select_no_groups = (By.ID, "nonecheckbox")

    # Review Changes Modal
    review_modal = (By.CLASS_NAME, "modal-content")
    review_modal_button_ok = (By.ID, "review_submit")
    # Save changes / Cancel changes.
    bulk_save_changes = (By.ID, "review_change_button")
    bulk_cancel = (By.LINK_TEXT, "Cancel")

    # Confirmation Pop-Up
    confirm = (By.CLASS_NAME, "checkbox")
    add_users_form = (By.ID, "addUsersForm")
    add_users_confirm = (By.ID, "addUsersReturn")
    add_users_disabled = (By.ID, "addUsersReturnDisabled")
    add_users_table = (By.ID, "addUsersTable")
    add_users_message_success = (By.ID, "addUsersSuccess")

    @staticmethod
    def get_user_xpath(i) -> str:
        return '//span[contains(text(),"'+i+'")]'

    @staticmethod
    def get_role_by_name(role_name):
        return "//div[contains(@class,'tab3')]//span[contains(@class,'name') and contains(text(), '" + role_name + "')]"
