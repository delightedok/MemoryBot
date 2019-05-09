#! python3
# coding=utf-8

import os
import re


class FileHandler:

    def __init__(self, filename, read_encoding='utf-8', write_encoding='utf-8'):
        self.filename = filename
        self.read_encoding = read_encoding
        self.write_encoding = write_encoding

    def read_line_iterator(self, line_callback, args=None, encoding='utf-8'):
        with open(self.filename, 'r', encoding=encoding) as fp:
            line = fp.readline()
            while line is not None and len(line) > 0:
                line_callback(line, args)
                line = fp.readline()
            fp.close()

    # append the txt-data to file
    def append_plain(self, data, encoding='utf-8'):
        with open(self.filename, 'a', encoding=encoding) as fp:
            fp.write(data)
            fp.close()

    def remove(self):
        os.remove(self.filename)

    def set_encoding(self, read_encoding=None, write_encoding=None):
        if read_encoding is not None:
            self.read_encoding = read_encoding
        if write_encoding is not None:
            self.write_encoding = write_encoding

    def rename(self, filename_old, filename_new):
        os.rename(filename_old, filename_new)
        self.filename = filename_new


class FileUtils:

    @staticmethod
    def read_line_iterator(filename, callback, args=None, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as fp:
            line = fp.readline()
            while line is not None and len(line) > 0:
                callback(line, args)
                line = fp.readline()
            fp.close()

    # append the txt-data to file
    @staticmethod
    def append_plain(filename, data, encoding='utf-8'):
        with open(filename, 'a', encoding=encoding) as fp:
            fp.write(data)
            fp.close()

    @staticmethod
    def remove(filename):
        os.remove(filename)

    @staticmethod
    def path_join_filename(path, filename):
        return os.path.join(path, filename)

    @staticmethod
    def get_files_from_path(path):
        result_list = list()
        file_list = os.listdir(path)
        for file in file_list:
            filename = os.path.join(path, file)
            if os.path.isfile(filename):
                result_list.append(filename)
            else:
                result_list += FileUtils.get_files_from_path(filename)
        return result_list

    @staticmethod
    def is_file_with_suffix(filename, suffix):
        regexp = r'[\w\W]+?\.' + suffix
        pattern = re.compile(regexp)
        return pattern.match(filename)

    @staticmethod
    def rename(filename_old, filename_new):
        os.rename(filename_old, filename_new)
