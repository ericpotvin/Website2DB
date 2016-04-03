""" Database module
"""
from collections import OrderedDict
import json

from Database import Database
from Files import Files, FILE_EXT_JSON
from lib.Sites import __classmap__, Sites


class DB(Sites):
    """ DB Class
    """

    def __init__(self, name, debug):
        """ init
            :param name: The site name
            :param debug: Debug mode
        """
        super(DB, self).__init__(name, debug)
        self.db_name = self.generated_folder + self.name + Database.DATABASE_EXT
        self.database = None

    def create(self):
        """ Create the database
        """

        self._create_db()
        self._create_tables()

        self._insert()
        self.database.close()

    def _create_db(self):
        """ Create the DB file
        """

        if self.debug:
            print "  Creating DB name %s" % self.db_name

        self.database = Database(self.db_name)

    def _create_tables(self):
        """ Create the table(s)
        """
        tables = __classmap__[self.name].get_sql_tables()

        for table in tables:
            if self.debug:
                print "    Creating DB table %s" % table

            fields = __classmap__[self.name].get_sql_types(table)
            self.database.create_table(table, fields)

    def _insert(self):
        """ Insert records
        """

        if self.debug:
            print "  Creating BD for %s" % self.test_file + FILE_EXT_JSON
            file_list = [self.test_file + FILE_EXT_JSON]
        else:
            file_list = Files.get_file_list(self.generated_folder)

        for json_file in file_list:

            if not Files.file_exists(self.generated_folder + json_file):
                continue

            data = json.load(open(self.generated_folder + json_file))
            sub_tables = OrderedDict()

            for (_key, _value) in data.items():

                # images are not saved in the db
                if _key == __classmap__[self.name].FIELD_IMAGE:
                    del data[_key]
                    continue

                if isinstance(_value, dict):
                    sub_tables[_key] = data[_key]
                    del data[_key]
                del _key

            self._parse_data("", data, sub_tables)

    def _parse_data(self, _key, data, sub_tables):
        """ Read a json file
            :param _key: The key of the object
            :param data: the json data for the main table
            :param sub_tables: json data for the sub tables
        """
        table = __classmap__[self.name].TABLE_NAME
        if len(_key) > 0:
            table += Database.SQL_FIELD_SEPARATOR + _key

        _id = self.database.insert(table, data)

        if not _id:
            return

        for sub in sub_tables:
            sub_data = __classmap__[self.name].convert_sub_table_data(
                table, sub, sub_tables[sub], _id)

            self.database.insert(table + Database.SQL_FIELD_SEPARATOR + sub,
                                 sub_data, _id)
