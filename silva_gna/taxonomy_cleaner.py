#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2015, Marine Biological Laboratory
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
# 26102   "Bacteria;Cyanobacteria;Chloroplast;putative agent of rhinosporidiosis" ???Why Bacteria
# 53416   "Bacteria;Proteobacteria;Alphaproteobacteria;Sphingomonadales;Sphingomonadaceae;Sphingobium;Sphingomonas sp."
# 78264   "Bacteria;Proteobacteria;Gammaproteobacteria;Vibrionales;Vibrionaceae;Vibrio;Vibrio halioticoli"
# 56239   "Bacteria;Proteobacteria;Betaproteobacteria;Burkholderiales;Burkholderiaceae;Limnobacter;Limnobacter thiooxidans"
# 77226   "Bacteria;Proteobacteria;Gammaproteobacteria;Pseudomonadales;Pseudomonadaceae;Pseudomonas;Pseudomonas syringae pv. actinidiae"

''' 
todo:
 *) by arg - clean part taxonomy or make old taxonomies or what
 *) send partial_taxonomy_result file name by args
 *) check species - if genus is repeated - remove
 *) remove unknown rank_name ("Unknown Family" etc)
 *) check all indexes, if between valid ranks - remove and add to a separate file (extra_ranks)
 done) old_taxonomy_partial - get binomial, run GNA API, get our ranks, add to taxonomy
 *) add time benchmark to different parts
 *) check which "weird" ids are not in partial
 *) what to do with Candidatus
 done) upload to the taxonomy table clean ncbi taxonomy with ids
 done) if no NCBI look for GBIF (11 GBIF Backbone Taxonomy) u'is_known_name': False
 *) get all double genus names and ask Silva people (Xanthomonadaceae, Alcaligenaceae)
'''

import argparse
import json
import sys

class Taxonomy:
    
    def __init__(self):
        self.old_taxonomy_good    = {}
        self.old_taxonomy_weird   = {}
        self.old_taxonomy_weird_by_species = {}
        self.old_taxonomy_partial = {}
        self.separated_species_taxonomy = {}
        self.taxonomy_partial_file_name = "taxonomy_partial.txt"
        self.taxonomy_partial_binomials_file_name = "taxonomy_partial_binomials.txt"
        self.taxonomy_weird_file_name   = "taxonomy_weird.txt"
        self.taxonomy_good_file_name    = "taxonomy_good.txt"
        self.classification_unknown_file_name = "classification_unknown.txt"
        
        ordered_names1 = ["kingdom", "phylum", "class", "order", "family", "genus", "species"]
        ordered_names2 = ["superkingdom", "kingdom", "phylum", "class", "order", "family", "genus", "species"]
        self.ordered_names = ordered_names2
        # self.bad_value     = "Fungi", "unculturedfungus", "unidentified", "sp", "sp.", "unculturedsoil_fungus", "unidentified_sp.", "unculturedcompost_fungus", "unculturedectomycorrhizal_fungus"
        self.bad_value     =  ["unidentified", "sp.", "cf.", "aff.", "gen.", "nr.", "str.", "genomosp.", "n.", "unidentified_sp.", "genosp.", "(sen."]
        
        self.gna_result                = {}
        self.ncbi_classification       = []
        self.ncbi_classification_by_sp = {}
        self.ncbi_classification_by_sp_good = {}
        self.classification_unknown    = []
        self.taxonomy                  = {}
        

    def uniq_array(self, arr):
       # order preserving
       noDupes = []
       [noDupes.append(i) for i in arr if not noDupes.count(i)]
       return noDupes

    def check_if_super_sub(self, split_tax, taxon):
        # or taxon.endswith("idea")
        sub_sup_index = None
        if taxon.endswith("acea") or taxon.endswith("anae") or taxon.endswith("enalia") or taxon.endswith("enea") or taxon.endswith("enion") or taxon.endswith("etosum") or taxon.endswith("idanae") or taxon.endswith("idinae") or taxon.endswith("inae") or taxon.endswith("indae") or taxon.endswith("ineae") or taxon.endswith("mycetidae") or taxon.endswith("mycia") or taxon.endswith("mycotera") or taxon.endswith("mycotina") or taxon.endswith("obionta") or taxon.endswith("oidea") or taxon.endswith("oideae") or taxon.endswith("ophytanae") or taxon.endswith("virinae") or taxon.endswith("viroinae"):
            sub_sup_index = split_tax.index(taxon)
            # if taxon != split_tax[-1]:
                # print "split_tax = %s,\n taxon = %s, sub_sup_index = %s" % (split_tax, taxon, sub_sup_index)
        return sub_sup_index
        
    def add_simple_rank(self, tax_line, taxon, rank):
        tax_line[rank]  = taxon
        return tax_line

    def add_to_weird(self, split_tax, taxon, id_tax, rank_index):
        t_index = split_tax.index(taxon)
        if (t_index != rank_index):
            self.old_taxonomy_weird[id_tax] = split_tax    

    def add_tax_line_to_taxonomy(self, tax_line, split_tax, id_tax):
        if len(tax_line) != len(split_tax):
            self.old_taxonomy_partial[id_tax] = (tax_line, split_tax)
            self.old_taxonomy_partial[id_tax] = (tax_line, split_tax)
        else:
            self.old_taxonomy_good[id_tax]  = tax_line

    def clean_tsv_line(self, f_line):
      tax_line_split = f_line.strip().split("\t")
      split_tax      = tax_line_split[1].strip('"').split(';')
      id_tax         = tax_line_split[0]
      return (split_tax, id_tax)
      
    def make_taxa_dict(self, tax_infile):
        for line in open(tax_infile):
            tax_line = {}
            split_tax, id_tax = self.clean_tsv_line(line)
            # tax_line_split = line.strip().split("\t")
            # split_tax = tax_line_split[1].strip('"').split(';')
            # id_tax    = tax_line_split[0]

            family_index = None

            tax_line = self.add_simple_rank(tax_line, split_tax[0], "kingdom")
            if (" " in split_tax[-1]) or (split_tax[-1] == 'unidentified'):
                tax_line = self.add_simple_rank(tax_line, split_tax[-1], "species")
            
            for taxon in split_tax:
                if taxon != split_tax[-1]:
                    sub_sup_index = self.check_if_super_sub(split_tax, taxon)
                    if sub_sup_index >= 0:
                      self.old_taxonomy_weird[id_tax] = split_tax
                        
                    elif taxon.endswith("opsida"):
                      tax_line = self.add_simple_rank(tax_line, taxon, "class")
                      self.add_to_weird(split_tax, taxon, id_tax, 2)
                      
                    elif taxon.endswith("ales"):
                      tax_line = self.add_simple_rank(tax_line, taxon, "order")
                      self.add_to_weird(split_tax, taxon, id_tax, 3)

                    elif taxon.endswith("aceae"):
                      tax_line = self.add_simple_rank(tax_line, taxon, "family")
                      self.add_to_weird(split_tax, taxon, id_tax, 4)
                      family_index = split_tax.index(taxon)

            # print "======"
            # print "family_index = %s" % (family_index)
            if (family_index == 4):
              tax_line = self.add_simple_rank(tax_line, split_tax[1], "phylum")
              tax_line = self.add_simple_rank(tax_line, split_tax[5], "genus")
         
              if not 'class' in tax_line:
                tax_line = self.add_simple_rank(tax_line, split_tax[2], "class")
              if not 'order' in tax_line:
                  tax_line = self.add_simple_rank(tax_line, split_tax[3], "order")
        
            self.add_tax_line_to_taxonomy(tax_line, split_tax, id_tax)

            # if (class_index and order_index and (class_index - order_index) > 1):
            #     print "\n======\nsplit_tax = %s" % (split_tax)
            #     print "class_index = %s" % (class_index)
            #     print "order_index = %s" % (order_index)
            #     print "split_tax[class_index:order_index] = %s" % (split_tax[class_index:order_index])
            #     print "split_tax[class_index] = %s" % (split_tax[class_index])
            #     print "split_tax[order_index] = %s" % (split_tax[order_index])
            #     print "class_index - order_index = %s" % (class_index - order_index)
            # 
            # if (order_index and family_index and (family_index - order_index) > 1):
            #     print "\n------\nsplit_tax = %s" % (split_tax)
            #     print "order_index = %s" % (order_index)
            #     print "family_index = %s" % (family_index)
            #     print "split_tax[order_index] = %s" % (split_tax[order_index])
            #     print "split_tax[family_index] = %s" % (split_tax[family_index])
            #     print "split_tax[order_index:family_index] = %s" % (split_tax[order_index:family_index])
            #     print "split_tax[1:5] = %s" % (split_tax[1:5])


                

    #   see etales
                # if taxon.endswith("etales"):
                #     # tax_line["order"]  = taxon
                #     etales_index = split_tax.index(taxon)
                #     if (etales_index != 3):
                #         print "split_tax = %s,\n taxon = %s, etales_index = %s" % (split_tax, taxon, etales_index)

                    # print "split_tax = %s,\n order_index = %s" % (split_tax, order_index)
            # print "tax_line = %s, taxon = %s " % (tax_line, taxon)
    # ====
            #     if taxon.startswith("p__"):
            #         tax_line["phylum"]  = taxon.split("__")[1]
            # -mycota: (mycol.) suffix used to indicate that the name of a fungus is in the  rank of division or phylum.
            # -mycotina: (mycol.) suffix used to indicate that the name of a fungus is in  the rank of a subdivision or phylum.

            #     if taxon.startswith("c__"):
            #         tax_line["class"]   = taxon.split("__")[1]
            # -opsida: (bot.) suffix used to denote a name in the rank of class, except in  algae and fungi.
            # -mycetes: (mycol.) suffix used to indicate that the name of a fungus is in the  rank of class.
            # -inea: (phyt., obsol.) the suffix once used for terminating the name of a  syntaxon in the rank of class; see -etea. = genera!
            # -etea: (phyt.) the suffix terminating the name of a syntaxon in the rank of  class. = genera!
            # -etales: (phyt., obsol.) the suffix once used for terminating the name of a  syntaxon in the rank of class; see -etea.

            #     if taxon.startswith("o__"):
            #         tax_line["order"]   = taxon.split("__")[1]
            # -etalia: (phyt.) the suffix terminating the name of a syntaxon in the rank of  order.
            # -ales: (prok., bot.) suffix added to the stem of a generic name to indicate  that it applies to the taxon of a rank of order.
            #     if taxon.startswith("f__"):
            #         tax_line["family"]  = taxon.split("__")[1]
            #     if taxon.startswith("g__"):
            #         tax_line["genus"]   = taxon.split("__")[1]
            #     if taxon.startswith("s__"):
            #         tax_line["species"] = taxon.split("__")[1]
        # return taxonomy
    
    def get_first(self, tax_line_value):
        first_val = ""
        # III tax_line_value = sp. MAR_2010_100
        if tax_line_value.count(' ') > 0:
            first_val = tax_line_value.split(" ")[0]
        else:
            first_val = tax_line_value
        return first_val
            

    def remove_empty(self, tax_line, name, bad_value):
        try:
          single_value = self.get_first(tax_line[name])                    
          if single_value in bad_value:
              single_value = ''
              return single_value
          else:
              return tax_line[name]
        except KeyError:
          pass
        except:
          print "Unexpected error:", sys.exc_info()[0]
          raise                  
  
    def remove_empty_from_end(self, old_taxonomy, bad_value):
        taxonomy_with_wholes = {}
        for tax_id, tax_line in old_taxonomy.items():          
            for name in reversed(self.ordered_names):
                res_taxa = self.remove_empty(tax_line, name, bad_value)
                if res_taxa != '':
                    tax_line[name] = res_taxa
                    break
                else:
                    del tax_line[name]
            taxonomy_with_wholes[tax_id] = tax_line
        return taxonomy_with_wholes

    def separate_binomial_name(self, tax_line):
        if "species" in tax_line:
          species = tax_line["species"]
          if (species.find(" ") > 0 and species[0].isupper()):
              try:
                species_list = species.split(" ")
                genus        = tax_line["genus"]
                if (species_list[0] == genus):
                    try:
                        tax_line["species"] = " ".join(species_list[1:])
                    except TypeError:
                        del tax_line["species"]
                    except:
                        raise
                else:
                    self.old_taxonomy_weird_by_species[species] = tax_line    
              except KeyError:
                tax_line["genus"] = species[0]
                tax_line["species"] = species[1]
                self.old_taxonomy_weird_by_species["species"] = tax_line    
        return tax_line

    def make_new_taxonomy(self, tax_line):
        # print "IN make_new_taxonomy: tax_line = %s, ordered_names = %s" % (tax_line, self.ordered_names)
        new_line = ""
        for name in self.ordered_names:
          try:
            # print "IN make_new_taxonomy 111: tax_line = %s, name = %s" % (tax_line, name)
            # print "if tax_line[name] != "":"
            if tax_line[name]:
              new_line += (tax_line[name] + ";")
          except KeyError:
            pass
          except:
            raise          
        return new_line

    def has_uncultured(self, binomial):
        try:
            binomial.index("uncultured")
            return binomial
        except ValueError:
          # ValueError: substring not found
          pass
        except:
            raise
            
    def has_capital(self, line):
      if any(c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for c in line):
        print "CCC has_capital, line = %s" % line
      
      # print [c.isupper() for c in line]
      # try:
      #     a = line.index([A-Z])
      #     print "aaa = %s" % a
      #     b = line[a:]
      #     print "bbb = %s" % b
      # except:
      #     raise
    
            
    def deal_with_taxonomy_partial(self):
      taxonomy_partial_file           = open(self.taxonomy_partial_file_name,'w')
      for tax_id, tax_line in self.old_taxonomy_partial.items():
        self.separated_species_taxonomy[tax_id] = self.separate_binomial_name(tax_line[0])
        taxonomy_partial_file.write("---\ntax_id = %s, tax_line[0] = %s, tax_line[1] = %s in self.old_taxonomy_partial.items()\nseparated_species_taxonomy[tax_id] = %s\n" % (tax_id, tax_line[0], tax_line[1], self.separated_species_taxonomy[tax_id] ))

    def get_binomials_from_old_taxonomy_partial(self):
      taxonomy_partial_binomials_file = open(self.taxonomy_partial_binomials_file_name,'w')
      for k, v in self.old_taxonomy_partial.items():
        try:
          bin_list = v[0]["species"].split(" ")
          if len(bin_list) == 2:
            # print bin_list          
            taxonomy_partial_binomials_file.write(v[0]["species"])
            taxonomy_partial_binomials_file.write("\n")             
        except:
            pass

    def make_list_from_json(self):
      for data in self.gna_result["data"]:
        try:
          classification_path_ranks = data["results"][0]["classification_path_ranks"].split("|")
          classification_path       = data["results"][0]["classification_path"].split("|")      
          self.ncbi_classification.append(dict(zip(classification_path_ranks, classification_path)))
        except:
          if data["is_known_name"] == False:
            self.classification_unknown.append(data["supplied_name_string"])

    def get_next_available_rank(self, hey_of_ranks, end_rank = "species"):
      for ordered_n in reversed(self.ordered_names):
          if ordered_n in hey_of_ranks.keys():
              return ordered_n
          else:
              continue
      return end_rank
      
    def make_gna_result_dict_by_key(self, key, dict_in, dict_out):
      for n in dict_in:
        try:
          key = self.get_next_available_rank(n)
          dict_out[n[key]] = n
        except KeyError:
          pass
        except:
          print "Unexpected error:", sys.exc_info()[0]
          raise
      return dict_out
      
    def make_taxonomy_w_empty_ranks(self, tax_line):
      new_line = ""
      for name in self.ordered_names:
        try:
          if tax_line[name]:
            new_line += (tax_line[name] + ";")
        except KeyError:
          new_line += ("empty_" + name + ";")
        except:
          raise       
      return new_line
      
    def make_taxonomy_w_good_ranks(self, dict_in, dict_out):
      for k, v in dict_in.items():
        clean_tax_line = self.separate_binomial_name(v)
        new_tax = self.make_new_taxonomy(clean_tax_line).strip(";")
        my_tax = self.make_taxonomy_w_empty_ranks(clean_tax_line)
        
        if len(new_tax.split(";")) == 7:
          dict_out[k] = new_tax
        elif len(new_tax.split(";")) > 0:
          self.taxonomy[k] = my_tax
        else:
          self.classification_unknown.append(k)
      return dict_out

    def parse_json(self, json_res_file_name):
      with open(json_res_file_name) as data_file:    
        self.gna_result = json.load(data_file)      
      
    def write_list_to_file(self, list_name, file_name, to_add = 'w'):
      file_open = open(file_name, to_add)
      for line in list_name:
        file_open.write("%s\n" % (line))
      file_open.close()
      
    def print_w_div(self, dict_in, div = "#"):
        try:
          for k, v in dict_in:
            print "%s%s%s" % (k, div, v)
        except:
          pass
    
    def make_clean_taxonomy_from_partial(self, json_res_file_name):
        self.parse_json(json_res_file_name)        
        self.make_list_from_json()
                
        self.make_gna_result_dict_by_key('species', self.ncbi_classification, self.ncbi_classification_by_sp) 
        ncbi_tax_ok = self.make_taxonomy_w_good_ranks(self.ncbi_classification_by_sp, self.ncbi_classification_by_sp_good)    
        # self.print_w_div(ncbi_tax_ok.items())
        #
        print "=====000"
        print self.taxonomy
        print "=====111"
        self.write_list_to_file(self.classification_unknown, self.classification_unknown_file_name, 'a')      
        self.write_list_to_file(self.taxonomy.values(), "genus_taxonomy.txt", 'a')      
        

    def write_dict_to_file(self, file_name, dict_name, to_add = 'w'):
        file_open = open(file_name, to_add)
        for tax_id, tax_line in dict_name.items():
            # file_open.write('%s, "%s"\n' % (tax_id, tax_line))
            file_open.write("%s#%s\n" % (tax_id, tax_line))
        file_open.close()

    def write_old_taxonomy_weird_by_species(self):
      with open("old_taxonomy_weird_by_species.txt", 'a') as the_file:        
      
        for k, v in self.old_taxonomy_weird_by_species.items():
          new_tax = self.make_new_taxonomy(v).strip(";")        
          the_file.write("%s#%s\n" % (k, new_tax))
    
    def get_good_silva(self, tax_infile_name):
      self.make_taxa_dict(tax_infile_name)
      separated_species_taxonomy = {}
      for k, v in self.old_taxonomy_good.items():
        try:
          separated_species_taxonomy[k] = self.separate_binomial_name(v)
        except:
          raise
      
      taxonomy_with_wholes = self.remove_empty_from_end(separated_species_taxonomy, self.bad_value)
      
      # print "taxonomy_with_wholes = "
      # print taxonomy_with_wholes
      
      good_silva_tax = {}
      for id_tax, tax_line_dict in taxonomy_with_wholes.items():
        if ('species' in tax_line_dict) and tax_line_dict['species'] and tax_line_dict['species'].count(' ') > 0:
            self.old_taxonomy_weird[id_tax] = tax_line_dict    
            # print "TTT id_tax = %s, tax_line_dict = %s" % (id_tax, tax_line_dict)
        else:        
            good_silva_tax[id_tax] = self.make_new_taxonomy(tax_line_dict).strip(";")

      self.write_dict_to_file(self.taxonomy_good_file_name, good_silva_tax)
      self.write_old_taxonomy_weird_by_species()
      # todo:
      # write old_taxonomy_weird (by id)
        
    def process(self, args):
        tax_infile    = args.tax_infile
        taxout_fh     = open(args.tax_outfile,'w')
        self.make_taxa_dict(tax_infile)
        # print "HERE result"
        print len(self.old_taxonomy_weird)
        # 5571
        # after counting ranks (includes old_taxonomy_partial)
        # 36710
        
        print len(self.old_taxonomy_good)
        # 108436
        # after counting ranks
        # 71875
        # 71821
        # print self.old_taxonomy_good 
        # todo: check if only Bacteria?
        
        print len(self.old_taxonomy_partial)
        # 36561
        # 36615
        # print self.old_taxonomy_partial['89370']
        
        self.get_binomials_from_old_taxonomy_partial()
        self.make_clean_taxonomy_from_partial()
        
        self.deal_with_taxonomy_partial()
        
        taxonomy_weird_file = open(self.taxonomy_weird_file_name,'w')
        for tax_id, tax_line in self.old_taxonomy_weird.items():
          if tax_id in self.old_taxonomy_partial:
            del self.old_taxonomy_weird[tax_id]
          else:
            # pass
            # print "tax_id = %s, tax_line = %s in self.old_taxonomy_weird.items()" % (tax_id, tax_line)
            # print tax_line[0:6]
          # self.separated_species_taxonomy[tax_id] = self.separate_binomial_name(tax_line[0])
            taxonomy_weird_file.write("---\ntax_id = %s, tax_line = %s in self.old_taxonomy_weird.items()\n" % (tax_id, tax_line))
        
        print len(self.old_taxonomy_weird)
        # 148
        # separated_species_taxonomy = {}
        # for tax_id, tax_line in old_taxonomy.items():
        #     separated_species_taxonomy[tax_id] = separate_binomial_name(tax_line)
        # taxonomy_with_wholes = remove_empty_from_end(ordered_names, separated_species_taxonomy, bad_value)
        # for tax_id, tax_line in taxonomy_with_wholes.items():
        #     tax_line_w_k_ph = make_kingdom_phylum(tax_line, bad_value)
        #     taxout_fh.write(change_id(tax_id) + "\t"  + make_new_taxonomy(tax_line_w_k_ph, ordered_names) + "\t" + "1" + "\n")
    
    def is_genus(self, word):
      try:
        if word[0].isupper():
          return True
      except:
        raise
      return False  
      
    def is_bad(self, word):  
      for bad_value in self.bad_value:
        if word.startswith(bad_value):
        # if word in self.bad_value or word.startsswith(self.bad_value):
            return True
      # else:
      return False
    
    def get_good_binomial(self, binomial):
      good_binomial_list = []
      binomial_list = binomial.split(" ")
      if (self.is_genus(binomial_list[0])):
        good_binomial_list.append(binomial_list[0])
        try:
          if not (self.is_bad(binomial_list[1])):
            good_binomial_list.append(binomial_list[1])
            
        except IndexError:
          # IndexError: list index out of range
          pass
        except:
          raise              
      return good_binomial_list
        
    def separate_binomials(self, tax_infile_name):
      uncultured = {}
      good_binomials = {}
      the_rest = {}
      for line in open(tax_infile_name):
          split_tax, id_tax = self.clean_tsv_line(line)
          binomial = split_tax[-1]
          # print "SSS split_tax = %s, id_tax = %s, binomial = %s" % (split_tax, id_tax, binomial)
          uncultured_binomial = self.has_uncultured(binomial)
          if uncultured_binomial:
            uncultured[id_tax] = uncultured_binomial
          # uncultured.append[uncultured_binomial]
          good_binomial = " ".join(self.get_good_binomial(binomial))
          if good_binomial:
            good_binomials[id_tax] = good_binomial
          else:
            the_rest[id_tax] = binomial
      # 1) has genus species or
      #   a) genus = genus in tax_line
      # 2) has only genus (with additions?)
      print "RRR 31405"
      print len(good_binomials)
      self.write_dict_to_file("binomial_good_binomials.txt", good_binomials)
      print "BBB check_binomials 16238"
      print len(uncultured)
      self.write_dict_to_file("binomial_uncultured.txt", uncultured)
      # 3) get the rest as a list and researh ('uncultured', 'uncultured Haliphthoros'; 'uncultured eukaryote')
      print "PPP the_rest 23282"
      print len(the_rest)
      self.write_dict_to_file("binomial_the_rest.txt", the_rest)
      

    def get_list_before_uncultured(self, tax_infile_name):
        before_uncultured_dict_by_id = {}
        for line in open(tax_infile_name):
            split_tax, id_tax = self.clean_tsv_line(line)
            last_name_before_uncultured = split_tax[-1]
            if (last_name_before_uncultured == "uncultured") or (last_name_before_uncultured[0].isdigit()):
                last_name_before_uncultured = split_tax[-2]
            before_uncultured_dict_by_id[id_tax] = (last_name_before_uncultured, split_tax)
            # print "SSS split_tax = %s, id_tax = %s, last_name_before_uncultured = %s" % (split_tax, id_tax, last_name_before_uncultured)
            print last_name_before_uncultured
        self.write_dict_to_file("before_uncultured_dict_by_id.txt", before_uncultured_dict_by_id)
        

    def get_list_before_binomial(self, tax_infile_name):
        before_binomial_dict_by_id = {}
        for line in open(tax_infile_name):
            split_tax, id_tax = self.clean_tsv_line(line)
            last_name_before_binomial = split_tax[-1]
            if (last_name_before_binomial == "uncultured") or (last_name_before_binomial[0].isdigit()):
                last_name_before_binomial = split_tax[-2]
            before_binomial_dict_by_id[id_tax] = (last_name_before_binomial, split_tax)
            # print "SSS split_tax = %s, id_tax = %s, last_name_before_binomial = %s" % (split_tax, id_tax, last_name_before_binomial)
            print last_name_before_binomial
        self.write_dict_to_file("before_binomial_dict_by_id.txt", before_binomial_dict_by_id)


"""
def make_clean_taxonomy_from_partial(self, json_res_file_name):
    self.parse_json(json_res_file_name)        
    self.make_list_from_json()
            
    self.make_gna_result_dict_by_key('species', self.ncbi_classification, self.ncbi_classification_by_sp)        
    ncbi_tax_ok = self.make_taxonomy_w_good_ranks(self.ncbi_classification_by_sp, self.ncbi_classification_by_sp_good)    
    try:
      for k, v in ncbi_tax_ok.items():
        print "%s#%s" % (k, v)
    except:
      pass
      
    self.write_list_to_file(self.classification_unknown, self.classification_unknown_file_name, 'a')      
"""

    # def make_list_from_json1(self):
    #   for data in self.gna_result["data"]:
    #     try:
    #       if self.gna_result["data"][0]["is_known_name"]:
    #         classification_path_ranks = data["results"][0]["classification_path_ranks"].split("|")
    #         classification_path       = data["results"][0]["classification_path"].split("|")
    #         self.ncbi_classification.append(dict(zip(classification_path_ranks, classification_path)))
    #     except:
    #       if data["is_known_name"] == False:
    #         self.classification_unknown.append(data["supplied_name_string"])
    #
    #
    #
    # def make_clean_taxonomy_from_gna_api_res_preff(self, json_res_file_name):
    #   self.parse_json(json_res_file_name)


if __name__ == '__main__':
    print "Use raxonomy_cleaner_client.py -i input_file_name"
#     THE_DEFAULT_BASE_OUTPUT = '.'
# 
#     usage = "usage: %prog [options] arg1"
#     parser = argparse.ArgumentParser(description='ref fasta/tax file creator')
#     parser.add_argument('-it', '--tax_in', required=True, dest = "tax_infile",
#                                                  help = '')
#     #parser.add_argument('-if', '--fasta_in', required=True, dest = "fasta_infile",
#     #                                             help = '')
#     parser.add_argument('-ot', '--tax_out', required=False, dest = "tax_outfile",   default='outfile.tax',
#                                                  help = '')
#     #parser.add_argument('-of', '--fasta_out', required=False, dest = "fasta_outfile", default='outfile.fasta',
#     #                                             help = '')
#     args = parser.parse_args()
# 
# 
#     tax_class = Taxonomy()
#     # now do all the work
#     tax_class.process(args)
# 
