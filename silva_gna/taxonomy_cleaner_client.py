#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2015, Marine Biological Laboratory
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.

import argparse
from taxonomy_cleaner import Taxonomy

# usage = "usage: %prog [options] arg1, for example: %prog -p -j file_name"
parser = argparse.ArgumentParser(usage='%(prog)s [options], for example: %(prog)s -p -j file_name', description='Works with names, cleans taxonomy')

parser.add_argument('-b', '--get_list_before_binomial', action="count", default=0, help = 'Run get_list_before_binomial')
parser.add_argument('-f', '--make_clean_taxonomy_from_gna_api_res_preff', action="count", default=0, help = 'Run make_clean_taxonomy_from_gna_api_res_preff (using resolver\'s result in json, :preferred_data_sources => "4|11|5", e.g. NCBI, GBIF and Index Fungorum) - doesn\'t work')

parser.add_argument('-j', dest = "json_res", help = 'GNA result file in json format, e.g. small_names_list_gna_result.json')

parser.add_argument('-i', '--tax_in', dest = "tax_infile", 
      help = 'Tab delimited taxonomy input file: 10437\t"Bacteria;Actinobacteria;Actinobacteria;Micromonosporales;Micromonosporaceae;Micromonospora;Micromonospora stanfordense"')

parser.add_argument('-g', '--get_good_silva', action="count", default=0, help = 'Run get_good_silva')
parser.add_argument('-l', '--get_list_of_good_binomials', action="count", default=0, help = 'Run get_list_of_good_binomials')

parser.add_argument('-p', '--make_clean_taxonomy_from_partial', action="count", default=0, help = 'Run make_clean_taxonomy_from_partial (using resolver\'s result in json)')

parser.add_argument('-r', '--get_list_last_good', action="count", default=0, help = 'Run get_list_last_good on the rest of taxa')

parser.add_argument('-u', '--get_list_before_uncultured', action="count", default=0, help = 'Run get_list_before_uncultured')



args = parser.parse_args()

# print "args.get_good_silva = %s" % args.get_good_silva

tax_class = Taxonomy()


# tax_class.process(args)
# tax_class.make_clean_taxonomy_from_partial(args.json_res)
if (args.get_good_silva == 1):
  tax_class.get_good_silva(args.tax_infile)

if (args.get_list_of_good_binomials == 1):
  tax_class.separate_binomials(args.tax_infile)

if (args.make_clean_taxonomy_from_partial == 1):
  tax_class.make_clean_taxonomy_from_partial(args.json_res)

if (args.get_list_before_uncultured == 1):
    tax_class.get_list_before_uncultured(args.tax_infile)

if (args.get_list_before_binomial == 1):
    tax_class.get_list_before_binomial(args.tax_infile)

