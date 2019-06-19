from selenium.webdriver.common.by import By


class CustomizationsLocators:

    add_custom_field = (By.ID, "accept")
    add_custom_field_description = (By.ID, "description")
    add_custom_field_type = (By.ID, "type_id")
    add_custom_field_include_specific_templates = (By.ID, "includeSpecific")
    add_custom_field_exploratory_session = (By.ID, "template_ids-1")
    add_custom_field_testcase_steps = (By.ID, "template_ids-2")
    add_custom_field_testcase_text = (By.ID, "template_ids-3")

    add_priority_abbreviation = (By.ID, "short_name")

    add_ui_script = (By.CSS_SELECTOR, "button[type='submit']")
    add_ui_script_script = (By.ID, "config")
    add_ui_script_active = (By.ID, "is_active")
    add_ui_script_edit_save = (By.CSS_SELECTOR, "button[type='submit'].button-ok")

    edit_status_is_final = (By.ID, "is_final")
    edit_status_is_active = (By.ID, "is_active")
    edit_status_color_dark = (By.ID, "color_dark")
    edit_status_color_medium = (By.ID, "color_medium")
    edit_status_color_bright = (By.ID, "color_bright")

    add_template_field = (By.ID, "name")

    @classmethod
    def element_by_name(cls, name):
        xpath = "//span[contains(text(), '{}')]".format(name)
        return (By.XPATH, xpath)
