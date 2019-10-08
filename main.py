# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 09:16:31 2019

@author: XLi83
"""

from wordnet import WordNetRelation, WordNetParser
from pointer import SemanticPointerConstructor, SemanticPointerSolver
import logging
import pointer
import utility as utl

def get_word_pointer(id_index_map, word_pointers,  word_id):
    word_pointer=[]
    word_index = id_index_map[word_id]
    if word_index in word_pointers.keys():
        word_pointer = word_pointers[word_index]
    
    else:
        print("cannot find pointer:%s"%word_index)
    return word_pointer, word_index
    

def main():
    
    logging.basicConfig(level=logging.INFO)
    semantic_network = 'wordnet'
    
    #relation = WordNetRelation()
    #relation.generate_semantic_pointers()
    
    parser = WordNetParser()
    #parser.parse()
    
    #constructor = SemanticPointerConstructor('wordnet')
    #constructor.construct()
           
    #solver = SemanticPointerSolver(semantic_network)
    #solver.solve()
    
    
    id_index_map = parser.load_word_index()
    
    relation_pointers = pointer.load_relation_pointers(semantic_network)
    word_pointers = pointer.load_word_pointers(semantic_network)
    
    relation_graph = pointer.load_relation_graph(semantic_network)
    print(type(relation_graph))
    
    word_id='02084071' #dog
    
    word_pointer, word_index = get_word_pointer(id_index_map, word_pointers, word_id)
    word_index = '0000024274'
    word_pointer = word_pointers[word_index]
    print(word_pointer)
    relations = relation_graph[word_index]
    
    print(pointer.compute_word_pointer(relations, relation_pointers, word_pointers))
    
  

if __name__ == '__main__':
    main()
