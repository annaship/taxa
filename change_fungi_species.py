#! /opt/local/bin/python

# -*- coding: utf-8 -*-
# ~/BPC/today/silva/apr_10$ ./change_fungi_species.py fungi_to_check_genus.txt.check.in_its.csv >temp.csv

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

fname = sys.argv[1]

with open(fname) as f:
    content = f.readlines()
    
for line in content:
    try:
        its_taxonomy              = line.split(",")[0].strip()
        count_fields              = its_taxonomy.count(';')
        its_taxonomy_species      = its_taxonomy.split(";")[-1].strip()
        silva_fullname_species    = line.split(",")[-1].strip()
        its_taxonomy_to_genus     = its_taxonomy.split(";")[:-1]
        its_taxonomy_new_species  = ";".join(its_taxonomy_to_genus) + ";" + silva_fullname_species if len(silva_fullname_species) > 0 else ";".join(its_taxonomy_to_genus)
        # Apiosordaria
        its_taxonomy_add_species  = its_taxonomy + ";" + silva_fullname_species if len(silva_fullname_species) > 0 else its_taxonomy
        
        
        if its_taxonomy_species != silva_fullname_species and count_fields == 6:
            # Eukarya;Fungi_Basidiomycota;Pucciniomycetes;Pucciniales;Pucciniaceae;Gymnosporangium;clavariiforme vs. juniperi-virginianae
            print "%s, %s" % (line.strip(), its_taxonomy_new_species)
        elif its_taxonomy_species != silva_fullname_species and count_fields == 5 and its_taxonomy_species != "":
            # Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia Eukarya;Fungi_Ascomycota;Lecanoromycetes    Evernia prunastri   prunastri    Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia
            print "%s, %s" % (line.strip(), its_taxonomy_add_species)
        else:
            print "%s, %s" % (line.strip(), its_taxonomy)
            # Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;nigeriensis vs. Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;
            
            
    except:
        print "line with error: ", line
        print "Unexpected error:", sys.exc_info()[0]
        raise
