# coding: utf-8
""" blue apron website
"""
from collections import OrderedDict
import re

from Database import Database
from HTMLCleaner import HTMLCleaner

from lib.Sites import Sites
from lib.Testing import Testing


class BlueApron(object):
    """ BlueApron site class
    """
    SITE_NAME = "blueapron"
    BASE_URL = "http://blueapron.com/recipes/"

    FIELD_NAME = "name"
    FIELD_IMAGE = "images"
    FIELD_INGREDIENT = "ingredients"
    FIELD_INSTRUCTION = "instructions"
    FIELD_SERVINGS = "servings"
    FIELD_CALORIES = "calories"
    FIELD_LINK = "link"
    FIELD_ORDER = "order_number"

    IMAGE_MAIN = "main"
    IMAGE_INGREDIENT = "ingredient"
    IMAGE_STEP = "steps"

    TABLE_NAME = "meal"

    TEST_FILE = "warm-grain-salad-with-beets-orange-avocado-gorgonzola"

    @staticmethod
    def get_link_tag():
        """ Get the link field
        """
        return BlueApron.FIELD_LINK

    # TODO: Use HTLMParser module instead
    @staticmethod
    def get_replace_html():
        """ Get the list of HTML tags we need to remove
            :return list
        """

        replace = OrderedDict()

        # replace needed non ascii
        replace[u"½"] = u"&#189;"
        replace[u"¼"] = u"&#188;"
        replace[u"¾"] = u"&#190;"

        # remove \n</a>
        replace["\n</a>"] = "</a>"

        # site
        replace["<span itemscope itemtype='http://schema.org/Recipe'>"] = ""
        replace[" - Blue Apron"] = ""

        tags = HTMLCleaner.get_common_tags()
        for (_from, _to) in tags.items():
            replace[_from] = _to

        # headers and footer
        replace["<header(.*?)</header>"] = ""
        replace["<footer(.*?)</footer>"] = ""

        tags = HTMLCleaner.get_layout_tags()
        for (_from, _to) in tags.items():
            replace[_from] = _to  # tags

        tags = HTMLCleaner.get_style_tags()
        for (_from, _to) in tags.items():
            replace[_from] = _to

        # layout
        replace[
            "<section class='section-rec-reviews container' id='reviews'>" +
            "(.*?)</section>"] = ""
        replace[
            "Recipe: (.*?)<section class='section-rec-basics js-RecipeArea' " +
            "data-area-name='basics' id='basics'>"] = ""
        replace[
            "<section class='section-rec-tools container' id='tools'>" +
            "(.*?)</section>"] = ""
        replace["Per Serving(.*?)</section>"] = ""
        replace["\n\n\n"] = ""
        replace[' class="rec-splash-img"'] = ""
        replace['class="img-max"'] = ""
        replace[' class="ingredients-img"'] = ""
        replace[
            "<section class='section-rec-instructions container' " +
            "id='instructions'>(.*?)</section>"] = ""
        replace[
            "<section class='section-rec-techniques container' " +
            "id='techniques'>(.*?)</section>"] = ""
        replace[r" to download a PDF of this recipe."] = ""
        replace[
            "<section class='section-rec-ingredients container' " +
            "id='ingredients'>"] = ""

        # a
        replace["<a class='js-StepStoryLaunch(.*?)>(.*?)</a>"] = ""
        replace["<a class='js-IngModalLink'(.*?)>"] = ""
        replace["<a class='js-SubStory vid-tip'(.*?)>"] = ""
        replace["<a href=\"\"(.*?)>(.*?)</a>"] = ""
        replace["<a(.*?)>(.*?)</a>"] = ""

        tags = HTMLCleaner.clean_up_tags()
        for (_from, _to) in tags.items():
            replace[_from] = _to

        replace["Servings"] = "\n"
        replace["About\n\n"] = ""
        replace["\nCalories:"] = "\nCalories: "
        replace['</section>'] = ""

        for i in ["1", "2", "3", "4", "5", "6"]:
            replace[i + "\n\n"] = i + ") "

        # in case there's no text on the instruction
        for i in ["1", "2", "3", "4", "5", "6"]:
            _from = i + "\n\t"
            _to = i + ") Step " + i + ": "
            replace[_from] = _to
            del (_from, _to)

        replace["<img alt=\"Introducing our Market(.*?) />"] = ""
        replace["<img alt=\"Recipe cards\" (.*?) />"] = ""
        replace[r"\) <img"] = "\n<img"

        replace[r"\) \n"] = "\n"
        replace["</a>"] = ""

        return replace

    @staticmethod
    def parse_line(line, data):
        """ Parse line for converted html files
            :param line: The line (string)
            :param data: The json object
        """

        if line[:4] == "<img":
            img = line.replace('<img src="', "").replace('" />', "")
            BlueApron._process_image(img, data[BlueApron.FIELD_IMAGE])

        elif line[:6] == "Makes:":
            servings = int(line.replace("Makes:", ""))
            data.update({BlueApron.FIELD_SERVINGS: servings})

        elif line[:9] == "Calories:":
            calories = int(line.replace("Calories:", ""))
            data.update({BlueApron.FIELD_CALORIES: calories})

        elif re.findall("[0-9]( )", line[:2]) or \
                re.findall("[0-9](/)[0-9]( )", line[:4]) or \
                re.findall("[0-9](&#)", line[:3]) or \
                re.findall("(&#)", line[:2]):
            data[BlueApron.FIELD_INGREDIENT][
                len(data[BlueApron.FIELD_INGREDIENT])] = line

        elif re.findall(r"[0-9](\) )", line[:3]):
            data[BlueApron.FIELD_INSTRUCTION][
                len(data[BlueApron.FIELD_INSTRUCTION])] = line

        else:
            data.update({BlueApron.FIELD_NAME: line})

    @staticmethod
    def _process_image(img, data_image):
        """ Process the img
            :param img: The image url
            :param data_image: The data img object
        """
        if img.find("/ingredient_images/") > 0:
            data_image[BlueApron.IMAGE_INGREDIENT] = img
        elif img.find("/c_main_dish_images/") > 0:
            data_image[BlueApron.IMAGE_MAIN] = img
        elif img.find("/recipe_steps/") > 0:
            if BlueApron.IMAGE_STEP not in data_image:
                data_image[BlueApron.IMAGE_STEP] = OrderedDict()
            length = len(data_image[BlueApron.IMAGE_STEP])
            data_image[BlueApron.IMAGE_STEP][length] = img

    @staticmethod
    def parse_images(base_name, data):
        """ Download the image from a json file
            :param base_name: The base name of the image
            :param data: Json Object
        """

        images = {}

        # main image
        _image = str(data[BlueApron.FIELD_IMAGE][
                         BlueApron.IMAGE_MAIN]).encode("utf8")
        image = Sites.get_image_name(base_name, _image, BlueApron.IMAGE_MAIN)
        images[image] = _image

        # ingredients image (if exists)
        if BlueApron.IMAGE_INGREDIENT in data[BlueApron.FIELD_IMAGE]:
            image = Sites.get_image_name(
                base_name,
                data[BlueApron.FIELD_IMAGE][BlueApron.IMAGE_INGREDIENT],
                BlueApron.IMAGE_INGREDIENT
            )
            images[image] = \
                data[BlueApron.FIELD_IMAGE][BlueApron.IMAGE_INGREDIENT]

        # steps
        for step in data[BlueApron.FIELD_IMAGE][BlueApron.IMAGE_STEP]:
            image = Sites.get_image_name(
                base_name,
                data[BlueApron.FIELD_IMAGE][BlueApron.IMAGE_STEP][step],
                BlueApron.IMAGE_STEP,
                step,
                )
            images[image] = \
                data[BlueApron.FIELD_IMAGE][BlueApron.IMAGE_STEP][step]

        return images

    @staticmethod
    def get_default_json():
        """ Build default dict (json file)
            :return dict
        """
        data = OrderedDict()
        data[BlueApron.FIELD_NAME] = ""
        data[BlueApron.FIELD_LINK] = ""
        data[BlueApron.FIELD_SERVINGS] = 0
        data[BlueApron.FIELD_CALORIES] = 0

        data.update({BlueApron.FIELD_IMAGE: OrderedDict()})
        data.update({BlueApron.FIELD_INSTRUCTION: OrderedDict()})
        data.update({BlueApron.FIELD_INGREDIENT: OrderedDict()})

        return data

    @staticmethod
    def get_sql_tables():
        """ Get the list of SQL Tables to create
            :return list
        """
        return [BlueApron.TABLE_NAME,
                BlueApron.TABLE_NAME + Database.SQL_FIELD_SEPARATOR +
                BlueApron.FIELD_INGREDIENT,
                BlueApron.TABLE_NAME + Database.SQL_FIELD_SEPARATOR +
                BlueApron.FIELD_INSTRUCTION
                ]

    @staticmethod
    def get_sql_types(table_name):
        """ Get the database field type for the table name
            :param table_name: The table name
        """

        fields = OrderedDict()

        if table_name == BlueApron.TABLE_NAME:
            fields[Database.SQL_PRIMARY_KEY] = "INTEGER"
            fields[BlueApron.FIELD_NAME] = "TEXT"
            fields[BlueApron.FIELD_LINK] = "TEXT"
            fields[BlueApron.FIELD_CALORIES] = "INTEGER"
            fields[BlueApron.FIELD_SERVINGS] = "INTEGER"

            return fields

        table = BlueApron.TABLE_NAME + Database.SQL_FIELD_SEPARATOR

        if table_name == table + BlueApron.FIELD_INGREDIENT or \
           table_name == table + BlueApron.FIELD_INSTRUCTION:

            fields[Database.SQL_PRIMARY_KEY] = "INTEGER"

            foreign_key = Database.SQL_FOREIGN_KEY_PREFIX + \
                BlueApron.TABLE_NAME + \
                Database.SQL_FOREIGN_KEY_SUFFIX
            fields[foreign_key] = "INTEGER"

        if table_name == table + BlueApron.FIELD_INGREDIENT:
            fields[BlueApron.FIELD_ORDER] = "TEXT"
            fields[BlueApron.FIELD_INGREDIENT] = "TEXT"
            return fields

        if table_name == table + BlueApron.FIELD_INSTRUCTION:
            fields[BlueApron.FIELD_ORDER] = "TEXT"
            fields[BlueApron.FIELD_INSTRUCTION] = "TEXT"
            return fields

        return None

    @staticmethod
    def convert_sub_table_data(fk_name, table, data, fk_id):
        """ Convert an OrderDict to a custom sub table OrderDict
            :param fk_name: The foreign key name
            :param table: The table name
            :param data: The json data
            :param fk_id: The foreign key
        """
        new_data = OrderedDict()

        fk_name = Database.SQL_FOREIGN_KEY_PREFIX + fk_name + \
            Database.SQL_FOREIGN_KEY_SUFFIX

        for _key in data:

            tmp = OrderedDict()

            if table == BlueApron.FIELD_INGREDIENT:
                tmp[fk_name] = fk_id
                tmp[BlueApron.FIELD_ORDER] = _key
                tmp[BlueApron.FIELD_INGREDIENT] = data[_key]

            elif table == BlueApron.FIELD_INSTRUCTION:
                tmp[fk_name] = fk_id
                tmp[BlueApron.FIELD_ORDER] = _key
                tmp[BlueApron.FIELD_INSTRUCTION] = data[_key]

            new_data.update({_key: tmp})

        return new_data

    @staticmethod
    def get_test_data():
        """ Test the json file
            :return list
        """

        tests = [
            {
                "name": BlueApron.FIELD_NAME,
                "type": Testing.TEST_TYPE_STR
            },
            {
                "name": BlueApron.FIELD_INSTRUCTION,
                "type": Testing.TEST_TYPE_DICT
            },
            {
                "name": BlueApron.FIELD_INGREDIENT,
                "type": Testing.TEST_TYPE_DICT
            },
            {
                "name": BlueApron.FIELD_CALORIES,
                "type": Testing.TEST_TYPE_NUM
            },
            {
                "name": BlueApron.FIELD_SERVINGS,
                "type": Testing.TEST_TYPE_NUM
            },
            {
                "name": BlueApron.FIELD_IMAGE,
                "type": Testing.TEST_TYPE_DICT
            }
        ]

        return tests
