import pytest
from src.test_cases.base_test import BaseTest
from src.common import read_config
from src.pages.administration.administration_page import AdministrationPage
from urllib.parse import urlparse


HOSTED = False
ENTERPRISE = False
TRIAL = False
if "hosted" == pytest.config.getoption('server'):
    HOSTED = True
if read_config('../config/enterprise.json').version == 'enterprise trial':
    ENTERPRISE = True
    TRIAL = True
elif read_config('../config/enterprise.json').version == 'enterprise':
    ENTERPRISE = True


@pytest.mark.skipif(not HOSTED, reason="TestRail is not Hosted")
class TestEnterprise(BaseTest):

    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.enterprise = read_config('../config/enterprise.json')

        # Set URLs
        cls.admin_overview_url = cls.data.server_name + cls.enterprise.urls.admin_overview_url
        cls.subscription_url = cls.data.server_name + cls.enterprise.urls.subscription_url

        # Initialize Page Object
        cls.administration = AdministrationPage(cls.driver)

    def setup_method(self):
        self.login.open_page(self.data.server_name)
        self.login.simple_login(self.data.login.username, self.data.login.password)

    def teardown_method(self):
        self.driver.delete_all_cookies()

    @pytest.mark.skipif(not(ENTERPRISE and TRIAL), reason="TestRail instance is not an Enterprise Cloud Trial")
    def test_check_enterprise_trial(self):
        instance_name = urlparse(self.data.server_name).netloc
        self.administration.open_page(self.admin_overview_url)
        self.administration.check_banner_text(banner_header=self.enterprise.messages.enterprise_trial.overview.banner_header,
                                              banner_body=self.enterprise.messages.enterprise_trial.overview.banner_body)
        self.administration.check_link(link_text=self.enterprise.links.contact_us_create_subscription.link_text,
                                       link=self.enterprise.links.contact_us_create_subscription.href)
        self.administration.check_link(link_text=self.enterprise.links.purchase_licenses.link_text,
                                       link=self.enterprise.links.purchase_licenses.href)
        self.administration.check_link(link_text=self.enterprise.links.switch_back_classic_testrail.link_text,
                                       link=self.enterprise.links.switch_back_classic_testrail.href)
        self.administration.check_link(link_text=self.enterprise.links.get_quote.link_text,
                                       link=self.enterprise.links.get_quote.href)
        self.administration.open_page(self.subscription_url)
        self.administration.check_banner_text(banner_header=self.enterprise.messages.enterprise_trial.banner_header +
                                              " (at "+instance_name+")",
                                              banner_body=self.enterprise.messages.enterprise_trial.banner_body)
        self.administration.check_link(link_text=self.enterprise.links.contact_us.link_text,
                                       link=self.enterprise.links.contact_us.href)

    @pytest.mark.skipif(not(ENTERPRISE and (not TRIAL)), reason="TestRail instance is not an Enterprise Standard")
    def test_check_enterprise_full(self):
        instance_name = urlparse(self.data.server_name).netloc
        self.administration.open_page(self.admin_overview_url)
        self.administration.check_banner_text(banner_header=self.enterprise.messages.enterprise_standard.overview.banner_header,
                                              banner_body=self.enterprise.messages.enterprise_standard.overview.banner_body)
        self.administration.check_link(link_text=self.enterprise.links.add_project.link_text,
                                       link=self.data.server_name + self.enterprise.links.add_project.href)
        self.administration.check_link(link_text=self.enterprise.links.add_disable_users.link_text,
                                       link=self.data.server_name + self.enterprise.links.add_disable_users.href)
        self.administration.check_link(link_text=self.enterprise.links.manage_subscription.link_text,
                                       link=self.data.server_name + self.enterprise.links.manage_subscription.href)
        self.administration.open_page(self.subscription_url)
        self.administration.check_banner_text(banner_header=self.enterprise.messages.enterprise_standard.banner_header +
                                              " (at " + instance_name + ")",
                                              banner_body=self.enterprise.messages.enterprise_standard.banner_body)
        self.administration.check_link(link_text=self.enterprise.links.contact_us.link_text,
                                       link=self.enterprise.links.contact_us.href)


if __name__ == "__main__":
    pytest.main()

