from selenium.webdriver.common.by import By


class SectionLocators(object):

    addSectionInline = (By.ID, "addSectionInline")
    addSection = (By.ID, "addSection")
    addTestCase = (By.PARTIAL_LINK_TEXT, "Add Test Case")
    addSubsection = (By.LINK_TEXT, "Add Subsection")

    addCase = (By.LINK_TEXT, "Add Case")

    sectionColumn = "section-"
    sectionName = "sectionName-"
    sectionDesc = "sectionDesc-"
    sectionCount = "sectionCount-"
    sectionDelete = (By.XPATH, ".//div[@class='grid-title']/a[2]")
    sectionEdit = (By.XPATH, "//div[@class='grid-title']/a")
    sectionTitles = (By.CSS_SELECTOR, "div.grid-title > span.title")
    section_link = (By.CSS_SELECTOR, '.summary-title > a')

    # Add/Edit section
    editSectionName = (By.ID, "editSectionName")
    editSectionDescription = (By.ID, "editSectionDescription")
    editSectionSubmit = (By.ID, "editSectionSubmit")

    group = (By.CLASS_NAME, "group")
    testCase = (By.CLASS_NAME, "caseRow")
    group_container = (By.ID, "groups")
    titles = (By.CLASS_NAME, "title")
    drag_menu_copy = (By.ID, "sectionsDndCopy")
    drag_menu_move = (By.ID, "sectionsDndMove")

    @classmethod
    def section_title_name(cls, name):
        title_locator = "//span[@class='title' and contains(., '{}')]".format(name)
        return (By.XPATH, title_locator)

    @classmethod
    def textbox_in_section(cls, section_id):
        xpath = "//div[@id='section-{}']//input[@name='title']".format(section_id)
        return (By.XPATH, xpath)

    @classmethod
    def draggable_section(self, id):
        full_id = 'sectionNameAlt-{}'.format(id)
        return (By.ID, full_id)

    @classmethod
    def subsection_id(self, section_id):
        return (By.ID, "subsections-{}".format(section_id))