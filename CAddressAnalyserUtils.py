#! python3
# coding=utf-8


import re
import FileUtils


class CAddressAnalyserUtils:

    pat_malloc = re.compile(r'^[\t _0-9a-zA-Z*\->.]+?=[\w\W]*?[c|m]alloc[\w\W]+')
    pat_malloc_address_declare = re.compile(r'^[\t _0-9a-zA-Z*\->.]+')
    pat_malloc_address = re.compile(r'[_0-9a-zA-Z\->.]+')

    # malloc memory by calling malloc or calloc
    @staticmethod
    def get_malloc_line_address_variable(line):
        result = CAddressAnalyserUtils.pat_malloc.findall(line)
        if len(result) > 0:
            address_declare = CAddressAnalyserUtils.pat_malloc_address_declare.findall(result[0])[0]
            address = CAddressAnalyserUtils.pat_malloc_address.findall(result[0])
            if len(address) > 0:
                if '*' in address_declare:
                    return address[1]
                else:
                    return address[0]
        return None

    # malloc memory by calling malloc or calloc
    @staticmethod
    def is_malloc_line(line):
        result = CAddressAnalyserUtils.pat_malloc.findall(line)
        if len(result) > 0:
            return True
        else:
            return False

    pat_log_malloc_line = re.compile(r'^\w+? \d+ [c|m]alloc 0x[\da-fA-F]+$')
    pat_log_free_line = re.compile(r'\w+? \d+ free 0x[\da-fA-F]+$')

    @staticmethod
    def log_is_malloc_line(line):
        _line = line
        if '\n' in line:
            _line = line[: len(line) - 1]
        if '\r' in _line:
            _line = _line[: len(_line) - 1]
        result = CAddressAnalyserUtils.pat_log_malloc_line.match(_line)
        if result is not None:
            return True
        else:
            return False

    @staticmethod
    def log_is_free_line(line):
        _line = line
        if '\n' in line:
            _line = line[: len(line) - 1]
        if '\r' in _line:
            _line = _line[: len(_line) - 1]
        result = CAddressAnalyserUtils.pat_log_free_line.match(_line)
        if result is not None:
            return True
        else:
            return False

    @staticmethod
    def log_get_line_info(line):
        _line = line
        if '\n' in line:
            _line = line[: len(line) - 1]
        if '\r' in _line:
            _line = _line[: len(_line) - 1]
        info = dict()
        results = _line.split(' ')
        if 4 == len(results):
            info['Function'] = results[0]
            info['Line'] = results[1]
            info['Type'] = results[2]
            info['Address'] = results[3]
            return info
        else:
            print('split of line[{}] failed!'.format(_line))
            return None


class CAddressAnalyserHandler:

    def __init__(self):
        self.address_info_dict = dict()

    @staticmethod
    def _log_analyse(line, args):
        if CAddressAnalyserUtils.log_is_malloc_line(line):
            info = CAddressAnalyserUtils.log_get_line_info(line)
            if info is not None:
                args[info['Address']] = info
        elif CAddressAnalyserUtils.log_is_free_line(line):
            info = CAddressAnalyserUtils.log_get_line_info(line)
            if info is not None:
                try:
                    args.pop(info['Address'])
                except KeyError:
                    print('key[{}] is not in address_info_dict'.format(info['Address']))

    def log_analyse(self, filename_log, filename_dst=None):
        log_file_handler = FileUtils.FileHandler(filename_log)
        log_file_handler.read_line_iterator(self._log_analyse, args=self.address_info_dict)
        for item in self.address_info_dict:
            if filename_dst is not None:
                FileUtils.FileUtils.append_plain(filename_dst, self.address_info_dict[item])
            else:
                print(item + ' -- ' + str(self.address_info_dict[item]))
