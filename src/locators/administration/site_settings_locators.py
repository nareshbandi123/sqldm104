from selenium.webdriver.common.by import By
from src.locators.general_locators import GeneralLocators


class Sitesettings_locators(object):

    # Site Settings Page Locator
    site_settings_button = (By.LINK_TEXT, "Site Settings")

    # Login Tab
    login_tab = (By.LINK_TEXT, "Login")

    api_tab = (By.LINK_TEXT, "API")
    api_enable_checkbox = (By.ID, "apiv2_enabled")

    login_textbox = (By.NAME, "login_text")
    sso_tab = (By.LINK_TEXT, "SSO")
    sso_switch_indicator = (By.ID, "saml_integration")
    sso_switch = (By.CLASS_NAME, "switch")

    # SAML 2.0 fields
    saml_entity_id = (By.NAME, "testrail_entity_id")
    saml_sso_url = (By.NAME, "sso_url")
    saml_idp_sso_url = (By.NAME, "idp_sso_url")
    saml_idp_issuer_url = (By.NAME, "idp_issuer_url")
    saml_authentication_fallback = (By.NAME, "is_fallback_enabled")
    saml_create_account_first_login = (By.NAME, "create_account_on_first_login")
    saml_ssl_certificate_upload = (By.ID, "input-file")
    certificate_upload_area = (By.ID, "attachmentDropzone")
    saml_ssl_certificate = (By.ID, "settings_idp_certificate")
    file_upload = (By.CLASS_NAME, "dz-hidden-input")

    # Okta Login page locators
    okta_username = (By.NAME, "username")
    okta_password = (By.NAME, "password")
    okta_login_button = (By.ID, "okta-signin-submit")
    okta_applications = (By.CLASS_NAME, "app-button-name")

    # Upload Certificate Modal
    file_dropzone = (By.ID, "attachmentDropzone")
    upload_button = (By.ID, "attachmentSubmit")
    upload_modal_cancel_button = (By.ID, "button-cancel")
    invalid_certificate_dialog = (By.CSS_SELECTOR, "[aria-labelledby=ui-dialog-title-messageDialog]")

    test_connection = (By.ID, "test-connection")
    save_settings = (By.NAME, "submit")

    @staticmethod
    def get_app_locator(app_name) -> str:
        return '//p[@oldtitle="' + app_name + '"]//preceding::a[1]'

    # Auditing
    auditing_tab = (By.ID, "auditing_tab")
    auditing_log_tab = (By.ID, "auditing_log_tab")
    auditing_configuration_tab = (By.ID, "auditing_configuration_tab")
    audit_level = (By.ID, "audit_level")
    audit_rows_per_page = (By.ID, "audit_rows_per_page")
    audit_number_of_records = (By.ID, "audit_number_of_records")
    audit_custom_number_of_records = (By.ID, "audit_custom_number_of_records")
    audit_number_of_days = (By.ID, "audit_number_of_days")
    audit_custom_number_of_days = (By.ID, "audit_custom_number_of_days")
    audit_grid = (By.ID, "auditGrid")
    audit_grid_row = (By.CSS_SELECTOR, "tr")
    audit_row_column = (By.CSS_SELECTOR, "td")
    audit_download_tooltip = (By.ID, 'tooltip')
    audit_write_logs = (By.ID, 'audit_write_logs')

    # Audit Log Filtering
    audit_filter_by_change = (By.ID, "filterByChange")
    audit_filter_by_info = (By.ID, "filterByInfo")
    audit_filter_logs_action = (By.ID, "filter-logs\\:action")
    audit_filter_logs_author = (By.ID, "filter-logs\\:author")
    audit_filter_logs_date = (By.ID, "filter-logs\\:date")
    audit_filter_logs_entity_name = (By.ID, "filter-logs\\:entity_name")
    audit_filter_logs_entity_type = (By.ID, "filter-logs\\:entity_type")
    audit_filter_logs_mode = (By.ID, "filter-logs\\:mode")
    audit_filter_link = (By.CSS_SELECTOR, "a.link-noline")
    audit_filter_select = (By.CSS_SELECTOR, ".filterContent select")
    audit_filter_text_input_field = (By.CSS_SELECTOR, "input[type=text]")
    audit_filter_date_custom_from = (By.CSS_SELECTOR, ".custom_from")
    audit_filter_date_custom_to = (By.CSS_SELECTOR, ".custom_to")
    audit_filter_filter_mode_and = (By.ID, "filterMode_and")
    audit_filter_filter_mode_or = (By.ID, "filterMode_or")
    audit_filter_reset = (By.ID, "filterLogsReset")
    audit_filter_apply = (By.ID, "filterLogsApply")
    audit_filter_pagination_loader = (By.ID, "auditlogsPaginationBusy")
    audit_filter_logs_bubble = (By.ID, "filterLogsBubble")
    audit_filter_logs_busy = (By.CSS_SELECTOR, "#filterBy span.busy")

    # Backups
    restore_backup_btn = (By.ID, "restore-backup")
    restore_backup_banner = (By.ID, "restoreBackup")
    restore_backup_hour = (By.ID, "backup_hour")
    restore_backup_last_backup_time = (By.NAME, "last_backup_time")
    restore_backup_dialog = (By.ID, "backupDialog")
    restore_backup_delete_checkbox = (By.ID, "delete_checkbox")
    restore_backup_confirm_restore = (By.ID, "confirm_restore")
    backup_cancel = (By.ID, "cancel_restoration_message_link")
    backup_form_save_btn = (By.ID, "settings_save")

    # License
    license_key_div = (By.ID, 'license')
    license_key_textarea = (By.ID, 'license_key')
