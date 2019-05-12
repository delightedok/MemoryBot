#! python3
# coding=utf-8

import CAddressAnalyserUtils

if __name__ == '__main__':
    log_handler = CAddressAnalyserUtils.CAddressAnalyserHandler()
    log_handler.log_analyse('C:\\Users\\NakamoriAkina-TGS\\Desktop\\program\\memory.log',
                            'C:\\Users\\NakamoriAkina-TGS\\Desktop\\program\\memory_func.record')
