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
    parser = argparse.ArgumentParser(description='remediate names for directory contents (files and subdirs)')
    parser.add_argument('dirs',
                        metavar='dir',
                        nargs='+',
                        help='directory to remediate')
    parser.add_argument('-v','--verbose',
                        action='store_true',
                        help='verbose logging, which includes untouched files/dirs')
    global args
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

def log_processing_msg(offset, type_arg, name):
    file_logger.info(offset + 'Processing ' + type_arg + ": '" + name + "'")

def log_renamed_msg(offset, type_arg, old_name, new_name):
    file_logger.info(offset + 'Renamed ' + type_arg)
    file_logger.info(offset + "old: '" + old_name + "'")
    file_logger.info(offset + "new: '" + new_name + "'")

def log_name_exists_error(offset, type_arg, old_name, new_name):
    file_logger.info(offset + '**** ERROR (BEGIN) **** -- ' + type_arg +
                     " with new name already exists, so won't rename original " + type_arg + '.')
    file_logger.info(offset + "old: '" + old_name + "'")
    file_logger.info(offset + "new: '" + new_name + "'")
    file_logger.info(offset + '**** ERROR (END) **** -- See above info')

def process_dir(target_dir):
    file_logger.info('Starting dir for script:')
    file_logger.info("'" + target_dir + "'")
    file_logger.info('All current dir paths in the log will be relative to the above path')
    # offset is used when logging output, to help with the formating
    offset = '  '
    no_offset = ''
    # os.walk takes a topdown parameter which defaults to true.
    # Need to set it to true so it goes bottom-up.
    for dirpath, subdirs, files in os.walk(target_dir, topdown=False):
        file_logger.info('Current dir: ')
        file_logger.info("'" + os.path.relpath(dirpath,target_dir) + "'")
        # First, handle subdirs in current directory
        for subdir in subdirs:
            if args.verbose:
                log_processing_msg(offset, 'subdir', subdir)
            remediated_name = remediate_basename_dirname(subdir)
            if remediated_name != subdir:
                if os.path.lexists(os.path.join(dirpath,remediated_name)):
                    log_name_exists_error(no_offset, 'subdir', subdir, remediated_name)
                else:
                    os.rename(os.path.join(dirpath, subdir),
                              os.path.join(dirpath, remediated_name))
                    log_renamed_msg(offset, 'subdir', subdir, remediated_name)
        # Second, handle files in current directory
        for filename in files:
            if args.verbose:
                log_processing_msg(offset, 'file', filename)
            # separate file into basename and extension
            basename, extension = os.path.splitext(filename)
            remediated_basename = remediate_basename_dirname(basename)
            remediated_extension = remediate_extension(extension) if extension else extension
            if remediated_basename != basename or remediated_extension != extension:
                if os.path.lexists(os.path.join(dirpath,remediated_basename + remediated_extension)):
                    log_name_exists_error(no_offset, 'file', filename, remediated_basename + remediated_extension)
                else:
                    os.rename(os.path.join(dirpath, filename),
                              os.path.join(dirpath, remediated_basename + remediated_extension))
                    log_renamed_msg(offset, 'file', filename, remediated_basename + remediated_extension)

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
