#! python3
# coding=utf-8


import re


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
