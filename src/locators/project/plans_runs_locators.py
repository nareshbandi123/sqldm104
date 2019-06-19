from selenium.webdriver.common.by import By


class PlanRunLocators(object):

    # Run locators
    add_run = (By.LINK_TEXT, "Add Test Run")
    run_description = (By.ID, "description")
    assigned_to = (By.ID, 'assignedto_id')
    accept = (By.ID, "accept")
    add = (By.CLASS_NAME, "button-left")
    block_ui = (By.CLASS_NAME, "blockUI")
    include_specific_cases = (By.ID, "includeSpecific")
    close_run = (By.LINK_TEXT, "Close this test run")
    delete_run = (By.LINK_TEXT, "Delete this test run")
    run_description_link = (By.CLASS_NAME, "descriptionLink")
    run_edit_description = (By.ID, "editRunDescription")
    run_edit_submit = (By.ID, "editRunSubmit")
    run_overview = (By.ID, "content-inner")
    run_edit = (By.LINK_TEXT, "Edit")
    run_tooltip_links = (By.CLASS_NAME, 'link-tooltip')
    run_name = (By.PARTIAL_LINK_TEXT, "Test Run")
    run_title = (By.CLASS_NAME, "content-header-title")

    @classmethod
    def select_cases_by_section_name(cls, section_name):
        xpath = "//ul[@id='selectCasesSections']//li//a[contains(., '{}')]/preceding-sibling::input[@type='checkbox']".format(section_name)
        return (By.XPATH, xpath)

    # Plan locators
    add_plan = (By.LINK_TEXT, "Add Test Plan")
    add_run_in_plan = (By.LINK_TEXT, "Add Test Run(s)")
    plan_description = (By.ID, "description")
    plan_run_container = (By.CLASS_NAME, "detailsContainer")
    edit_run_assignee_in_plan = (By.LINK_TEXT, "change")
    run_add_assignee_in_plan = (By.ID, "selectUser")
    change_assignee_of_run = (By.LINK_TEXT, "change")
    run_assign_dialog = (By.ID, "selectUserDialog")
    plan_run_assigned = (By.CLASS_NAME, "assignedTo")
    run_select_cases = (By.LINK_TEXT, "change selection")
    run_test_case_rows = (By.CLASS_NAME, "row")
    case_assigned = (By.CLASS_NAME, "assigned")
    select_case_submit = (By.ID, "selectCasesSubmit")
    include_all_tests = (By.LINK_TEXT, "include all")
    select_case_dialog = (By.ID, "selectCasesDialog")
    select_milestone = (By.ID, "milestone_id")
    active_plans = (By.XPATH, "//div[@id='active']")
    plan_rows = (By.XPATH, ".//div[@class='table']/div[@class='row']")
    delete_plan = (By.LINK_TEXT, "Delete this test plan")
    close_plan = (By.LINK_TEXT, "Close this test plan")
    plan_select_cases = (By.LINK_TEXT, "select cases")
    review_changes = (By.ID, 'confirmDiffSubmit')

    rerun = (By.LINK_TEXT, "Rerun")
    rerun_form = (By.ID, "rerunForm")
    rerun_statuses = (By.ID, "rerunStatuses_control")

    test_run_title = (By.CLASS_NAME, 'summary-title')
    edit_run_name_link = (By.XPATH, "//div[contains(@class, 'summary-title')]//a")
    edit_run_name_textbox = (By.ID, 'editName')
    edit_run_name_dialog = (By.ID, 'editNameDialog')

    run_configurations = (By.LINK_TEXT, "Configurations")
    run_configurations_submit = (By.ID, 'addConfigSubmit')
    run_configurations_add_group = (By.LINK_TEXT, "Add Group")
    run_configurations_group_name = (By.ID, 'addConfigName')
    run_configurations_add_configuration = (By.LINK_TEXT, "Add Configuration")
    run_configurations_add_configuration_name = (By.ID, 'addConfigName')
    run_configurations_select_configurations_submit = (By.ID, 'selectConfigsSubmit')
    run_configurations_options = (By.XPATH, "//div[contains(@class, 'configurations')]//table//tr[contains(@class, 'row')]/td[2]")
    run_configuration_text = (By.CLASS_NAME, 'configuration')

    @classmethod
    def run_configurations_option_checkbox(cls, option):
        xpath = ".//tr[contains(., '{}')]/td/input[@type='checkbox']".format(option)
        return (By.XPATH, xpath)

    @classmethod
    def plan_name(cls, name):
        return (By.XPATH, ".//div[contains(.,'{}')]".format(name))

    @classmethod
    def plan_description(cls, description):
        return (By.XPATH, ".//p[contains(.,'{}')]".format(description))

    @classmethod
    def select_case_checkbox(cls, title):
        xpath = ".//div[@id='selectCasesGroup']//td[contains(., '{}')]/../td/input[@type='checkbox']".format(title)
        return (By.XPATH, xpath)

    confirm_select_cases = (By.ID, 'selectCasesSubmit')
    run_case_links = (By.XPATH, ".//div[@id='groups']//table//tr/td[3]/a")
