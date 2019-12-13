'''自写简单文件工具模块'''
import os
from pathlib import Path

def get_file_obj(file_name,module):
    try:
        return open(file_name,module)
    except IOError as ie:
        print(ie)

def get_file_objr(file_name):
    return get_file_obj(file_name,'r')

def get_file_objw(file_name):
    return get_file_obj(file_name,'w')

def get_file_obja(file_name):
    return get_file_obj(file_name,'a')

def is_exists(f):
    return os.path.exists(f)

def is_file(f):
    return os.path.isfile(f)

def mkdir(file_path):
    try:
        Path(file_path).mkdir(parents=True)
    except:
        print('创建文件夹失败')
