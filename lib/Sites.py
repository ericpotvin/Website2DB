""" Sites class
"""
from os import path
from Files import Files
from lib import DOWNLOAD_PATH, GENERATED_PATH, IMAGE_PATH, SITE_PATH
from lib import ERROR_ACTION_INVALID, ERROR_SITE, IMAGE_SEP
from lib import ACTION_CONVERT, ACTION_CREATE_DB, ACTION_DELETE, \
    ACTION_DOWNLOAD, ACTION_DOWNLOAD_IMAGE, ACTION_TEST

DEBUG = 1
__classmap__ = {}


class Sites(object):
    """ Sites object
    """
    generated_folder = None
    download_folder = None
    image_folder = None

    def __init__(self, name, debug):
        self.debug = debug
        self.name = name

        self.base_url = __classmap__[name].BASE_URL
        self.test_file = __classmap__[name].TEST_FILE

        self.download_folder = DOWNLOAD_PATH + self.name + "/"
        self.generated_folder = GENERATED_PATH + self.name + "/"
        self.image_folder = IMAGE_PATH + self.name + "/"

        Files.create_folder(self.download_folder)
        Files.create_folder(self.generated_folder)
        Files.create_folder(self.image_folder)

        if self.debug:
            print "DEBUG Mode Enabled"

    @staticmethod
    def execute(site, action):
        """ Execute the action for a site
            Steps:
                1) download
                2) convert
                3) test
                4) create_db
                5) download_images
                6) delete
            :param site: the site
            :param action: the action
        """

        # check actions
        if not Sites.valid_action(action):
            print ERROR_ACTION_INVALID
            return

        if not Sites.is_valid_site(site):
            print ERROR_SITE
            return

        if site == "blueapron":
            from websites.blueapron import BlueApron

            __classmap__["blueapron"] = BlueApron

        if action == ACTION_DOWNLOAD:
            from lib.DownloadSite import DownloadSite
            download = DownloadSite(site, DEBUG)
            download.download()

        elif action == ACTION_CONVERT:
            from lib.Convert import Convert
            convert = Convert(site, DEBUG)
            convert.convert_html()

        elif action == ACTION_TEST:
            from lib.Testing import Testing
            testing = Testing(site, DEBUG)
            testing.test_json()

        elif action == ACTION_DOWNLOAD_IMAGE:
            from lib.DownloadSite import DownloadSite
            download = DownloadSite(site, DEBUG)
            download.download_images()

        elif action == ACTION_CREATE_DB:
            from lib.DB import DB
            database = DB(site, DEBUG)
            database.create()

        elif action == ACTION_DELETE:
            from lib.Cache import Cache
            cache = Cache(site, DEBUG)
            cache.delete_cache()

    @staticmethod
    def is_valid_site(site):
        """ Check if the site is valid
            :param site: The site
            :return boolean
        """

        sites = Files.get_file_list(SITE_PATH, [".urls"])
        return site + ".py" in sites

    @staticmethod
    def valid_action(action):
        """ Check if the action provided is valid
            :param action: The action
            :return boolean
        """
        if action == ACTION_CONVERT or \
           action == ACTION_DOWNLOAD or \
           action == ACTION_DELETE or \
           action == ACTION_CREATE_DB or \
           action == ACTION_DOWNLOAD_IMAGE or \
           action == ACTION_TEST:

            return True

        return False

    @staticmethod
    def get_image_name(name, filename, _type, suffix=""):
        """ Normalize images name (from web to local)
            :param name: the image name
            :param filename: the filename
            :param _type: Type (main, ingredient, step)
            :param suffix: A suffix name
            :return string
        """
        filename, ext = path.splitext(filename)
        del filename
        return name + IMAGE_SEP + _type + suffix + ext
