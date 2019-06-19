from selenium.webdriver.common.by import By


class ResultsLocators:

    add_result = (By.ID, "addResult")
    confirm_result = (By.ID, "addResultSubmit")
    add_result_status = (By.ID, "addResultStatus")
    attachment_dropzone = '#addResultDropzone'
    image_attachment_dropzone = '#attachmentDropzone'
    attachment_title = (By.CLASS_NAME, "attachment-title")
    attachment_description = (By.CLASS_NAME, "attachment-description")
    add_image_link = (By.XPATH, "//form[@id='addResultForm']//a[@class='link-tooltip'][2]")
    confirm_image_attachment = (By.ID, 'attachmentSubmit')

    edit_result = (By.XPATH, "//div[@class='change-meta']//a[contains(text(), 'Edit')]")
    comment_textarea = (By.ID, 'addResultComment')
    comment = (By.XPATH, "//div[@class='change-container']//div[@class='content markdown']/p")
    assign_to = (By.ID, "addResultAssignTo")
    assigned_to = (By.CLASS_NAME, "change-meta-item")

    @classmethod
    def expand_case_link(cls, title):
        xpath = "//div[@id='groups']//tr[contains(., '{}')]/td[position()=last()]/a".format(title)
        return (By.XPATH, xpath)

    @classmethod
    def case_row(cls, title):
        xpath = "//div[@id='groups']//tr[contains(., '{}')]".format(title)
        return (By.XPATH, xpath)

    @classmethod
    def case_status(cls, title):
        xpath = "//div[@id='groups']//tr[contains(., '{}')]/td[@class='js-status']/a".format(title)
        return (By.XPATH, xpath)
