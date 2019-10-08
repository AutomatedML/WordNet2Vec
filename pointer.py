# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 10:07:33 2019

@author: XLi83
"""
import config as cnf
from os import path
import utility as utl
import numpy as np
import logging

def load_relation_pointers(semantic_network):
        relation_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        semantic_network, cnf.SEMANTIC_POINTER_RELATION_FILE)
        
        relation_pointers = utl.load_pointers(relation_file)
        return relation_pointers
        
def load_word_pointers(semantic_network):
    word_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                    semantic_network, cnf.SEMANTIC_POINTER_WORD_FILE)
    word_pointers = utl.load_pointers(word_file)
    
    variable_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                    semantic_network, cnf.SEMANTIC_POINTER_VARIABLE_FILE)
    variable_pointers = utl.load_pointers(variable_file)
    word_pointers.update(variable_pointers)
    
    return word_pointers
    

def compute_word_pointer(relations, relation_pointer_map, word_pointer_map):
    word_pointer = np.zeros(cnf.SEMANTIC_POINTER_DIMENSION)
    for word_index in relations.keys():
        symbol = relations[word_index]
        
        relation_pointer = relation_pointer_map[symbol]
        pointer = word_pointer_map[word_index]
        word_pointer = word_pointer + utl.conv(relation_pointer, pointer)
        
    return word_pointer

def load_relation_graph(semantic_network):
    relation_graph_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                    semantic_network, cnf.RELATION_GRAPH_FILE)
    relation_graph={}
    with open(relation_graph_file, 'r') as file:
        for line in file:
            
            word_index, relations = utl.parse_relation(line)
            
            relation_graph[word_index] = relations
    logging.debug("loaded relation graph:%s"%relation_graph)
    return relation_graph
    

class Equation:
    def __init__(self, pointers, variables, relations_to_solve):
        self.pointers = pointers
        self.variables = variables
        self.relations_to_solve = relations_to_solve

class SemanticPointerConstructor:
    relation_pointer_map=None
    word_pointer_map={}
    
    def __init__(self, semantic_network):
        self.semantic_network = semantic_network
    
    
    
    
    
    def construct(self):
        """
        output: equations, words
        """
       
        relation_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        self.semantic_network, cnf.SEMANTIC_POINTER_RELATION_FILE)
        word_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        self.semantic_network, cnf.SEMANTIC_POINTER_WORD_FILE)
        equation_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        self.semantic_network, cnf.SEMANTIC_POINTER_EQUATION_FILE)
        
        relation_graph = load_relation_graph(self.semantic_network)
        
        
        self.relation_pointer_map = utl.load_pointers(relation_file)
        
        removable = True
        remove_keys = []
        #remove words with no relations or with relation words which can be determined
        while removable:
            removable = False
            for key in remove_keys:
                relation_graph.pop(key)
            remove_keys = []
            for word_index in relation_graph.keys():
                relations = relation_graph[word_index]
                if (len(relations) == 0): #no relations
                    removable = True
                    pointer = utl.generate_random_vector()
                    self.word_pointer_map[word_index] = pointer
                    remove_keys.append(word_index)
                    
                else: #all relation words have pointers
                    has_pointer = True
                    
                    for key in relations.keys():
                        
                        if key not in self.word_pointer_map.keys():
                            has_pointer = False
                    if (has_pointer):
                        word_pointer = compute_word_pointer(\
                                    relations, self.relation_pointer_map, self.word_pointer_map)
                        self.word_pointer_map[word_index] = word_pointer
                        remove_keys.append(word_index)
                        removable = True
        logging.debug("save word pointers:%s"%self.word_pointer_map)               
        utl.save_pointers(self.word_pointer_map, word_file)
        
        logging.debug("reduced relation graph%s"%relation_graph)
        
        n = 0
        index_id_map = {}
        id_index_map = {}
        for key in relation_graph.keys():
            index_id_map[key] = n
            id_index_map[n] = key
            n = n + 1
           
        #construct adjacency matrix    
        adjacency_matrix = np.zeros((n, n))
        
        merged_relations = []
        
        for word_index in relation_graph.keys():
            relations = relation_graph[word_index]
            word_id = index_id_map[word_index]
            for key in relations.keys():
                if key in index_id_map.keys():
                    relation_id = index_id_map[key]
            adjacency_matrix[word_id][relation_id] = 1
            
        
        
        #merge dependent variables
        visited_vars = np.zeros(n)
        
        for i in range(n):
            if visited_vars[i] == 0:
                check_vars = []
                
                visited_vars = np.zeros(n)
                
                check_vars.append(i)
                merge_relation = []
                
                while len(check_vars) > 0 :
                    
                    var = check_vars[0]
                    if visited_vars[var] == 0:
                        visited_vars[var] = 1
                        merge_relation.append(id_index_map[var])
                        for j in range(n):
                            if adjacency_matrix[var][j] == 1 and \
                            j not in check_vars and visited_vars[j] == 0:
                                check_vars.append(j)
                        for j in range(n):
                            if adjacency_matrix[j][var] == 1 and \
                            j not in check_vars and visited_vars[j] == 0:
                                 check_vars.append(j)      
                    check_vars.remove(var)
                   
                    
                    
                merged_relations.append(merge_relation)  
                
        #save equations        
        i = 1
        with open(equation_file, 'w') as rfile:        
            for variables in merged_relations:
                relations_to_solve={}
                
                pointers = []
                for var in variables:
                    relations = relation_graph[var]
                    relations_to_solve[var] = relations
                    
                    for word in relations.keys():
                        if word in self.word_pointer_map.keys() and \
                            word not in pointers:
                                pointers.append(word)
                                
                rfile.write(utl.to_line(cnf.EQUATION_START, i, 2 + len(relations_to_solve)))            
                rfile.write(utl.to_line(variables))
                rfile.write(utl.to_line(pointers))
                for  word_index in relations_to_solve:
                    rfile.write(utl.to_line(word_index, relations_to_solve[word_index]))
                i = i + 1
                 

class SemanticPointerSolver:
    
    relation_pointers = None
    word_pointers = None
    
    def __init__(self, semantic_network):
        self.semantic_network = semantic_network
        
    def _solve_equation(self, lines):
        
        relation_start_line = 2
        
        variables = utl.parse_list(lines[0])
        pointers = utl.parse_list(lines[1])
        
        num_col = len(variables)
        num_row = len(lines) - relation_start_line
               
        coefficients = {}
        
        for i in range(0, len(lines)-relation_start_line):
            line = lines[i + relation_start_line]
            
            word_index, relations = utl.parse_relation(line)
            
            constant = utl.get_zero_pointer()
            
            for j in range(0, num_col):
                var = variables[j]
                if var == word_index:
                    coefficients[(i, j)] = utl.get_identity_pointer()
                else:
                    
                    if var in relations.keys():
                        relation = relations[var]
                        relation_pointer = self.relation_pointers[relation]
                       
                        
                        coefficients[(i, j)] = -relation_pointer
                    else:
                        coefficients[(i, j)] = utl.get_zero_pointer()
                        
            for key in relations.keys():
                
                if key in self.word_pointers.keys():
                    relation = relations[key]
                    relation_pointer = self.relation_pointers[relation]
                    key_pointer = self.word_pointers[key]
        
                    constant = constant + utl.conv(relation_pointer,\
                                       key_pointer)
                        
            coefficients[(i, j+1)] = constant    
            
        
        
        logging.debug("coefficinets:%s"%coefficients)
        
        variable_pointers = self._gaussian_elimination(coefficients, num_row, num_col + 1) 
       
        variable_pointer_map = {}
        
        for i in range(num_col):
            variable_pointer_map[variables[i]] = variable_pointers[i]
        
        return variable_pointer_map
        
        
            
        
       
    def _gaussian_elimination(self, coefficients, num_row, num_col):
        
        pivot_row = 0
        pivot_col = 0
        
        
        while pivot_row < num_row-1 and pivot_col < num_col-1:
            
            row = -1
            for i in range(pivot_row, num_row):
                if utl.is_identity_pointer(coefficients[(i, pivot_col)]):
                    row = i
                    break
            
            if row == -1:
                for i in range(pivot_row, num_row):
                    if not utl.is_zero_pointer(coefficients[(i, pivot_col)]):
                        row = i
                        break
             
            for j in range(num_col):
                tmp = coefficients[(row, j)]
                coefficients[(row, j)] = coefficients[(pivot_row, j)]
                coefficients[(pivot_row, j)] = tmp
            
            for j in range(pivot_row + 1, num_row):
                if not utl.is_zero_pointer(coefficients[(j, pivot_col)]):
                    r = utl.conv(coefficients[(j, pivot_col)], \
                                              utl.invert_pointer(coefficients[(pivot_row, pivot_col)]))
                    coefficients[(j, pivot_col)] = utl.get_zero_pointer()
                    for k in range(pivot_col + 1, num_col):
                        coefficients[(j,k)] = coefficients[(j,k)] - \
                        utl.conv(r, coefficients[(pivot_row, k)])
                    
            
           
            pivot_row = pivot_row + 1
            pivot_col = pivot_col + 1
            
        
            
        n = num_row - 1
        
        for j in range(num_col-2, -1, -1):
            
            coefficients[(n, num_col - 1)] = utl.conv( \
                         utl.invert_pointer(coefficients[(n, j)]), \
                         coefficients[(n, num_col - 1)])
            coefficients[(n, j)] = utl.get_identity_pointer()
            for i in range(n-1, -1, -1):
                coefficients[(i, num_col - 1)] = coefficients[(i, num_col - 1)] - \
                        utl.conv(coefficients[(n, num_col - 1)], \
                         coefficients[(i, j)])
                coefficients[(i, j)] = utl.get_zero_pointer()
                
            n = n - 1
            
        pointers=[]
        
       
        for i in range(0, num_row):
           
            pointers.append(coefficients[(i, num_col - 1)])
            
        logging.debug("pointers:%s"%pointers)
        
        return pointers
        
    
        
    def solve(self):
        
        self.relation_pointers = load_relation_pointers(self.semantic_network)
        self.word_pointers = load_word_pointers(self.semantic_network)
        
        equation_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        self.semantic_network, cnf.SEMANTIC_POINTER_EQUATION_FILE)
        
        variable_file = path.join(cnf.SEMANTIC_POINTER_DIR, \
                                        self.semantic_network, cnf.SEMANTIC_POINTER_VARIABLE_FILE)
        
        variable_pointer_map = {}
        
        with open(equation_file, 'r') as efile:
            line = efile.readline()
            
            while line:
                
                if line.startswith(cnf.EQUATION_START):
                    print(line)
                    fields = line.split(cnf.FIELD_SEP)
                    
                    equation_len = int(fields[cnf.EQUATION_LEN_POS])
                   
                    equation_line_num = 0
                    equation_lines = []
                else:
                    equation_line_num = equation_line_num + 1
                    equation_lines.append(line)
                    
                    if equation_line_num == equation_len:
                        
                        pointers = self._solve_equation(equation_lines)
                        variable_pointer_map.update(pointers)
                    
                line = efile.readline()
                
        utl.save_pointers(variable_pointer_map, variable_file)       
                           




        
    
                
