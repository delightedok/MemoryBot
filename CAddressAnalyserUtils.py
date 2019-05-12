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

    pat_free = re.compile(r'^[\t ]*?free\([_0-9a-zA-Z\->.]+\);')
    pat_free_address = re.compile(r'\([_0-9a-zA-Z\->.]+\)')

    # free memory by calling free or FREE
    @staticmethod
    def get_free_line_address_variable(line):
        result = CAddressAnalyserUtils.pat_free.findall(line)
        if len(result) > 0:
            address = CAddressAnalyserUtils.pat_free_address.findall(result[0])[0]
            address = address[1: len(address) - 1]
            return address
        return None

    # free memory by calling free or FREE
    @staticmethod
    def is_free_line(line):
        result = CAddressAnalyserUtils.pat_free.findall(line)
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
        self.path = None

    record_address_code_h = '#ifndef _PYTHON_RECORD_MEMORY_H_\n' \
                            '#define _PYTHON_RECORD_MEMORY_H_\n' \
                            'void python_record_malloc_address(const char * function, int line, void * pointer);\n' \
                            'void python_record_free_address(const char * function, int line, void * pointer);\n' \
                            '#endif\n'
    record_malloc_code_include = '#include <stdio.h>\n' \
                                 '#include \"python_record_memory.h\"\n'
    record_malloc_code_func = 'void python_record_malloc_address(const char * function, int line, void * pointer)\n' \
                              '{\n' \
                              '    printf(\"%s %d malloc %p\\n\", function, line, pointer);\n' \
                              '}\n'
    record_free_code_func = 'void python_record_free_address(const char * function, int line, void * pointer)\n' \
                            '{\n' \
                            '    printf(\"%s %d free %p\\n\", function, line, pointer);\n' \
                            '}\n'

    @staticmethod
    def _add_debug_memory_info_in_code(line, args):
        file_handler = args
        if CAddressAnalyserUtils.is_malloc_line(line):
            pointer = CAddressAnalyserUtils.get_malloc_line_address_variable(line)
            file_handler.append_plain(line)
            if '\\' not in line:
                file_handler.append_plain('python_record_malloc_address(__FUNCTION__, __LINE__, {});\n'.format(pointer))
            else:
                file_handler.append_plain('python_record_malloc_address(__FUNCTION__, __LINE__, {});\\\n'
                                          .format(pointer))
        elif CAddressAnalyserUtils.is_free_line(line):
            pointer = CAddressAnalyserUtils.get_free_line_address_variable(line)
            if '\\' in line:
                # it is only supported for style like this if free is defined in MACRO
                # #ifndef FREE
                # #define FREE(_p) do{\
                # 					if(_p)\
                # 					{\
                # if(NULL != _p)\
                #     python_record_free_address(__FUNCTION__, __LINE__, _p);\
                # 						free(_p);\
                # 					}\
                # 					_p = NULL;\
                # 				}while(0)
                file_handler.append_plain('if(NULL != {})\\\n'
                                          '    python_record_free_address(__FUNCTION__, __LINE__, {});\\\n'
                                          .format(pointer, pointer))
            else:
                file_handler.append_plain('if(NULL != {})\n'
                                          '    python_record_free_address(__FUNCTION__, __LINE__, {});\n'
                                          .format(pointer, pointer))
            file_handler.append_plain(line)
        else:
            file_handler.append_plain(line)

    def add_debug_memory_info_in_code(self, path):
        self.path = path

        file_c_list = FileUtils.FileUtils.get_files_from_path(self.path)
        for file_c in file_c_list:
            if FileUtils.FileUtils.is_file_with_suffix(file_c[0], 'c') \
                    or FileUtils.FileUtils.is_file_with_suffix(file_c[0], 'h'):
                include_str = '#include \"'
                depth = file_c[1]
                for i in range(depth):
                    include_str += '../'
                include_str += 'python_record_memory.h'
                include_str += '\"\n'
                FileUtils.FileUtils.rename(file_c[0], file_c[0] + '_bk')
                file_handler = FileUtils.FileHandler(file_c[0])
                file_handler.append_plain(include_str)
                FileUtils.FileUtils.read_line_iterator(file_c[0] + '_bk', self._add_debug_memory_info_in_code,
                                                       args=file_handler)

        record_func_filename_h = FileUtils.FileUtils.path_join_filename(path, 'python_record_memory.h')
        record_func_filename_c = FileUtils.FileUtils.path_join_filename(path, 'python_record_memory.c')
        FileUtils.FileUtils.append_plain(record_func_filename_h, self.record_address_code_h)
        record_func_code_handler = FileUtils.FileHandler(record_func_filename_c)
        record_func_code_handler.append_plain(self.record_malloc_code_include)
        record_func_code_handler.append_plain(self.record_malloc_code_func)
        record_func_code_handler.append_plain(self.record_free_code_func)

    @staticmethod
    def _log_analyse(line, args):
        args[1] += 1
        if CAddressAnalyserUtils.log_is_malloc_line(line):
            info = CAddressAnalyserUtils.log_get_line_info(line)
            if info is not None:
                info['Line_LOG'] = args[1]
                args[0][info['Address']] = info
        elif CAddressAnalyserUtils.log_is_free_line(line):
            info = CAddressAnalyserUtils.log_get_line_info(line)
            if info is not None:
                try:
                    args[0].pop(info['Address'])
                except KeyError:
                    print('key[{}] is not in address_info_dict'.format(info['Address']))

    def log_analyse(self, filename_log, filename_dst=None):
        log_file_handler = FileUtils.FileHandler(filename_log)
        line = 0
        log_file_handler.read_line_iterator(self._log_analyse, args=[self.address_info_dict, line])
        for item in self.address_info_dict:
            if filename_dst is not None:
                FileUtils.FileUtils.append_plain(filename_dst, str(self.address_info_dict[item]) + '\n')
            else:
                print(item + ' -- ' + str(self.address_info_dict[item]))
