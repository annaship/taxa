#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

fname = sys.argv[1]

with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        count_fields              = line.split(",")[0].count(';')
        its_taxonomy_species      = line.split(",")[0].split(";")[-1]
        silva_fullname_species    = line.split(",")[-1]
        its_taxonomy_to_genus     = line.split(",")[0].split(";")[:-1]
        its_taxonomy_new_species  = ";".join(its_taxonomy_to_genus) + ";" + silva_fullname_species    
        
        if its_taxonomy_species.strip() != silva_fullname_species.strip() and count_fields == 6:
            # print "%s != %s" % (its_taxonomy_species, silva_fullname_species)
            print "%s, %s" % (line.strip(), its_taxonomy_new_species)
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
