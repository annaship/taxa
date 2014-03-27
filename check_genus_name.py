#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

class Entry:
    def __init__(self, line):
        self.full_name                = line.split(",")[0].strip()
        self.genus_species            = line.split(",")[1].strip()

        self.number_of_ranks          = len(self.full_name.split(";"))
        self.last_rank_from_full_name = self.full_name.split(";")[-1]
        self.genus_name               = self.genus_species.split()[0]
        self.species_name             = ""
        if (len(self.genus_species.split()) == 2):
            self.species_name         = self.genus_species.split()[1]

    def is_genus(self):
        if len(self.genus_name) > 0:
            return self.genus_name[0].isupper() and re.search('[^A-Za-z]', self.genus_name) == None

        
    def is_species(self):
        if len(self.species_name) > 0:
            return self.species_name[0].islower() and re.search('[^a-z]', self.species_name) == None
        
    def good_gen(self):
        query = ""    
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name == self.genus_name):
            if self.is_species():
                new_name = self.full_name + ";" + self.species_name                
                query = 'UPDATE refssu_115_from_file SET taxonomy = "%s", taxslv_silva_modification = concat(taxslv_silva_modification, "; add species name from fullname"), taxonomy_source = "taxslv_silva_modification" WHERE taxslv_silva_modified = "%s" and silva_fullname = "%s" AND deleted = 0 AND taxonomy = "";' % (new_name, self.full_name, self.genus_species)
        return query


    def print_bad_gen(self):
        to_check = ""
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name != self.genus_name):
            # print "BAD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\nself.full_name = %s\nself.genus_species = %s\n" % (self.number_of_ranks, self.last_rank_from_full_name, self.genus_name, self.full_name, self.genus_species)    
            to_check = self.full_name + "," + self.genus_species
        return to_check
        
    def gen5(self):
        to_check = ""
        if (self.number_of_ranks == 5): 
            if self.is_genus():        
                to_check = self.full_name + "," + self.genus_species + "," + self.genus_name
        return to_check
        

# main
def print_good_species_into_file(): 
    f = open(add_species_file_name, 'w')
    all_queries_str = "\n".join(map(str, all_queries))
    f.write(all_queries_str)
    f.close()

def print_check_species_into_file():
    f = open(check_species_file_name, 'w')
    f.write("taxslv_silva_modified,silva_fullname,genus_name")
    all_to_check_str = "\n".join(map(str, set(all_to_check)))    
    f.write(all_to_check_str)
    f.close()

def print_conflict_name_into_file():
    f = open(conflict_name_file_name, 'w')
    f.write("taxslv_silva_modified,silva_fullname")
    conflict_name_str = "\n".join(map(str, set(conflict_name)))    
    f.write(conflict_name_str)
    f.close()



fname                   = "mod_species3-27-14.csv"
add_species_file_name   = "add_species.sql"
check_species_file_name = "check_species.csv"
conflict_name_file_name = "conflict_name.csv"
all_queries             = []
all_to_check            = []
conflict_name           = []
n = 0 

with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        # print n
        # print "=" * 10
        # n += 1
        row = Entry(line)
        
        # print "row.good_gen() = %s" % row.good_gen()

        all_queries.append(row.good_gen())
        conflict_name.append(row.print_bad_gen())
        all_to_check.append(row.gen5())
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
print_good_species_into_file()
print_check_species_into_file()
print_conflict_name_into_file()