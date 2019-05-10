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

    def rename(self, filename_new):
        os.rename(self.filename, filename_new)
        self.filename = filename_new

    def path(self):
        return os.path.dirname(self.filename)

    def basename(self):
        return os.path.basename(self.filename)

    @staticmethod
    def _format_eol_callback(line, args):
        FileUtils.append_plain(args, line)

    # format end of line: if the line is end not with '\r\n', then the function would format the line to end with '\r\n'
    def format_eol(self):
        format_basename = '.' + self.basename() + '.format'
        format_filename = FileUtils.path_join_filename(self.path(), format_basename)
        self.read_line_iterator(self._format_eol_callback, args=format_filename)
        self.remove()
        FileUtils.rename(format_filename, self.filename)


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
    def _get_files_from_path(path, path_depth):
        result_list = list()
        file_list = os.listdir(path)
        for file in file_list:
            filename = os.path.join(path, file)
            if os.path.isfile(filename):
                result_list.append([filename, path_depth])
            else:
                result_list += FileUtils._get_files_from_path(filename, path_depth + 1)
        return result_list

    @staticmethod
    def get_files_from_path(path):
        path_depth = 0
        result_list = FileUtils._get_files_from_path(path, path_depth)
        return result_list

    @staticmethod
    def is_file_with_suffix(filename, suffix):
        regexp = r'^[\w\W]+?\.' + suffix + r'$'
        pattern = re.compile(regexp)
        if pattern.match(filename) is not None:
            return True
        else:
            return False

    @staticmethod
    def rename(filename_old, filename_new):
        os.rename(filename_old, filename_new)

    @staticmethod
    def get_path_from_filename(filename):
        return os.path.dirname(filename)

    @staticmethod
    def get_basename_from_filename(filename):
        return os.path.basename(filename)

    @staticmethod
    def _format_eol_callback(line, args):
        filename = args[0]
        encoding = args[1]
        FileUtils.append_plain(filename, line, encoding=encoding)

    # format end of line: if the line is end not with '\r\n', then the function would format the line to end with '\r\n'
    @staticmethod
    def format_eol(filename, replace=False, encoding='utf-8'):
        basename = FileUtils.get_basename_from_filename(filename)
        path = FileUtils.get_path_from_filename(filename)
        filename_format = FileUtils.path_join_filename(path, '.' + basename + '.format')
        FileUtils.read_line_iterator(filename, FileUtils._format_eol_callback,
                                     args=[filename_format, encoding], encoding=encoding)
        if replace is True:
            FileUtils.remove(filename)
            FileUtils.rename(filename_format, filename)
