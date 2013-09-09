#! /opt/local/bin/python

# -*- coding: utf-8 -*-

# Copyright (C) 2013, Marine Biological Laboratory
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
# Anna Shipunova
# ver 0 2013 

# 1)
# superkingdom, phylum, class, orderx, family, genus, species, strain, 
# 
# 3 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria    Bacteria    phylum_NA   class_NA    orderx_NA   family_NA   genus_NA    species_NA  strain_NA   domain  32  0.005865102639  5456    GAST
# 4 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria;Acidobacteria  Bacteria    Acidobacteria   class_NA    orderx_NA   family_NA   genus_NA    species_NA  strain_NA   phylum  19  0.003482404692  5456    GAST
# 5 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria;Acidobacteria;Acidobacteria;Acidobacteriales;Acidobacteriaceae Bacteria    Acidobacteria   Acidobacteria   Acidobacteriales    Acidobacteriaceae   genus_NA    species_NA  strain_NA   family  158 0.028958944282  5456    GAST
# 6 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria;Acidobacteria;Acidobacteria;Acidobacteriales;Acidobacteriaceae;Chloroacidobacterium    Bacteria    Acidobacteria   Acidobacteria   Acidobacteriales    Acidobacteriaceae   Chloroacidobacterium    species_NA  strain_NA   genus   9   0.001649560117  5456    GAST
# 7 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria;Acidobacteria;Acidobacteria_Gp22;Unassigned;Unassigned;Gp22    Bacteria    Acidobacteria   Acidobacteria_Gp22  Unassigned  Unassigned  Gp22    species_NA  strain_NA   genus   18  0.003299120235  5456    GAST
# 8 AB_HGB1_Bv6v4   HGB_0005_2  Bacteria;Acidobacteria;Acidobacteria_Gp26;Unassigned;Unassigned;Gp26    Bacteria    Acidobacteria   Acidobacteria_Gp26  Unassigned  Unassigned  Gp26    species_NA  strain_NA   genus   10  0.001832844575  5456    GAST

# see new_taxonomy_view
# TODO:
# *) parse taxonomy from db
# *) put result in db
# *) check ends ("ales" - order, "aceae" - family, etc)
# *) species - only small letters (e.g. see Fungi;)
# *) remove! repetitions: Bacteria;Acidobacteria;Acidobacteria;Acidobacteriales
# *) separate binomials into genus/species
# *) add "range_NA", like "species_NA" and "Unassigned" to the result table?
# *) check all "bad" words from bad_value
# *) no spaces
# *) "Atractiellales;unclassified Atractiellales" - remove underrank

import argparse
import sql_tables_class
import shared
import time
from collections import defaultdict

class MyTaxonomy:
    """
    Deal with taxonomy (csv from env454.taxonomy):
        clean,
        rearrange,
        put into new ROR tables    
    """
    
    def __init__(self):
        self.ordered_names = "superkingdom", "phylum", "class", "orderx", "family", "genus", "species", "strain"
        self.bad_value     = "Fungi", "unculturedfungus", "unidentified", "sp", "sp.", "unculturedsoil_fungus", "unidentified_sp.", "unculturedcompost_fungus", "unculturedectomycorrhizal_fungus"
        self.dup_ids       = defaultdict(list)
        self.old_taxonomy  = {}
        self.new_taxonomy  = {}
        self.time_stamps_ids = {}
        
    def make_taxa_dict(self, tax_infile):
    
        # # id,"taxonomy","created_at","updated_at"
        # # 1,"Archaea;Crenarchaeota;Thermoprotei;Desulfurococcales;Desulfurococcaceae;Unassigned;uncultured crenarchaeote pBA3","2013-08-16 21:12:22","2013-08-16 21:12:22"

        with open(tax_infile) as file_content:    
            next(file_content)
            for line in file_content:

                tax_line = {}
        
                line           = line.strip()
                tax_line_split = line.split(",")
                id_tax         = tax_line_split[0]
                time_stamps    = tax_line_split[2:]
                split_tax      = tax_line_split[1].strip('"').split(';')
        
                self.old_taxonomy[id_tax]    = dict(zip(self.ordered_names, split_tax))
                self.time_stamps_ids[id_tax] = time_stamps
            
    def remove_bad(self, tax_line, name):
        if tax_line[name] in self.bad_value:
            tax_line[name] = ''
        return tax_line[name]
    
    def remove_empty_and_get_dups(self, taxonomy_with_wholes):
        taxonomy_no_dup = {}
        
        for tax_id, tax_line in taxonomy_with_wholes.items():                
            new_tax_line    = {}
            rank_name       = "" 
            taxon           = ""            
            new_tax_line    = dict((rank_name, taxon) for rank_name, taxon in tax_line.items() if (taxon != "")) #remove_empty
            #get_dups
            if new_tax_line in taxonomy_no_dup.values():
                [self.dup_ids[key].append(tax_id) for key in taxonomy_no_dup.keys() if (taxonomy_no_dup[key] == new_tax_line)]
            else:
                taxonomy_no_dup[tax_id] = new_tax_line            
        return taxonomy_no_dup

    def remove_bad_from_end(self, taxononomy_with_empty):
        taxonomy_with_wholes = {}
        for tax_id, tax_line in taxononomy_with_empty.items():
            for name in reversed(self.ordered_names[1:]): # don't touch superkingdom
                res_taxa = self.remove_bad(tax_line, name)
                if res_taxa != '':
                    break
            taxonomy_with_wholes[tax_id] = tax_line
        return taxonomy_with_wholes

    def separate_binomial_name(self, tax_line):
        species = ""
        genus   = ""
        try: 
            if (tax_line["species"].find(" ") > 0):
                species = tax_line["species"].split(" ")
                genus   = tax_line["genus"]
                if (species[0] == genus):
                    tax_line["species"] = (" ").join(species[1:])
        except:
            pass
        return tax_line

    def upload_taxa(self, value):
        for rank, taxon in value.items():
            sql_taxa = ""
            # todo: create all values once: VALUES ("%s", "%s"), ("%s", "%s")...
            sql_taxa       = 'INSERT IGNORE INTO taxa_temp (taxon, rank) VALUES ("%s", "%s")' % (taxon, rank)
            # {'superkingdom': 'Archaea', 'phylum': 'Crenarchaeota', 'orderx': 'Desulfurococcales', 'family': 'Pyrodictiaceae', 'class': 'Thermoprotei'}
            print "sql_taxa = %s" % sql_taxa
            # shared.my_conn.execute_no_fetch(sql_taxa)    
    
    def make_empty_taxa(self, my_dict):
        for name in self.ordered_names:
            if name not in my_dict.keys():
                my_dict[name] = ""
        return my_dict
    
    def upload_new_taxonomy(self, key, value):
        # print time_stamps_ids
        # print key
        print value
        # , self.time_stamps_ids[key]
        self.upload_taxa(value)
        my_dict = self.make_empty_taxa(value)
            
        sql_taxonomies = ""
        sql_taxonomies = 'INSERT IGNORE INTO taxonomies_sep (id, superkingdom, phylum, class, orderx, family, genus, species, strain, created_at, updated_at) VALUES (%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, %s)' % (key, my_dict["superkingdom"], my_dict["phylum"], my_dict["class"], my_dict["orderx"], my_dict["family"], my_dict["genus"], my_dict["species"], my_dict["strain"], self.time_stamps_ids[key][0], self.time_stamps_ids[key][1])
        print "sql_taxonomies = %s" % sql_taxonomies
        # shared.my_conn.execute_no_fetch(sql_taxonomies)    

    def update_taxa_ranks_ids(self):
        sql = """
            UPDATE taxa_temp
            JOIN ranks USING(rank)
            SET taxa_temp.rank_id = ranks.id
        """
        shared.my_conn.execute_no_fetch(sql)    
    
    def update_taxonomies_sep_ids(self):
        for name in self.ordered_names:
            sql = """
                UPDATE taxonomies_sep
                JOIN taxa_temp ON(taxon = %s) AND rank = "%s"
                SET taxonomies_sep.%s_id = taxa_temp.id    
            """ % (name, name, name)
            # print sql
            shared.my_conn.execute_no_fetch(sql)    

    def update_sequence_uniq_infos(self):
        # dup_ids = {'41': [], '1': [], '91': [], '3': [], '2': [], '5': ['81'], '4': [], '7': ['6', '8'], '6': [], '9': [], '8': [], '81': []}
    
        # sql = """
        #     SELECT * FROM sequence_uniq_infos
        #     WHERE taxonomy_id in (%s)
        # """ % ", ".join(dup_ids.keys())
        # print sql
        # res = shared.my_conn.execute_fetch_select(sql)    
        # print res
        print "make dup_only"
        dup_only = dict((k, v) for k, v in self.dup_ids.items() if v)
        # print dup_only

        print "create sql_update"
        for good_id, dup_ids in dup_only.items():
            # print "good_id = %s, dup_ids = %s" % (good_id, dup_ids)
            sql_update = """
                UPDATE sequence_uniq_infos
                SET taxonomy_id = %s
                WHERE taxonomy_id in (%s)
            """ % (good_id, ", ".join(dup_ids))
            print sql_update
            # shared.my_conn.execute_no_fetch(sql_update)    

    # What to do if the same taxonomy has diff gast? - gast for a read, not for taxonomy?
    # (128L, 128L, 81L, Decimal('0.01600'), 0L, 175L, 4L, 'v6_AO868,v6_AO871', datetime.datetime(2013, 8, 19, 13, 11), datetime.datetime(2013, 8, 19, 13, 11))
    # (165L, 165L, 81L, Decimal('0.01600'), 0L, 174L, 4L, 'v6_AO871', datetime.datetime(2013, 8, 19, 13, 11), datetime.datetime(2013, 8, 19, 13, 11))
            
    def create_new_taxa_tables(self):
        sql1 = """
            CREATE TABLE IF NOT EXISTS `taxa` (
              `id` int(11) NOT NULL AUTO_INCREMENT,
              `taxon` varchar(300) DEFAULT NULL,
              rank_id  int(11) NOT NULL, 
              PRIMARY KEY (`id`),
              UNIQUE KEY `taxon` (`taxon`)
            ) ENGINE=InnoDB CHARSET=latin1;
        """
        shared.my_conn.execute_no_fetch(sql1)    
        sql2 = """
        CREATE TABLE IF NOT EXISTS `taxonomies_sep` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `superkingdom` varchar(60) NOT NULL DEFAULT '',
          `superkingdom_id` int(11) DEFAULT NULL,
          `phylum` varchar(60) NOT NULL DEFAULT '',
          phylum_id int(11) DEFAULT NULL,
          `class` varchar(60) NOT NULL DEFAULT '',
          class_id int(11) DEFAULT NULL,
          `orderx` varchar(60) NOT NULL DEFAULT '',
          orderx_id int(11) DEFAULT NULL,
          `family` varchar(60) NOT NULL DEFAULT '',
          family_id int(11) DEFAULT NULL,
          `genus` varchar(60) NOT NULL DEFAULT '',
          genus_id int(11) DEFAULT NULL,
          `species` varchar(60) NOT NULL DEFAULT '',
          species_id int(11) DEFAULT NULL,
          `strain` varchar(60) NOT NULL DEFAULT '',
          strain_id int(11) DEFAULT NULL,
          `created_at` datetime DEFAULT NULL,
          `updated_at` datetime DEFAULT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `all_names` (`superkingdom`,`phylum`,`class`,`orderx`,`family`,`genus`,`species`,`strain`)
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """
        shared.my_conn.execute_no_fetch(sql2)   
        sql3 = """
        CREATE TABLE IF NOT EXISTS `taxa_temp` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `taxon` VARCHAR(300) DEFAULT NULL,
          `rank_id` INT(11) NOT NULL,
          `rank` VARCHAR(32) NOT NULL DEFAULT '',  
          PRIMARY KEY (`id`),
          UNIQUE KEY `taxon` (`taxon`)
        ) ENGINE=INNODB DEFAULT CHARSET=latin1;
        """
        shared.my_conn.execute_no_fetch(sql3)    
        sql4 = """
        RENAME TABLE taxonomies TO taxonomies_old
        """
        shared.my_conn.execute_no_fetch(sql4)    
        sql5 = """
        CREATE TABLE IF NOT EXISTS `taxonomies` (
          `id` int(11) NOT NULL AUTO_INCREMENT,
          `superkingdom_id` int(11) DEFAULT NULL,
          `phylum_id` int(11) DEFAULT NULL,
          `class_id` int(11) DEFAULT NULL,
          `orderx_id` int(11) DEFAULT NULL,
          `family_id` int(11) DEFAULT NULL,
          `genus_id` int(11) DEFAULT NULL,
          `species_id` int(11) DEFAULT NULL,
          `strain_id` int(11) DEFAULT NULL,
          `created_at` datetime DEFAULT NULL,
          `updated_at` datetime DEFAULT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `all_names` (`superkingdom_id`,`phylum_id`,`class_id`,`orderx_id`,`family_id`,`genus_id`,`species_id`,`strain_id`),
            CONSTRAINT `taxonomy_fk_taxa_id1` FOREIGN KEY (`superkingdom_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id2` FOREIGN KEY (`phylum_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id3` FOREIGN KEY (`class_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id4` FOREIGN KEY (`orderx_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id5` FOREIGN KEY (`family_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id6` FOREIGN KEY (`genus_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id7` FOREIGN KEY (`species_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE,
            CONSTRAINT `taxonomy_fk_taxa_id8` FOREIGN KEY (`strain_id`) REFERENCES `taxa` (`id`) ON UPDATE CASCADE 
        ) ENGINE=InnoDB DEFAULT CHARSET=latin1;
        """
        shared.my_conn.execute_no_fetch(sql5)    
     
    def taxa_insert(self):
        sql = """
            INSERT IGNORE INTO taxa (id, taxon, rank_id) SELECT id, taxon, rank_id FROM taxa_temp
        """
        shared.my_conn.execute_no_fetch(sql)    

    def taxonomies_insert(self):
        sql = """
        INSERT IGNORE INTO taxonomies (superkingdom_id, phylum_id, class_id, orderx_id, family_id, genus_id, species_id, strain_id, created_at, updated_at) SELECT superkingdom_id, phylum_id, class_id, orderx_id, family_id, genus_id, species_id, strain_id, created_at, updated_at FROM taxonomies_sep
        """
        shared.my_conn.execute_no_fetch(sql)    
    
    def db_update(self):
        start = time.time()
        print "start create_new_taxa_tables"
        create_new_taxa_tables()
        end = time.time()
        print end - start
    
        start = time.time()
        print "start upload_new_taxonomy"
        for key, value in self.new_taxonomy.items():
            self.upload_new_taxonomy(key, value)
        end = time.time()
        print end - start

        start = time.time()
        print "start update_taxa_ranks_ids"
        update_taxa_ranks_ids()    
        end = time.time()
        print end - start

        start = time.time()
        print "start update_taxonomies_sep_ids"
        update_taxonomies_sep_ids()
        end = time.time()
        print end - start

        start = time.time()
        print "start taxa_insert"
        taxa_insert()
        end = time.time()
        print end - start

        start = time.time()
        print "start taxonomies_insert"
        taxonomies_insert()
        end = time.time()
        print end - start

        start = time.time()
        print "start update_sequence_uniq_infos"
        update_sequence_uniq_infos()
        end = time.time()
        print end - start


#         ===================== Taxonomy check ==============
# http://en.wikipedia.org/wiki/Taxonomic_rank
    def is_phylum(self, name):
        if name.endswith("phyta") or name.endswith("mycota"):
            return True
        else:
            return False
    # Subdivision/Subphylum     -phytina -mycotina

    def is_class(self, name):
        if name.endswith("opsida") or name.endswith("phyceae") or name.endswith("mycetes"):
            return True
        else:
            return False
    # Subclass  -idae -phycidae -mycetidae

    # Superorder        -anae
    def is_order(self, name):
        if name.endswith("ales"):
            return True
        else:
            return False
    # Suborder  -ineae
    # Infraorder        -aria - could be species too!


    # Superfamily       -acea -oidea
    # Epifamily                 -oidae
    def is_family(self, name):
        if name.endswith("aceae"):
            return True
        else:
            return False
    # "idae" - could by subclass or family
    # Subfamily -oideae -inae
    # Infrafamily                   -odd 
    # Tribe -eae -ini
    # Subtribe  -inae -ina    
    # Infratribe                    -ad
    # For Bacteria only:
    # (http://en.wikipedia.org/wiki/Bacterial_taxonomy)
    # Rank  Suffix  Example
    # Genus     Elusimicrobium
    # Subtribe (disused)    -inae   (Elusimicrobiinae)
    # Tribe (disused)   -inae   (Elusimicrobiieae)
    # Subfamily -oideae (Elusimicrobioideae)
    # Family    -aceae  Elusimicrobiaceae
    # Suborder  -ineae  (Elusimicrobineae)
    # Order -ales   Elusimicrobiales
    # Subclass  -idae   (Elusimicrobidae)
    # Class -ia Elusimicrobia
    # Phylum    see text    Elusimicrobia
        
    def has_spaces(self, name):
        pass

    def species_initial(self, name):
        pass

    def check_ranks(self, rank_name, taxon_name):
        terminals = {
        'phylum': ["phyta", "mycota"],
        'class': ["opsida", "phyceae", "mycetes"],
        'orderx': ["ales"],
        'family': ["aceae"]
        }
        
        for term_name, terminal_list in terminals.items():
            return [True for terminal in terminal_list if taxon_name.endswith(terminal) and term_name != rank_name]
        
    def taxonomy_check(self):
        for id_key, name_values in self.new_taxonomy.items():
            for rank_name, taxon_name in name_values.items():     
                # print "rank_name = %s, taxon_name = %s" % (rank_name, taxon_name)
                print self.check_ranks(rank_name, taxon_name)
                # print "term_name = %s, terminal = %s, rank_name = %s, bad taxon_name = %s" % (term_name, terminal, rank_name, taxon_name)

                
                # if (rank_name in ('phylum', 'class', 'orderx', 'family')): 
                #     res = self.check_rank(rank_name, taxon_name)
                #     if not res:
                #         print "rank_name %s, taxon_name = %s" % (rank_name, taxon_name)
                # self.is_phylum(taxon_name)
                # self.is_class(taxon_name)
                # self.is_order(taxon_name)
                # self.is_family(taxon_name)
                self.has_spaces(taxon_name)
                self.species_initial(taxon_name)
        
    def process(self, args):
        tax_infile    = args.tax_infile
        start = time.time()
        print "start make_taxa_dict"
        self.make_taxa_dict(tax_infile)
        print "self.old_taxonomy = %s" % self.old_taxonomy
        separated_species_taxonomy = {}
        end = time.time()
        print end - start
    
        start = time.time()
        print "start separate_binomial_name"
        for tax_id, tax_line in self.old_taxonomy.items():
            separated_species_taxonomy[tax_id] = self.separate_binomial_name(tax_line)
        taxononomy_with_empty = {}
        end = time.time()
        print end - start

        start = time.time()
        print "start make_empty_taxa"
        for key, value in separated_species_taxonomy.items():
            taxononomy_with_empty[key] = self.make_empty_taxa(value)    
        end = time.time()
        print end - start

        start = time.time()
        print "start remove_bad_from_end"
        taxonomy_with_wholes = self.remove_bad_from_end(taxononomy_with_empty)
        end = time.time()
        print end - start

        start = time.time()
        print "start remove_empty_and_get_dups"
        self.new_taxonomy = self.remove_empty_and_get_dups(taxonomy_with_wholes)
        end = time.time()
        print end - start
    
        print "self.new_taxonomy = %s" % self.new_taxonomy
        print "self.dup_ids = %s" % self.dup_ids
    
        if args.db_update:
            self.db_update()
        
        if args.taxonomy_check:
            self.taxonomy_check()    

#             ---------- temp test -------------
        start = time.time()
        print "start upload_new_taxonomy"
        for key, value in self.new_taxonomy.items():
            self.upload_new_taxonomy(key, value)
        end = time.time()
        print end - start
                
    
if __name__ == '__main__':
    shared.my_conn = sql_tables_class.MyConnection('localhost', 'vamps2')
    # usage = "usage: %prog [options] arg1"
    parser = argparse.ArgumentParser(description = 'Taxonomy cleaning and splitting')
    parser.add_argument('tax_infile',
                        help = 'CSV file with taxonomy - import from env454.taxonomy (id,"taxonomy","created_at","updated_at")')   
    parser.add_argument('--db_update', '-u', required = False, action="store_true",
                        help = 'Update the db')
    parser.add_argument('--taxonomy_check', '-t', required = False, action="store_true",
                        help = 'Check taxonomic names and get list of suspicious names')
                                                 
    args = parser.parse_args() 

    # now do all the work
    MyTaxonomy().process(args)

