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

def main():
    print("Entering main()")

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
        for subdir in subdirs:
            print(subdir)
            remediated_name = remediate_string(subdir)
            if remediated_name != subdir:
                os.rename(os.path.join(dirpath, subdir),
                          os.path.join(dirpath, remediated_name))
            # as_test_just_rename_dir(root,subdir)
            print(subdir)

def find_files(target_dir):
    for root, subdirs, files in os.walk(target_dir):
        for target_file in files:
            print(os.path.join(root,target_file))
            process_file(target_file)

def process_file(target_file):
    # separate file into basename and extension
    basename, extension = os.path.splitext(target_file)
    print(basename)
    print(extension)

def as_test_just_rename_dir(base_path, target_dir):
    os.rename(os.path.join(base_path, target_dir),
              os.path.join(base_path, target_dir + "foo"))

def remediate_string(str_arg):
    # first, handle non-ASCII characters
    ascii_str = unidecode(str_arg)
    # then, replace invalid ASCII characters, such as space, !, *, ., etc
    remediated_str = re.sub('[^a-zA-Z0-9]+','_',ascii_str)
    return remediated_str

def validate_name_and_remediate_if_needed(target_name):
    pass

if __name__ == "__main__":
    main()
