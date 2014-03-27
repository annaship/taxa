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

        
    def is_species(self):
        if len(self.species_name) > 0:
            return self.species_name[0].islower() and re.search('[^a-z]', self.species_name) == None
        
    def good_gen(self):
        query = ""    
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name == self.genus_name):
            # print "GOOD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\nself.full_name = %s\ngenus_species = %s\n" % (self.number_of_ranks, self.last_rank_from_full_name, self.genus_name, self.full_name, self.genus_species)    
            # print "HERE: self.is_species()  = %s\n" % self.is_species() 
            if self.is_species():
                new_name = self.full_name + ";" + self.species_name
                print "NEW name = %s\n" % new_name                
                
                query = 'UPDATE refssu_115_from_file SET taxonomy = "%s", taxslv_silva_modification = concat(taxslv_silva_modification, "; add species name from fullname"), taxonomy_source = "taxslv_silva_modification" WHERE taxslv_silva_modified = "%s" and silva_fullname = "%s" AND deleted = 0 AND taxonomy = "";' % (new_name, self.full_name, self.genus_species)
                print "query:\n", query
                # print(query, file = self.add_species_file_name)
        return query

    def print_bad_gen(self):
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name != self.genus_name):
            print "BAD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (self.number_of_ranks, self.last_rank_from_full_name, self.genus_name)    

    def add_good_species(self):
        pass


fname                 = "mod_species3-27-14.csv"
add_species_file_name = "add_species.sql"
all_queries          = []
n = 0 

with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        print n
        print "=" * 10
        n += 1
        row = Entry(line)
        
        print "row.good_gen() = %s" % row.good_gen()

        all_queries.append(row.good_gen())
        # row.print_bad_gen()
        # print "number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (number_of_ranks, last_rank_from_full_name, genus_name)    
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
    

f = open(add_species_file_name, 'w')
print "HERE11"
print all_queries
print "all_queries.type = ", type(all_queries)

all_queries_str = "\n".join(map(str, all_queries))

print all_queries_str
print "all_queries_str.type = ", type(all_queries_str)

f.write(all_queries_str)
f.close()
