""" Download a site
"""
from os import path
import json

from Files import Files, FILE_EXT_JSON, FILE_EXT_HTML
import Download
from lib.Sites import __classmap__, Sites


class DownloadSite(Sites):
    """ Download site class
    """

    def __init__(self, name, debug):
        """ init
            :param name: The site name
            :param debug: Debug mode
        """
        super(DownloadSite, self).__init__(name, debug)

    def download(self):
        """ Download HTML web pages
        """

        if self.debug:
            print "  Downloading: %s" % self.test_file + FILE_EXT_HTML
            url_list = [self.base_url + self.test_file + FILE_EXT_HTML]
        else:
            url_list = Files.get_raw_contents(self.name + ".urls", "./")

        for web_file in url_list:
            cached_file = web_file.replace(self.base_url, "")
            if not Files.file_exists(self.download_folder + cached_file):
                data = Download.download_page(web_file)
                Files.write(data, cached_file, self.download_folder)
            elif self.debug:
                print "    File %s already exists" % (self.download_folder +
                                                      cached_file)

    def download_image(self, url, filename):
        """ Download an image and save it to a location
            :param url: The url
            :param filename: The filename
        """

        if self.debug:
            print "    Downloading: %s\n     => %s" % \
                  (url, self.image_folder + filename)

        if path.isfile(self.image_folder + filename):
            return

        data = Download.download_page(url)
        Files.write(data, filename, self.image_folder)

    def download_images(self):
        """ Download images for a page (listed in the json file)
        """

        if self.debug:
            print "  Downloading Images: %s" % self.test_file + FILE_EXT_JSON
            file_list = [self.test_file + FILE_EXT_JSON]
        else:
            file_list = Files.get_file_list(self.generated_folder)

        for json_files in file_list:
            if not Files.file_exists(self.generated_folder + json_files):
                continue

            data = json.load(open(self.generated_folder + json_files))

            # define the base name for all images
            base_name = json_files.replace(FILE_EXT_JSON, "")

            images = __classmap__[self.name].parse_images(base_name, data)

            for (filename, url) in images.items():
                self.download_image(url, filename)
