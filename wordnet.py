# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 09:26:03 2019

@author: XLi83
"""


import config as cnf
from os import path
import re
import utility as utl
import logging


_isA_symbols = ['@', '@i']
_holonym_symbols = ['#p', '#s', '#m']
                    
RELATION_SYMBOLS = _isA_symbols + _holonym_symbols
DATA_FILES = ["data.noun"]
SEMANTIC_NETWORK = "wordnet"
DATA_FIELD_SEP = " "

POS_WORD_ID = 0
POS_WORD_NUM = 3
POS_WORD = 4
WORD_LEN = 2
RELATION_LEN = 4


class WordNetRelation:
    
   
    pointers = None
    pointer_file = None
        
    def __init__(self):
        self.pointer_file = path.join(cnf.SEMANTIC_POINTER_DIR, SEMANTIC_NETWORK, cnf.SEMANTIC_POINTER_RELATION_FILE)
        self.pointers = {}
        
    
    def generate_semantic_pointers(self):
        """    
        output relation 
        """
        for i in range(len(RELATION_SYMBOLS)):
           
            self.pointers[RELATION_SYMBOLS[i]] = utl.generate_random_vector()
            
        utl.save_pointers(self.pointers, self.pointer_file)
        
    
       
                
class WordNetParser:
   
    
    def __init__(self, semantic_dir = None, result_dir = None):
        
        if semantic_dir == None:
            self.semantic_dir = path.join(cnf.SEMANTIC_NETWORK_DIR, SEMANTIC_NETWORK)
        else:
            self.semantic_dir = semantic_dir
        if result_dir == None:
            self.result_dir = path.join(cnf.SEMANTIC_POINTER_DIR, SEMANTIC_NETWORK)
        else:
            self.result_dir = result_dir
            
    
    def parse(self):
        
        """
        output word_index, relation_graph
        """
        
        word_index_file = path.join(self.result_dir, cnf.WORD_INDEX_FILE)
       
        relation_graph_file =  path.join(self.result_dir, cnf.RELATION_GRAPH_FILE)
       
        index_word_map = {}
        
        relation_graph = {}
       
        
        id_index_map = self._generate_word_index()
                        
        
        for data in DATA_FILES:
            with open(path.join(self.semantic_dir, data)) as db:
                
                for line in db:
                    if re.match('\d{8}\s', line) != None:
                        
                        fields = line.split(DATA_FIELD_SEP)
                        word_id = fields[POS_WORD_ID]
                        
                        
                        word_num = int(fields[POS_WORD_NUM], 16)
                        word_index = id_index_map[word_id]
                        
                        word_list = []
                        word_end =  POS_WORD + WORD_LEN*word_num
                        for i in range(POS_WORD,word_end, WORD_LEN):
                            word_list.append(fields[i])
                            
                        index_word_map[word_index] = (word_id, word_list)
                        
                        relation_num = int(fields[word_end])
                        relation_end = word_end + 1 + relation_num * RELATION_LEN
                        
                        if word_index in relation_graph.keys():
                                    relation_words = relation_graph[word_index]
                        else:
                            relation_words = []
                            
                        for i in range(word_end+1, relation_end, RELATION_LEN):
                            symbol = fields[i]
                            if symbol in RELATION_SYMBOLS:
                                relation_word_id = fields[i+1]
                                
                                if relation_word_id in id_index_map:
                                    relation_word_index = id_index_map[relation_word_id]
                                
                                    relation_words.append(symbol + cnf.WORD_RELATION_SEP + \
                                                      relation_word_index)
                                    
                        relation_graph[word_index] = relation_words
                            
        
        with open(word_index_file, 'w') as wfile:
            for word_index in index_word_map.keys():
                
                desc = index_word_map[word_index]
                word_id = desc[0]
                words = desc[1]
                
                wfile.write(utl.to_line(word_index, word_id, words)) 
                
        with open(relation_graph_file, 'w') as rfile:
            for word_index in relation_graph.keys():
                
                relations = relation_graph[word_index]
                rfile.write(utl.to_line(word_index, relations))
                                              
                        
                     
                     
    def _generate_word_index(self):
        
        last_word_index = utl.get_word_index()
        id_index_map = {}
        
        index_max_file = path.join(self.result_dir, cnf.WORD_INDEX_MAX_FILE)
           
        for data in DATA_FILES:
            with open(path.join(self.semantic_dir, data)) as db:
                for line in db:
                    if re.match('\d{8}\s', line) != None:
                        fields = line.split(DATA_FIELD_SEP)
                        word_id = fields[POS_WORD_ID]
                        
                        last_word_index = utl.get_word_index(last_word_index)
                        id_index_map[word_id] = last_word_index
                        
        with open(index_max_file, 'w') as file:
            file.write(last_word_index)
    
        return id_index_map              
                    
                    

    def load_word_index(self):
        word_index_file = path.join(self.result_dir, cnf.WORD_INDEX_FILE)
        id_index_map = {}
        with open(word_index_file, 'r') as file:
            for line in file:
                fields = utl.parse_line(line)
                id_index_map[fields[1]] = fields[0]
                
        return id_index_map






          
            
            
    
    
                
              

        
    
    
    
    
    