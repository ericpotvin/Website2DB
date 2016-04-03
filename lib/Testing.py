""" Test a generated json file
"""
import json

from lib.Sites import __classmap__, Sites
from Files import FILE_EXT_JSON, Files


class Testing(Sites):
    """ Testing Class
    """
    TEST_TYPE_STR = 1
    TEST_TYPE_DICT = 2
    TEST_TYPE_NUM = 3

    def __init__(self, name, debug):
        """ init
            :param name: The site name
            :param debug: Debug mode
        """
        super(Testing, self).__init__(name, debug)

    def test_json(self):
        """ Test jSon files
        """

        if self.debug:
            print "  Testing SQL: %s" % self.test_file + FILE_EXT_JSON
            file_list = [self.test_file + FILE_EXT_JSON]
        else:
            file_list = Files.get_file_list(self.generated_folder)

        for json_file in file_list:

            if not Files.file_exists(self.generated_folder + json_file):
                continue

            data = json.load(open(self.generated_folder + json_file))

            test_data = __classmap__[self.name].get_test_data()

            ret = self._check_json(data, test_data)

            if isinstance(ret, str):
                print "  ** TEST Failed for: %s => %s" % (json_file, ret)

    @staticmethod
    def _check_json(data, tests):
        """ Check the json file
            :param data: the json data
            :param tests: The tests to perform
        """

        for test in tests:

            # Make sure the element exists
            if test['name'] not in data:
                return "no %s" % test['name']

            if test["type"] == Testing.TEST_TYPE_STR:
                if not Testing._test_str(data[test["name"]]):
                    return "The string for %s is invalid" % test["name"]

            elif test["type"] == Testing.TEST_TYPE_DICT:
                if not Testing._test_dict(data[test["name"]]):
                    return "The dictionary for %s is invalid" % test["name"]

            elif test["type"] == Testing.TEST_TYPE_NUM:
                if not Testing._test_num(data[test["name"]]):
                    return "The number for %s is invalid" % test["name"]

        return True

    @staticmethod
    def _test_str(text):
        """ Test if the string is valid
            :param text: The string
        """
        return len(text) > 0

    @staticmethod
    def _test_dict(dic):
        """ Test is a dictionary is valid
            :param dic: the dictionary
        """

        if not isinstance(dic, dict):
            return False
        if len(dic) == 0:
            return False
        return True

    @staticmethod
    def _test_num(text):
        """ Test if the string is a valid number
            :param text: the string
        """
        text = str(text)
        if not Testing._test_str(text):
            return False
        if not str(text).isdigit():
            return False
        return True
