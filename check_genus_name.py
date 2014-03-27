#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory
import sys

def get_values(line):
    full_name                = line.split(",")[0]
    genus_species            = line.split(",")[1]
    
    number_of_ranks          = len(full_name.split(";"))
    last_rank_from_full_name = full_name.split(";")[-1]
    genus_name               = genus_species.split()[0]
    
    return full_name, genus_species, number_of_ranks, last_rank_from_full_name, genus_name
    
def print_good_gen(line):
    if (number_of_ranks == 6 and last_rank_from_full_name == genus_name):
        print "GOOD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (number_of_ranks, last_rank_from_full_name, genus_name)    

def print_bad_gen(line):
    if (number_of_ranks == 6 and last_rank_from_full_name != genus_name):
        print "BAD: number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (number_of_ranks, last_rank_from_full_name, genus_name)    


fname = "mod_species3-27-14.csv"
with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:


        print_good_gen(line)
        print_bad_gen(line)
        # print "number_of_ranks = %s, last_rank_from_full_name = %s, genus_name = %s\n" % (number_of_ranks, last_rank_from_full_name, genus_name)    
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
