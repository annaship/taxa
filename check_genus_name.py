#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

class Entry:
    def __init__(self, line):
        self.full_name                = line.split(",")[0]
        self.genus_species            = line.split(",")[1]

        self.number_of_ranks          = len(self.full_name.split(";"))
        self.last_rank_from_full_name = self.full_name.split(";")[-1]
        self.genus_name               = self.genus_species.split()[0]
        self.species_name             = ""
        if (len(self.genus_species.split()) == 2):
            self.species_name             = self.genus_species.split()[1]
        # except:
        #     print "genus_species with error: ", self.genus_species
        #     print "Unexpected error:", sys.exc_info()[0]
        #     raise

        
    def is_species(self):
        if len(self.species_name) > 0:
            return self.species_name[0].islower() and re.search('[^a-z]', self.species_name) == None
        
    def good_gen(self):
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name == self.genus_name):
            print "GOOD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\nself.full_name = %s\ngenus_species = %s\n" % (self.number_of_ranks, self.last_rank_from_full_name, self.genus_name, self.full_name, self.genus_species)    
            print "HERE: self.is_species()  = %s\n" % self.is_species() 
            if self.is_species():
                print "NEW name = "
                print self.full_name + ";" + self.species_name
                print "=" * 10

    def print_bad_gen(self):
        if (self.number_of_ranks == 6 and self.last_rank_from_full_name != self.genus_name):
            print "BAD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (self.number_of_ranks, self.last_rank_from_full_name, self.genus_name)    

    def add_good_species(self):
        pass


fname = "mod_species3-27-14.csv"
with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        row = Entry(line)
        row.good_gen()
        # row.print_bad_gen()
        # print "number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (number_of_ranks, last_rank_from_full_name, genus_name)    
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
