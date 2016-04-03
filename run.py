#!/usr/bin/python

""" Main program
"""
import argparse

from lib import ACTION_TEST, ACTION_DOWNLOAD_IMAGE, ACTION_DOWNLOAD, \
    ACTION_DELETE, ACTION_CONVERT, ACTION_CREATE_DB
from lib.Sites import Sites


# todo: move this?
def parse_arg():
    """ Get arguments list
        :return args
    """

    action_help = "[" \
                  + ACTION_CONVERT + ", " \
                  + ACTION_DOWNLOAD + ", " \
                  + ACTION_DOWNLOAD_IMAGE + ", " \
                  + ACTION_CREATE_DB + ", " \
                  + ACTION_DELETE + ", " \
                  + ACTION_TEST \
                  + "]"

    parser = argparse.ArgumentParser(description="Website2jSonDB")
    parser.add_argument("--site",
                        default="",
                        type=str,
                        metavar='[website.com]',
                        nargs=1,
                        help='The website to process',
                        required=True)
    parser.add_argument("--action",
                        default="",
                        type=str,
                        metavar=action_help,
                        nargs=1,
                        help='Action to perform',
                        required=True)

    return parser.parse_args()


if __name__ == '__main__':
    ARGS = parse_arg()
    Sites.execute(ARGS.site[0], ARGS.action[0])
