from setuptools import setup, find_packages

setup(
    name='testrail-automation',
    version='',
    packages=[
        'src',
        'src.pages',
        'src.pages.administration',
        'src.config',
        'src.models',
        'src.models.administration',
        'src.locators',
        'src.locators.project',
        'src.locators.administration',
        'src.test_cases',
        'src.test_cases.administration'
    ] + find_packages(),
    url='',
    license='',
    author='smlinaric',
    author_email='',
    description=''
)
