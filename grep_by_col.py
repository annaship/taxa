#! /opt/local/bin/python

# -*- coding: utf-8 -*-
# ~/BPC/today/silva/apr_10$ ./change_fungi_species.py fungi_to_check_genus.txt.check.in_its.csv >temp.csv

# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

# class ItsCompare:
#     def __init__(self):
#         self.its_taxonomy              = ""
#         self.taxslv_silva_modified_old = ""
#         self.silva_fullname            = ""
#         self.silva_fullname_species    = ""
#         self.count_fields              = ""
#         self.its_taxonomy_species      = ""
#         self.its_taxonomy_to_genus     = ""
#         self.its_taxonomy_new_species  = ""
#         self.its_taxonomy_add_species  = ""
#         self.line                      = ""
#         
#     def make_update_query(self):
#       query = "UPDATE refssu_115_from_file \
#         SET taxslv_silva_modified = replace(taxslv_silva_modified, '" + self.taxslv_silva_modified_old + "', '" + self.taxslv_silva_modified_new + "'), \
#             taxslv_silva_modification = concat(taxslv_silva_modification, '; add ranks by Unite') \
#         WHERE taxslv_silva_modified = '" + self.taxslv_silva_modified_old + "'\
#             AND silva_fullname = '" + self.silva_fullname + "'\
#         ;\
#       "
#       return query
# 
#     def print_csv(self):
#         if self.its_taxonomy_species != self.silva_fullname_species and self.count_fields == 6:
#             # Eukarya;Fungi_Basidiomycota;Pucciniomycetes;Pucciniales;Pucciniaceae;Gymnosporangium;clavariiforme vs. juniperi-virginianae
#             self.taxslv_silva_modified_new = self.its_taxonomy_new_species
#             print "%s, %s" % (self.line.strip(), self.taxslv_silva_modified_new)
#         elif its_taxonomy_species != silva_fullname_species and count_fields == 5 and its_taxonomy_species != "":
#             # Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia Eukarya;Fungi_Ascomycota;Lecanoromycetes    Evernia prunastri   prunastri    Eukarya;Fungi_Ascomycota;Lecanoromycetes;Lecanorales;Parmeliaceae;Evernia
#             self.taxslv_silva_modified_new = self.its_taxonomy_add_species
#             print "%s, %s" % (self.line.strip(), self.taxslv_silva_modified_new)
#         else:
#             print "%s, %s" % (self.line.strip(), self.its_taxonomy)
#             self.taxslv_silva_modified_new = self.its_taxonomy
#             # Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;nigeriensis vs. Eukarya;Fungi_Ascomycota;Sordariomycetes;Sordariales;Lasiosphaeriaceae;Apiosordaria;
        

def read_file(filename):
    with open(filename) as f:
        content = f.read().splitlines()
    return content

def write_file(filename, to_write):
    f = open(filename,'w')
    f.write(to_write)
    f.close()
    
        
        
if __name__ == '__main__':
    try:
        list_to_take_out_name      = sys.argv[1].strip()
        file_to_take_out_from_name = sys.argv[2].strip()
        file_to_take_out_from_name = sys.argv[3].strip()
        file_to_take_out_from_name = sys.argv[4].strip()
        output_file_name           = file_to_take_out_from_name + ".out.csv"
        deleted_val_file_name      = file_to_take_out_from_name + ".del.csv"
    except:
        print "Arguments error: ", sys.argv
        print "Unexpected error:", sys.exc_info()[0]
        raise
    
    output_val                 = []
    deleted_val_fil            = []
    

    list_to_take_out      = read_file(list_to_take_out_name)
    file_to_take_out_from = read_file(file_to_take_out_from_name)

    for line in file_to_take_out_from:
        try:
            genus_name = line.split(",")[3].strip()  
            if genus_name in list_to_take_out:
                deleted_val_fil.append(line)
            else:
                output_val.append(line)
        except:
            print "line with error: ", line
            print "Unexpected error:", sys.exc_info()[0]
            raise
    
    write_file(output_file_name,      "\n".join(output_val))
    write_file(deleted_val_file_name, "\n".join(deleted_val_fil))