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
 
def make_taxa_dict(tax_infile, ordered_names):
    taxonomy       = {}
    time_stamps_ids = {}
    
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
            # print time_stamps
            split_tax      = tax_line_split[1].strip('"').split(';')
        
            taxonomy[id_tax] = dict(zip(ordered_names, split_tax))
            time_stamps_ids[id_tax] = time_stamps
        return taxonomy, time_stamps_ids
            
def remove_bad(tax_line, name, bad_value):
    if tax_line[name] in bad_value:
        tax_line[name] = ''
    return tax_line[name]

def remove_empty(tax_line):
    return dict((rank_name, taxon) for rank_name, taxon in tax_line.items() if (taxon != ""))

def get_dups(new_tax_line, taxonomy_no_dup, tax_id, dup_ids):
    if new_tax_line in taxonomy_no_dup.values():
        [dup_ids[key].append(tax_id) for key in taxonomy_no_dup.keys() if (taxonomy_no_dup[key] == new_tax_line)]
    else:
        taxonomy_no_dup[tax_id] = new_tax_line
    return taxonomy_no_dup, dup_ids
    
def remove_empty_and_get_dups(taxonomy_with_wholes):
    taxonomy_no_dup = {}
    dup_ids         = {}
    for tax_id, tax_line in taxonomy_with_wholes.items():    
        if tax_id not in dup_ids.keys():
            dup_ids[tax_id] = []    
        new_tax_line = {}
        rank_name    = "" 
        taxon        = ""
        new_tax_line = remove_empty(tax_line)
        taxonomy_no_dup, dup_ids = get_dups(new_tax_line, taxonomy_no_dup, tax_id, dup_ids)
    return taxonomy_no_dup, dup_ids

def remove_bad_from_end(old_taxonomy, bad_value, ordered_names):
    taxonomy_with_wholes = {}
    for tax_id, tax_line in old_taxonomy.items():
        for name in reversed(ordered_names[1:]): # don't touch superkingdom
            res_taxa = remove_bad(tax_line, name, bad_value)
            if res_taxa != '':
                break
        taxonomy_with_wholes[tax_id] = tax_line
    return taxonomy_with_wholes

def separate_binomial_name(tax_line):
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

def upload_taxa(value):
    for rank, taxon in value.items():
        sql_taxa = ""
        # todo: create all values once: VALUES ("%s", "%s"), ("%s", "%s")...
        sql_taxa       = 'INSERT IGNORE INTO taxa_temp (taxon, rank) VALUES ("%s", "%s")' % (taxon, rank)
        # {'superkingdom': 'Archaea', 'phylum': 'Crenarchaeota', 'orderx': 'Desulfurococcales', 'family': 'Pyrodictiaceae', 'class': 'Thermoprotei'}
        # print "sql_taxa = %s" % sql_taxa
        shared.my_conn.execute_no_fetch(sql_taxa)    
    
def make_empty_taxa(ordered_names, my_dict):
    for name in ordered_names:
        if name not in my_dict.keys():
            my_dict[name] = ""
    return my_dict
        
def upload_new_taxonomy(ordered_names, key, value, time_stamps_ids):
    # print time_stamps_ids
    # print key
    # print value
    upload_taxa(value)
    my_dict = make_empty_taxa(ordered_names, value)
            
    sql_taxonomies = ""
    sql_taxonomies = 'INSERT IGNORE INTO taxonomies_sep (id, superkingdom, phylum, class, orderx, family, genus, species, strain, created_at, updated_at) VALUES (%s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s, %s)' % (key, my_dict["superkingdom"], my_dict["phylum"], my_dict["class"], my_dict["orderx"], my_dict["family"], my_dict["genus"], my_dict["species"], my_dict["strain"], time_stamps_ids[0], time_stamps_ids[1])
    # print "sql_taxonomies = %s" % sql_taxonomies
    shared.my_conn.execute_no_fetch(sql_taxonomies)    

def update_taxa_ranks_ids():
    sql = """
        UPDATE taxa_temp
        JOIN ranks USING(rank)
        SET taxa_temp.rank_id = ranks.id
    """
    shared.my_conn.execute_no_fetch(sql)    
    
def update_taxonomies_sep_ids(ordered_names):
    for name in ordered_names:
        sql = """
            UPDATE taxonomies_sep
            JOIN taxa_temp ON(taxon = %s) AND rank = "%s"
            SET taxonomies_sep.%s_id = taxa_temp.id    
        """ % (name, name, name)
        # print sql
        shared.my_conn.execute_no_fetch(sql)    

def update_sequence_uniq_infos(dup_ids):
    # dup_ids = {'41': [], '1': [], '91': [], '3': [], '2': [], '5': ['81'], '4': [], '7': ['6', '8'], '6': [], '9': [], '8': [], '81': []}
    
    sql = """
        SELECT * FROM sequence_uniq_infos
        WHERE taxonomy_id in (%s)
    """ % ", ".join(dup_ids.keys())
    print sql
    res = shared.my_conn.execute_fetch_select(sql)    
    # print res
    dup_only = dict((k, v) for k, v in dup_ids.items() if v)
    print dup_only
    # for old_id, new_ids in dup_only.items():
    for row in res:
        print "row[2] = %s" % row[2]
    #         print row
    #         print "row[2] = %s, old_id = %s, new_ids = %s" % (row[2], old_id, new_ids)
            # if int(row[2]) == int(old_id):
            #     if old_id in new_ids:
                # for new_id in new_ids:
                #     print "new_id = %s" % new_id
                #     print "URA"
                # print "new_ids = %s" % new_ids
                # sql_update = """
                # UPDATE sequence_uniq_infos
                # SET taxonomy_id = %s
                # WHERE taxonomy_id = %s
                # """ %
                # ()

# What to do if the same taxonom,y has diff gast?
# (128L, 128L, 81L, Decimal('0.01600'), 0L, 175L, 4L, 'v6_AO868,v6_AO871', datetime.datetime(2013, 8, 19, 13, 11), datetime.datetime(2013, 8, 19, 13, 11))
# (165L, 165L, 81L, Decimal('0.01600'), 0L, 174L, 4L, 'v6_AO871', datetime.datetime(2013, 8, 19, 13, 11), datetime.datetime(2013, 8, 19, 13, 11))
            
def create_new_taxa_tables():
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
     
def taxa_insert():
    sql = """
        INSERT IGNORE INTO taxa (id, taxon, rank_id) SELECT id, taxon, rank_id FROM taxa_temp
    """
    shared.my_conn.execute_no_fetch(sql)    

def taxonomies_insert():
    sql = """
    INSERT IGNORE INTO taxonomies (superkingdom_id, phylum_id, class_id, orderx_id, family_id, genus_id, species_id, strain_id, created_at, updated_at) SELECT superkingdom_id, phylum_id, class_id, orderx_id, family_id, genus_id, species_id, strain_id, created_at, updated_at FROM taxonomies_sep
    """
    shared.my_conn.execute_no_fetch(sql)    
    
def process(args):
    tax_infile    = args.tax_infile
    ordered_names = "superkingdom", "phylum", "class", "orderx", "family", "genus", "species", "strain"
    bad_value     = "Fungi", "unculturedfungus", "unidentified", "sp", "sp.", "unculturedsoil_fungus", "unidentified_sp.", "unculturedcompost_fungus", "unculturedectomycorrhizal_fungus"
    old_taxonomy, time_stamps_ids  = make_taxa_dict(tax_infile, ordered_names)
    print "old_taxonomy = %s" % old_taxonomy
    separated_species_taxonomy = {}
    for tax_id, tax_line in old_taxonomy.items():
        separated_species_taxonomy[tax_id] = separate_binomial_name(tax_line)
    taxononomy_with_empty = {}
    for key, value in separated_species_taxonomy.items():
        taxononomy_with_empty[key] = make_empty_taxa(ordered_names, value)    
    taxonomy_with_wholes     = remove_bad_from_end(taxononomy_with_empty, bad_value, ordered_names)
    taxonomy_no_dup, dup_ids = remove_empty_and_get_dups(taxonomy_with_wholes)
    
    print "taxonomy_no_dup = %s" % taxonomy_no_dup
    print "dup_ids = %s" % dup_ids
    
    create_new_taxa_tables()
    
    for key, value in taxonomy_with_wholes.items():
        upload_new_taxonomy(ordered_names, key, value, time_stamps_ids[key])
    update_taxa_ranks_ids()    
    update_taxonomies_sep_ids(ordered_names)
    taxa_insert()
    taxonomies_insert()
    update_sequence_uniq_infos(dup_ids)
    
    
    
if __name__ == '__main__':
    shared.my_conn = sql_tables_class.MyConnection('localhost', 'vamps2')
    usage = "usage: %prog [options] arg1"
    parser = argparse.ArgumentParser(description='ref fasta/tax file creator')
    parser.add_argument('-it', '--tax_in', required=True, dest = "tax_infile",
                                                 help = '')   
    args = parser.parse_args() 
    
     

    # now do all the work
    process(args)

