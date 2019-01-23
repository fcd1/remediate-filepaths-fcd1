# assumption: Remediate filenames and path to filenames
# input: absolute path to directory containing filename to remediate
# fcd1, 18Oct18: add a no-op operation, where it will print out the change,
# but not actually change the dir/file name.
# use --dry-run

import sys
import os
import argparse
from unidecode import unidecode
import re
import logging
from datetime import datetime

def main():
    print("Entering main()")

    setup_logging()

    # process arguments

    # get arguments. Returns a list, first entry is name of script

    # assuming called as follows: python3 basic_sanitize_filename.py hi
    # rest of arguments should be absolute paths to directories
    # args = sys.argv
    # print(args)
    # args.pop(0)
    # print(args)

    parser = argparse.ArgumentParser(description='remediate names for directory contents (files and subdirs)')
    parser.add_argument('dirs',
                        metavar='dir',
                        nargs='+',
                        help='directory to remediate')

    args = parser.parse_args()

    # for each argument
    for i, directory in enumerate(args.dirs):
        # only process dir if it's an absolute path and
        # it's really a directory
        if ( os.path.isabs(directory) and os.path.isdir(directory) ):
            print("directory at position " + str(i) + " is " + directory)
            process_dir(directory)
        else:
            print("Kaboom!")

def process_dir(target_dir):
    # os.walk takes a topdown parameter which defaults to true.
    # Need to set it to true so it goes bottom-up.
    for dirpath, subdirs, files in os.walk(target_dir, topdown=False):
        # First, handle subdirs in current directory
        for subdir in subdirs:
            remediated_name = remediate_basename_dirname(subdir)
            if remediated_name != subdir:
                os.rename(os.path.join(dirpath, subdir),
                          os.path.join(dirpath, remediated_name))
        # Second, handle files in current directory
        for filename in files:
            # separate file into basename and extension
            basename, extension = os.path.splitext(filename)
            remediated_basename = remediate_basename_dirname(basename)
            remediated_extension = remediate_extension(extension) if extension else extension
            if remediated_basename != basename or remediated_extension != extension:
                os.rename(os.path.join(dirpath, filename),
                          os.path.join(dirpath, remediated_basename + remediated_extension))

def remediate_basename_dirname(str_arg):
    # first, handle non-ASCII characters
    ascii_str = unidecode(str_arg)
    # then, replace invalid ASCII characters, such as space, !, *, ., etc
    remediated_str = re.sub('[^a-zA-Z0-9]+','_',ascii_str)
    return remediated_str

def remediate_extension(str_arg):
    # remove leading '.'
    extension_str = str_arg.strip('.')
    # first, handle non-ASCII characters
    ascii_extension_str = unidecode(extension_str)
    # then, replace invalid ASCII characters, such as space, !, *, ., etc
    remediated_extension_str = re.sub('[^a-zA-Z0-9]+','_',ascii_extension_str)
    return '.' + remediated_extension_str

# Following return the absolute path to the logfile that will be generate
# The return value will contain the filename
def return_logfile_destination(log_filename):
    sudo_user = os.getenv('SUDO_USER')
    user = os.getenv('USER')
    print('SUDO_USER is set to', sudo_user)
    print('USER is set to', user)
    if sudo_user:
        print('Since SUDO_USER set, will use it')
        return os.path.join(os.path.expanduser('~' + sudo_user),
                            log_filename)
    else:
        print('Since SUDO_USER is not set, will use USER instead')
        return os.path.join(os.path.expanduser('~' + user),
                            log_filename)

def setup_logging(log_filename=return_logfile_destination('remediate_filepaths.'
                                                          + datetime.now().strftime("%d%b%y_%H%M%S")
                                                          + '.log')):
    # file for logging
    logfile_handler = logging.FileHandler(log_filename)
    global file_logger
    file_logger = logging.getLogger('remediate_filepaths_logger')
    file_logger.setLevel('INFO')
    file_logger.addHandler(logfile_handler)
    file_logger.info('Logging started on ' + datetime.now().strftime("%x") + ' at ' + datetime.now().strftime("%X"))

def setup_logging_original(log_filename=os.path.join('log/',datetime.now().strftime("%d%b%y_%H%M%S"))):
    # local file for logging
    logfile_handler = logging.FileHandler(log_filename)
    # tty. Believe stderr
    stream_handler = logging.StreamHandler()
    global stream_logger, file_logger, stream_file_logger
    stream_logger = logging.getLogger('migrate_doi_stream_logger')
    stream_logger.setLevel('INFO')
    stream_logger.addHandler(stream_handler)
    file_logger = logging.getLogger('migrate_doi_file_logger')
    file_logger.setLevel('INFO')
    file_logger.addHandler(logfile_handler)
    stream_file_logger = logging.getLogger('migrate_doi_stream_file_logger')
    stream_file_logger.setLevel('INFO')
    stream_file_logger.addHandler(logfile_handler)
    stream_file_logger.addHandler(stream_handler)
    file_logger.info('Logging started on ' + datetime.now().strftime("%x") + ' at ' + datetime.now().strftime("%X"))

if __name__ == "__main__":
    main()
