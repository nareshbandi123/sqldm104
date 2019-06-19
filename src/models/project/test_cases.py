from enum import Flag
import string
import random

class Section(object):

    def __init__(self, title, test_cases):
        self.title = title
        self.test_cases = test_cases

class TestResult(object):

    # Needed by pytest
    __test__ = False

    def __init__(self, __type__="TestResult", id=None, status=None, comment=None, assigned_to=None, version=None, elapsed=None, defects=None):
        self.__type__ = __type__
        self.id = id
        self.status = status
        self.comment = comment
        self.assigned_to = assigned_to
        self.version = version
        self.elapsed = elapsed
        self.defects = defects

class TestCase(object):

    # Needed by pytest
    __test__ = False

    def __init__(self, __type__="TestCase", title=None, template=None, type=None, priority=None, estimate=None, refs=None, custom_automation_type=None, preconditions=None, steps=None, expected_result=None, id=0, section=None):
        self.title = title + "".join(random.sample((string.ascii_uppercase+string.digits),6))
        self.template = template
        self.type = type
        self.priority = priority
        self.estimate = estimate
        self.refs = refs
        self.custom_automation_type = custom_automation_type
        self.preconditions = preconditions
        self.steps = steps
        self.expected_result = expected_result
        self.__type__ = __type__
        self.id = id
        self.section = section

class Template(Flag):

    EXPLORATORY_SESSION = 3
    TEST_CASE_STEPS = 2
    TEST_CASE_TEXT = 1

class Type(Flag):

    ACCEPTANCE = 1
    ACCESSIBILITY = 2
    AUTOMATED = 3
    COMPATIBILITY = 4
    DESTRUCTIVE = 5
    FUNCTIONAL = 6
    OTHER = 7
    PERFORMANCE = 8
    REGRESSION = 9
    SECURITY = 10
    SMOKE_SANITY = 11
    USABILITY = 12

class Priority(Flag):

    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1

class AutomationType(Flag):

    NONE = 0
    RANOREX = 1