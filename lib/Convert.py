""" Convert HTML

    This convert an HTML file to a simple/raw text file
"""
import json

from lib.Sites import __classmap__, Sites
from Files import FILE_EXT_HTML, FILE_EXT_JSON, Files
from HTMLCleaner import HTMLCleaner


class Convert(Sites):
    """ Convert Class
    """

    def __init__(self, name, debug):
        """ init
            :param name: The site name
            :param debug: Debug mode
        """
        super(Convert, self).__init__(name, debug)
        self.tags = __classmap__[name].get_replace_html()

    def convert_html(self):
        """ Convert HTML file to json save the jSon file
        """

        if self.debug:
            print "  Converting: %s" % self.download_folder + \
                  self.test_file + FILE_EXT_HTML
            file_list = [self.download_folder + self.test_file + FILE_EXT_HTML]
        else:
            file_list = Files.get_file_list(self.download_folder)

        for html_file in file_list:

            content = Files.get_raw_contents(html_file)

            html_cleaner = HTMLCleaner(self.tags)
            content = html_cleaner.clean(content)

            link = html_file.replace(FILE_EXT_HTML, "").replace(
                self.download_folder, "")

            content = self._text_to_json(content, link)

            file_to_save = html_file.replace(FILE_EXT_HTML,
                                             FILE_EXT_JSON
                                             ).replace(
                self.download_folder, "")

            if self.debug:
                print "  File to save: %s%s" % (self.generated_folder,
                                                file_to_save)

            if Files.file_exists(self.generated_folder + file_to_save):
                continue

            Files.write(content, file_to_save, self.generated_folder)

    def _text_to_json(self, content, filename):
        """ Process a generated raw file
            :param content: The filename content
            :param filename: The filename (used for link)
            :return: jSon String
        """

        json_object = __classmap__[self.name].get_default_json()

        for content_data in content.split("\n"):
            self._process_line(content_data, json_object)

        # Link: where to find the data, images, etc...
        link = __classmap__[self.name].get_link_tag()
        json_object[link] = str(filename).replace(FILE_EXT_HTML, "")

        return json.dumps(json_object, ensure_ascii=False)

    def _process_line(self, line, data):
        """ Process each line of the raw generated file
            :param line: The line
            :param data: The data
            - line 1: Name:
            - line that starts with # and space: ingredients
            - line that starts with #): instructions
            - img: all images
            - makes: # of servings
            - calories: # of calories per servings
        """
        line = line.strip()

        if not line:
            return

        if self.debug:
            print "    line = %s..." % line[:40]

        __classmap__[self.name].parse_line(line, data)
