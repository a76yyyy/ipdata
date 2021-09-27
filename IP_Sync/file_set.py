# -*- encoding: utf-8 -*-
'''
@Description:  :检查文件或目录是否存在, 存在返回1, 不存在则创建并返回0.
@Date          :2020/11/03 20:53:59
@Author        :a76yyyy
@version       :1.0
'''
import os
def file_set(file= None, open_type = None):
    if not os.path.exists(file):
        if not os.path.exists(os.path.dirname(file)):
            os.makedirs(os.path.dirname(file))
        if open_type == 'dir':
            os.makedirs(file)
        if open_type == 'file':
            with open(file, 'wb+'):
                pass
        if not os.path.exists(file):
            if os.path.isdir(file):
                os.makedirs(file)
            elif os.path.isfile(file):
                if not os.path.exists(os.path.dirname(file)):
                    os.makedirs(os.path.dirname(file))
                with open(file, 'wb+'):
                    pass
        return 0
    return 1