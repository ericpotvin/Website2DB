""" Cache Module

    Delete cached files, images etc...
"""

from lib.Sites import Sites
from Files import Files


class Cache(Sites):
    """ Convert Class
    """

    def __init__(self, name, debug):
        """ init
            :param name: The site name
            :param debug: Debug mode
        """
        super(Cache, self).__init__(name, debug)

    def delete_cache(self):
        """ Delete cache files for a site
        """

        if self.debug:
            print "  Deleting %s files " % self.name

        Files.delete_folder(self.generated_folder)
        Files.delete_folder(self.image_folder)
