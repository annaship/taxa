#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory

# SELECT DISTINCT accession_id, taxslv_silva_modified, silva_fullname
# FROM refssu_115_from_file 
#  WHERE 
# deleted = 0
# AND taxonomy = ""
# AND silva_fullname != ""
# ORDER BY silva_fullname


import sys
import re

class Entry:
    def __init__(self, line):
        self.accession_id             = line.split(",")[0].strip()
        self.full_name                = line.split(",")[1].strip()
        try:
            self.genus_species            = line.split(",")[2].strip()
        except:
            print "HERE1: line with error: ", line
            print "Unexpected error:", sys.exc_info()[0]
            raise
        

        self.number_of_ranks          = len(self.full_name.split(";"))
        self.last_rank_from_full_name = self.full_name.split(";")[-1]
        self.genus_name               = self.genus_species.split()[0]
        self.species_name             = ""
        if (len(self.genus_species.split()) == 2):
            self.species_name         = self.genus_species.split()[1]
        if (len(self.genus_species.split()) >= 2):
            self.species_name         = self.genus_species.split()[1]

    def is_genus(self):
        if len(self.genus_name) > 0:
            return self.genus_name[0].isupper() and re.search('[^A-Za-z]', self.genus_name) == None

        
    def is_species(self):
        if len(self.species_name) > 0:
            return self.species_name[0].islower() and re.search('[^a-z]', self.species_name) == None
        
    def good_gen(self):
        query = ""    
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name == self.genus_name and self.is_species()):
                new_name = self.full_name + ";" + self.species_name                
                query = 'UPDATE refssu_115_from_file SET taxonomy = "%s", taxslv_silva_modification = concat(taxslv_silva_modification, "; add species name from fullname"), taxonomy_source = "taxslv_silva_modification" WHERE taxslv_silva_modified = "%s" and silva_fullname = "%s" AND deleted = 0 AND taxonomy = "";' % (new_name, self.full_name, self.genus_species)
        return query


    def conflict_genus(self):
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name != self.genus_name and self.is_genus()):
            return True
        
    def gen5(self):
        if (self.number_of_ranks == 5 and self.is_genus()): 
            return True

    def less_ranks(self):
        if (self.number_of_ranks < 5 and self.is_genus()): 
            return True
        

# main
def print_good_species_into_file(): 
    f = open(add_species_file_name, 'w')
    all_queries_str = "\n".join(map(str, set(all_queries)))
    f.write(all_queries_str)
    f.close()

def print_check_species_into_csv(list_name, filename_base):
    check_species_file_name = filename_base + ".csv"
    f = open(check_species_file_name, 'w')
    f.write("accession_id,taxslv_silva_modified,silva_fullname,genus_name,last_rank\n")
    list_name_str = "\n".join(map(str, set(list_name)))    
    f.write(list_name_str)
    f.close()

fname                   = "id_mod_species_4-14-14.csv"
add_species_file_name   = "add_species.sql"
all_queries             = []
all_to_check            = []
conflict_name           = []
less_ranks_ask          = []
n = 0 

with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        row      = Entry(line)
        to_check = ""
        
        all_queries.append(row.good_gen())
        to_check = row.accession_id + "," + row.full_name + "," + row.genus_species + "," + row.genus_name + "," + row.last_rank_from_full_name            
        if (row.conflict_genus()):
            conflict_name.append(to_check)
        if (row.gen5()):
            all_to_check.append(to_check)
        if (row.less_ranks()):
            less_ranks_ask.append(to_check)
            
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
print_good_species_into_file()
print_check_species_into_csv(all_to_check, 'all_to_check')
print_check_species_into_csv(conflict_name, 'conflict_name')
print_check_species_into_csv(less_ranks_ask, 'less_ranks_ask')
