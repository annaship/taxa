#! /opt/local/bin/python

# -*- coding: utf-8 -*-
# ~/BPC/today/silva/apr_10$ ./change_fungi_species.py fungi_to_check_genus.txt.check.in_its.csv >temp.csv

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

class ItsCompare:
    def __init__(self):
        self.its_taxonomy              = ""
        self.taxslv_silva_modified_old = ""
        self.silva_fullname            = ""
        self.silva_fullname_species    = ""
        self.count_fields              = ""
        self.its_taxonomy_species      = ""
        self.its_taxonomy_to_genus     = ""
        self.its_taxonomy_new_species  = ""
        self.its_taxonomy_add_species  = ""
        self.line                      = ""
        
    def make_update_query(self):
      query = "UPDATE refssu_115_from_file \
        SET taxslv_silva_modified = replace(taxslv_silva_modified, '" + self.taxslv_silva_modified_old + "', '" + self.taxslv_silva_modified_new + "'), \
            taxslv_silva_modification = concat(taxslv_silva_modification, '; add ranks by Unite') \
        WHERE taxslv_silva_modified = '" + self.taxslv_silva_modified_old + "'\
            AND silva_fullname = '" + self.silva_fullname + "'\
        ;\
      "
      return query

    def print_csv(self):
        if self.its_taxonomy_species != self.silva_fullname_species and self.count_fields == 6:
            # Eukarya;Fungi_Basidiomycota;Pucciniomycetes;Pucciniales;Pucciniaceae;Gymnosporangium;clavariiforme vs. juniperi-virginianae
            self.taxslv_silva_modified_new = self.its_taxonomy_new_species
            print "%s, %s" % (self.line.strip(), self.taxslv_silva_modified_new)
        elif its_taxonomy_species != silva_fullname_species and count_fields == 5 and its_taxonomy_species != "":
            # Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia Eukarya;Fungi_Ascomycota;Lecanoromycetes    Evernia prunastri   prunastri    Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia
            self.taxslv_silva_modified_new = self.its_taxonomy_add_species
            print "%s, %s" % (self.line.strip(), self.taxslv_silva_modified_new)
        else:
            print "%s, %s" % (self.line.strip(), self.its_taxonomy)
            self.taxslv_silva_modified_new = self.its_taxonomy
            # Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;nigeriensis vs. Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;
        
        
        
if __name__ == '__main__':

    fname = sys.argv[1]

    with open(fname) as f:
        content = f.readlines()
    
    for line in content:
        self.line = line
        try:
            self.its_taxonomy              = line.split(",")[0].strip()
            self.taxslv_silva_modified_old = line.split(",")[1].strip()
            self.silva_fullname            = line.split(",")[2].strip()
            self.silva_fullname_species    = line.split(",")[-1].strip()

            self.count_fields              = self.its_taxonomy.count(';')
            self.its_taxonomy_species      = self.its_taxonomy.split(";")[-1].strip()
            self.its_taxonomy_to_genus     = self.its_taxonomy.split(";")[:-1]
            self.its_taxonomy_new_species  = ";".join(self.its_taxonomy_to_genus) + ";" + self.silva_fullname_species if len(self.silva_fullname_species) > 0 else ";".join(its_taxonomy_to_genus)
            # Apiosordaria
            self.its_taxonomy_add_species  = self.its_taxonomy + ";" + self.silva_fullname_species if len(self.silva_fullname_species) > 0 else self.its_taxonomy
        
            print "+" * 10
            print self.make_update_query()
            
        except:
            print "line with error: ", line
            print "Unexpected error:", sys.exc_info()[0]
            raise
