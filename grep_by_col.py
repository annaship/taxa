#! /opt/local/bin/python

# -*- coding: utf-8 -*-
# ~/BPC/today/silva/apr_15$ ./grep_by_col.py remove_from_conflict_and_check_manually.txt conflict_name_s.csv 4 ","


# Copyright (C) 2013, Marine Biological Laboratory
import sys
import re

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
        try:
            column_num_to_check = int(sys.argv[3].strip()) - 1
        except ValueError:
            column_num_to_check = 0
        
        field_separator            = sys.argv[4].strip()
        
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
            # genus_name = line.split(",")[3].strip()  
            genus_name = line.split(field_separator)[column_num_to_check].strip()  
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