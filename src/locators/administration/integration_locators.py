from selenium.webdriver.common.by import By


class IntegrationLocators(object):

    defect_view_url = (By.ID, "defect_id_url")
    defect_add_url = (By.ID, "defect_add_url")
    defect_plugin = (By.ID, "defect_plugin")
    defect_config = (By.ID, "defect_config")
    add_user_variable = (By.LINK_TEXT, "Add User Variable")
    defectBusy = (By.ID, "defectBusy")
    accept = (By.ID, "accept")

    configure_jira_integration_btn = (By.LINK_TEXT, "Configure JIRA Integration")
    jira_integration_dialog = (By.ID, "jiraIntegrationDialog")
    jira_integration_address = (By.ID, "jiraIntegrationAddress")
    jira_integration_user = (By.ID, "jiraIntegrationUser")
    jira_integration_password = (By.ID, "jiraIntegrationPassword")
    jira_integration_submit = (By.ID, "jiraIntegrationSubmit")

    # Configure Variable
    userFieldForm = (By.ID, "userFieldForm")
    userFieldLabel = (By.ID, "userFieldLabel")
    userFieldDesc = (By.ID, "userFieldDesc")
    userFieldName = (By.ID, "userFieldName")
    userFieldType = (By.ID, "userFieldType")
    userFieldFallback = (By.ID, "userFieldFallback")
    userFieldPassword = (By.ID, "userFieldPassword")
    userFieldSubmit = (By.ID, "userFieldSubmit")

    userVariableColumn = "userField-"
    user_variables = (By.CSS_SELECTOR, "[id*='userField-']")
    userColumn_name = (By.CSS_SELECTOR, "td:nth-child(1)")
    userColumn_type = (By.CSS_SELECTOR, "td:nth-child(2)")
    userColumn_fallback = (By.CSS_SELECTOR, "td:nth-child(3)")
    userColumn_delete = (By.CSS_SELECTOR, "td:nth-child(5) > a")

    configure_jira_integration_btn = (By.LINK_TEXT, "Configure JIRA Integration")
    jira_integration_dialog = (By.ID, "jiraIntegrationDialog")
    jira_integration_address = (By.ID, "jiraIntegrationAddress")
    jira_integration_user = (By.ID, "jiraIntegrationUser")
    jira_integration_password = (By.ID, "jiraIntegrationPassword")
    jira_integration_submit = (By.ID, "jiraIntegrationSubmit")