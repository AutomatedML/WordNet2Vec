# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 15:44:49 2019

@author: XLi83
"""
import random
import config as cnf
from numpy import array
import numpy as np
from numpy.fft import fft, ifft, fftn, ifftn
from numpy.linalg import norm

def get_word_index(lastIndex = None):
    num = cnf.WORD_INDEX_LEN
     
    if lastIndex == None:
        return '0'*num
    index = str(int(lastIndex) + 1)
   
    padding = '0'*num
    
    index = padding[0:num-len(index)] + index
    return index


def generate_random_vector():
    v = array([random.gauss(0,1) for i in range(cnf.SEMANTIC_POINTER_DIMENSION)])
    nrm=norm(v)
    if nrm>0: v/=nrm
    return v
    
def list_to_str(alist):
    res=""
    for a in alist:
        
        if res != "":
            res = res + cnf.ARRAY_SEP
        if type(a) is tuple:
            res = res + cnf.WORD_RELATION_SEP.join([str(i) for i in a])
        else:
            if type(a) is np.float64:
                
                res = res + "{0:.4f}".format(a)
            else:
                res = res + str(a)
        
    return cnf.ARRAY_START+ res + cnf.ARRAY_END

def dict_to_str(alist):
    res=""
    for a in alist.keys():
        if res != "":
            res = res + cnf.ARRAY_SEP
        res = res + alist[a] + cnf.WORD_RELATION_SEP + a
    return cnf.ARRAY_START + res + cnf.ARRAY_END
    

def to_line(*argv):
    line = ""
    
        
    for arg in argv:
        if line != "":
            line = line + cnf.FIELD_SEP
        if (type(arg) is list):
            line = line + list_to_str(arg)
        elif (type(arg) is dict):
            line = line + dict_to_str(arg)
        else:
            line = line + str(arg)
            
    line = line + cnf.LINE_SEP
    
    return line

def parse_line(line):
    fields = line.split(cnf.FIELD_SEP)
    results = []
    for field in fields:
        if field.startswith(cnf.ARRAY_START):
            arr = parse_list(field)
            results.append(arr)
        else:
            results.append(field)
    return results


def load_pointers(pointer_file):
       
        pointer_map={}
        with open(pointer_file, 'r') as file:
            for line in file:
                fields = line.split(cnf.FIELD_SEP)
                pointer_map[fields[0]] = np.array(eval(fields[1]))
        return pointer_map
                
def save_pointers(pointers, pointer_file):
    if len(pointers) > 0:
        with open(pointer_file, 'w') as file:
            for symbol in pointers.keys():
                file.write(symbol + cnf.FIELD_SEP + \
                           list_to_str(pointers[symbol]) +cnf.LINE_SEP)
                
def parse_relation(line):
    fields = line.split(cnf.FIELD_SEP)
    word_index = fields[0]
               
    relation_words = parse_list(fields[1])
    
    relations = {}
    for word in relation_words:   
                               
        desc = word.split(cnf.WORD_RELATION_SEP)
        relations[desc[1]] = desc[0]
        
    return word_index, relations

def parse_list(line):
    line = line.strip()[1:-1]
    if line != '':
        return line.split(cnf.ARRAY_SEP)
    else:
        return []
                
def conv(a, b):
    
    return np.real(ifft(fft(a)*fft(b)))

def get_identity_pointer():
    p = np.zeros(cnf.SEMANTIC_POINTER_DIMENSION)
    p[0] = 1
    return p

def get_zero_pointer():
    return np.zeros(cnf.SEMANTIC_POINTER_DIMENSION)

def is_identity_pointer(pointer):
    if pointer[0] != 1:
        return False
    for i in range(1, len(pointer)):
        if pointer[i] != 0:
            return False
    return True

def is_zero_pointer(pointer):
    for i in range(0, len(pointer)):
        if pointer[i] != 0:
            return False
    return True

def invert_pointer(v):
    
    vf = fft(v)
    return np.real(ifft(1/vf))

