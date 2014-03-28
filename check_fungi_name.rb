#!/usr/bin/env ruby

# /*
# From a file of genus names
# Acineta
# Actinomucor
# Actinoplanes
# 
# 1) get taxslv_silva_modified
# SELECT DISTINCT taxslv_silva_modified 
# FROM refssu_115_from_file 
# JOIN refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP)
#  WHERE 
# `family` = "Asterotremella"
# AND deleted = 0
# AND taxonomy = ""
# 
# 2) get data from refhvr_its
# 
# SELECT DISTINCT taxonomy FROM `refhvr_its1` JOIN taxonomy USING(taxonomy_id) WHERE taxonomy REGEXP "[[:<:]]Asterotremella[[:>:]]";
# 
# 3)
# make "Update" queries 
# 
# Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Asterotremella
# Eukarya;Fungi_Basidiomycota;Tremellomycetes;Trichosporonales;Trichosporonaceae;Asterotremella
# IF: Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Asterotremellaceae
# 
# 
# UPDATE refssu_115_from_file JOIN refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP) SET taxslv_silva_modified = replace(taxslv_silva_modified, "$1$2", "$3"), taxslv_silva_modification = concat(taxslv_silva_modification, "; $2 (genus) by Unite") WHERE taxslv_silva_modified like '$1$2'
# "UPDATE refssu_115_from_file JOIN refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP) SET taxslv_silva_modified = replace(taxslv_silva_modified, 'Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Asterotremella', 'Eukarya;Fungi_Basidiomycota;Tremellomycetes;Trichosporonales;Trichosporonaceae;Asterotremella'), taxslv_silva_modification = concat(taxslv_silva_modification, '; Asterotremella (genus) by Unite') WHERE taxslv_silva_modified like 'Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Asterotremella';\n    "

# */

require "rubygems"
require "json"
require "dbi"
require 'rest-client'
require 'uri'
require 'open-uri'

# gem install dbd-mysql

class GenusName
  attr_accessor :genus_name, :taxslv_silva_modified, :refhvr_its1
  
  def initialize
    @genus_name            = ""
    @taxslv_silva_modified = ""
    @refhvr_its1           = ""
  end
  
  # def taxslv_silva_modified=(value)
  #   @taxslv_silva_modified = value[0] if value.class == Array
  # end
  # 
  # def refhvr_its1=(value)
  #   @refhvr_its1 = value[0] if value.class == Array
  # end
  
  
  
    
  def make_update_query()
    query = 
    "UPDATE refssu_115_from_file 
      SET taxslv_silva_modified = replace(taxslv_silva_modified, '#{@taxslv_silva_modified}', '#{@refhvr_its1}'), 
          taxslv_silva_modification = concat(taxslv_silva_modification, '; #{@genus_name} (genus) by Unite') 
      WHERE taxslv_silva_modified like '#{@taxslv_silva_modified}';
    "
  end
end

# --- main ---

def use_args()
  if ARGV[0].nil?
    print "Please provide an input file name\n"
    exit
  end

  file_in_name  = ARGV[0]
  return file_in_name
end

def run_query(dbh, query)
  query_result = []
  # query = "SELECT * FROM env454.refssu_115_from_file limit ?;"
  
  sth = dbh.prepare(query)
  sth.execute()
  sth.each {|row| query_result << row.to_a }
  sth.finish
  return query_result
end

def make_taxslv_silva_modified_query(genus_names)
  query = 
  "SELECT DISTINCT taxslv_silva_modified 
      FROM env454.refssu_115_from_file 
      JOIN env454.refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP)
      WHERE family in (#{genus_names})
      AND deleted = 0
      AND taxonomy = '';
  "
end

def make_refhvr_its_query(genus_names_arr)
  # print "genus_names from 1 = "
  # p genus_names
  # genus_names_arr = genus_names.split(",")
  # print "genus_names_arr from 1 = "
  # p genus_names_arr
  query = "SELECT DISTINCT taxonomy FROM env454.refhvr_its1 JOIN env454.taxonomy USING(taxonomy_id) WHERE "
  genus_names_arr[0...-1].each do |genus_name|
    query += " taxonomy REGEXP '[[:<:]]#{genus_name.tr("'", "")}[[:>:]]' OR "
  end
  query += "taxonomy REGEXP '[[:<:]]#{genus_names_arr[-1].tr("'", "")}[[:>:]]';"
  return query
end


begin
  n = -1
  mysql_read_default_file="~/.my.cnf"
  dsn = "DBI:Mysql:host=newbpcdb2;mysql_read_default_group=client"
  dbh = DBI.connect(dsn,nil,nil)
  contents = ""
  
  file_in_name = use_args()
  # contents = File.readlines(file_in_name)
  
  File.readlines(file_in_name).each do |line|
    contents += line.strip
  end
  print "contents = "
  p contents
  taxslv_silva_modified_query =  make_taxslv_silva_modified_query(contents)
 # print "taxslv_silva_modified_query = " 
 # p taxslv_silva_modified_query
  taxslv_silva_modified_res = run_query(dbh, make_taxslv_silva_modified_query(contents))
 # p res
 
 
 contents_arr = 
 contents_arr = contents.split(",")
 print "contents_arr from 2 = "
 p contents_arr
 
 
 refhvr_its_res_query =  make_refhvr_its_query(contents_arr)
  refhvr_its_res            = run_query(dbh, refhvr_its_res_query)
  p "refhvr_its_res = "
  p refhvr_its_res
 
 # [["Eukarya;Fungi_Zygomycota;Unassigned;Mucorales;Actinomucor"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Incertae_sedis;Ambomucor"], ["Eukarya;Fungi_Chytridiomycota;Chytridiomycetes;Polychytriales;Arkaya"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Asterotremella"], ["Eukarya;Fungi_Zygomycota;Unassigned;Mucorales;Backusella"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Biatoropsis"], ["Eukarya;Fungi_Chytridiomycota;Chytridiomycetes;Chytridiales;Blyttiomyces"], ["Eukarya;Fungi_Chytridiomycota;Chytridiomycetes;Rhizophydiales;Boothiomyces"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Bullera"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Bulleromyces"]]
  
  # [["Eukarya;Fungi_Chytridiomycota;Chytridiomycetes;Rhizophydiales;Terramycetaceae;Boothiomyces"], ["Eukarya;Fungi_Chytridiomycota;Chytridiomycetes;Rhizophydiales;Terramycetaceae;Boothiomyces;macroporosum"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Mucoraceae;Actinomucor"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Mucoraceae;Actinomucor;elegans"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Incertae_sedis;Biatoropsis;usnearum"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Incertae_sedis;Bullera"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Incertae_sedis;Bullera;arundinariae"],  ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Tremellales;Incertae_sedis;Bulleromyces;albus"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Trichosporonales;Trichosporonaceae;Asterotremella"], ["Eukarya;Fungi_Basidiomycota;Tremellomycetes;Trichosporonales;Trichosporonaceae;Asterotremella;albida"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Backusellaceae;Backusella;circina"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Backusellaceae;Backusella;indica"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Backusellaceae;Backusella;variabilis"], ["Eukarya;Fungi_Zygomycota;Incertae_sedis;Mucorales;Incertae_sedis;Ambomucor"]]
  
  
  # contents.each do |line|
  #   instance = GenusName.new
  #   instance.genus_name            = line.strip
    # instance.taxslv_silva_modified = run_query(dbh, instance.make_taxslv_silva_modified_query())
 #    instance.refhvr_its1           = run_query(dbh, instance.make_refhvr_its_query())
 #    update_query                   = instance.make_update_query() unless instance.refhvr_its1.nil?
 #    
 # file_out = File.open("update_fung_genus.sql", "a")
 # file_out.write(update_query)
    
    
    # p "+" * 10
    # p instance.taxslv_silva_modified
    # p instance.refhvr_its1
    # p update_query
    # begin
    #   p instance.refhvr_its1[0].class
    #   p instance.refhvr_its1[0].length
    # rescue StandardError => e
    #   p e
    # end
  # end
  # file_out.close unless file_out == nil

# --- main ends ---

  rescue DBI::DatabaseError => e
    puts "An error occurred"
    puts "Error code: #{e.err}"
    puts "Error message: #{e.errstr}"
  ensure
    # disconnect from server
    dbh.disconnect if dbh    
end



# 
# def use_args()
#   if ARGV[0].nil?
#     print "Please provide an input file name in json format\n"
#     exit
#   end
# 
#   file_in_name  = ARGV[0]
#   file_out_name = ARGV[1] ||= file_in_name + ".filered.csv"
# 
#   rank_check    = ARGV[2] ||= "class"
#   return file_in_name, file_out_name, rank_check
# end
# 
# 
# 
# def pair_name_rank(res)
#   # p "HERE"
#   # p res["classification_path"]
#   unless res["classification_path"].nil?
#     classification_path       = res["classification_path"].split("|")
#     classification_path_ranks = res["classification_path_ranks"].split("|")
#     arr_combined = classification_path.zip(classification_path_ranks).flatten.compact
#     result = arr_combined.each_slice(2). # get every two elements
#         map { |top| "#{top.first} (#{top.last})" unless (top.first == "" and top.last == "") }.  # create a string for each pair
#         join(';')    # join them
#         # => "Bacteria (kingdom);Verrucomicrobia (phylum);Verrucomicrobiae (class)"
#       
#     return result  
#   end
# end
# 
# def make_to_print_csv(res)
#   to_print = res["data_source_title"]
#   to_print += ";"  
#   to_print += pair_name_rank(res) unless pair_name_rank(res).nil?
#   to_print += "\n"
#   return to_print
# end
# 
# def sort_by_taxonomy_ids(results)
#   # sort by taxonomy_ids in interest
#   begin  
#     return results.sort_by { |element| [4, 11, 5, 8, 9, 1].index(element["data_source_id"])} 
#   rescue Exception => e  
#     return results
#     print "sort_by_taxonomy_ids failed: "
#     puts e.message  
#     puts e.backtrace.inspect 
#   end  
# end
# 
# 
# def run_query(dbh, query)
#   query_result = []
#   # query = "SELECT * FROM env454.refssu_115_from_file limit ?;"
#   
#   sth = dbh.prepare(query)
#   sth.execute()
#   sth.each {|row| query_result << row.to_a }
#   sth.finish
#   return query_result
#   
# end
# 
# def find_scientific_name(current_silva)
#   current_silva_sc_name = ""
#   current_silva_r       = ""
#   
#   current_silva.each do |cur_s|
#     if (cur_s[-1] == cur_s[-1].capitalize)
#       return cur_s
#     end
#   end
# end
# 
# def current_silva_res(supplied_name_string, dbh, rank_check)
#   current_silva_sc_name = ""
#   current_silva_r       = ""
#   
#   query = "SELECT DISTINCT accession_id, taxslv_silva_modified, silva_fullname
#      FROM env454.refssu_115_from_file 
#      JOIN env454.refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP)
#      WHERE `" + rank_check + "` = '" + supplied_name_string + "'
#      AND deleted = 0
#      AND taxonomy = ''
#      order by silva_fullname
#      limit 10
#      ;"
# 
#   current_silva = run_query(dbh, query)
# 
#   unless current_silva[0].nil?  
#     scientific_name_entry = find_scientific_name(current_silva)
#   
#     if scientific_name_entry[0].class == String
#       current_silva_sc_name = scientific_name_entry[-1]
#       current_silva_r       = scientific_name_entry.join(";")       
#     end
#     
#     if current_silva_sc_name.empty?
#       current_silva_sc_name = current_silva[0][-1]
#       current_silva_r       = current_silva[0].join(";")     
#     end    
#   end
#   return current_silva_r, current_silva_sc_name
# end
# 
# def get_species(sc_name)
#   begin  
#     return RestClient.get(URI.escape("http://resolver.globalnames.org/name_resolvers.json?names="+ sc_name +"&resolve_once=false&data_source_ids=4|5"))  
#   rescue Exception => e  
#     p "*" * 10
#     puts 'I am rescued at get_species. sc_name = '  
#     p sc_name
#     puts e.message  
#     puts e.backtrace.inspect 
#     return nil
#   end    
#     
# end
# 
# # not used, check if rank only in one taxonomy
# def get_2tax_rank(res, rank_check, taxonomy_name)
#   return true if ((res["classification_path_ranks"].split('|')[-1] == rank_check) && (res["data_source_title"] == taxonomy_name)) 
# end
# 
# def is_tax_rank(res, rank_check)
#   return true if (res["classification_path_ranks"].split('|')[-1] == rank_check) 
# end
# 
# 
# def to_print_NCBI_IF(to_print, parsed)
#   begin  
#     unless (parsed["data"].nil? or parsed["data"][0].nil? or parsed["data"][0]["results"].nil?)
#       to_print += make_to_print_csv(parsed["data"][0]["results"][0])       
#       to_print += make_to_print_csv(parsed["data"][0]["results"][1]) unless parsed["data"][0]["results"][1].nil?      
#     end
#   rescue Exception => e  
#     p "*" * 10
#     puts 'I am rescued. parsed = '  
#     p parsed
#     puts e.message  
#     puts e.backtrace.inspect 
#   end    
#   return to_print  
# end
# 
# def get_genus(dd, rank_check) 
#   file_out_genus_name = "genus_from_" + rank_check.to_s
#   file_out_genus      = File.open(file_out_genus_name, "a")
#   add_to_genus        = []
#   # p dd
#   unless dd["results"].nil?  
#     dd["results"].each do |res| 
#       if (res["classification_path_ranks"].split('|')[-1] == "genus") 
#         add_to_genus << dd["supplied_name_string"]
#       end
#     end
#   end
#   add_to_genus.uniq!
#   genus_name = add_to_genus.join()
#   # make_genus('order', genus_name)
#   file_out_genus.write(add_to_genus.join() + "\n")     
#   file_out_genus.close unless file_out_genus == nil  
# end
# 
# def make_genus(rank, genus_name)
#   query = 'UPDATE refssu_115_from_file JOIN refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP) SET taxslv_silva_modified = replace(taxslv_silva_modified, "' + orig_string + '", "' + orig_string_part + ';Unassigned;Unassigned;' + genus_name + '"), taxslv_silva_modification = concat(taxslv_silva_modification, "; ' + genus_name + ' (genus)") WHERE taxslv_silva_modified like "' + orig_string + '%" AND deleted = 0 AND taxonomy = "" 
#   '
#   p query
# end
# 
# def circle_json(dd, rank_check, dbh)
#     # start = Time.now
#     current_silva_r, current_silva_sc_name = current_silva_res(dd["supplied_name_string"], dbh, rank_check)
#     # finish = Time.now
#     # diff = finish - start
#     # print "current_silva_res: "
#     # p diff.round(2)
#     
#     # start = Time.now
#     parsed  = JSON.parse(get_species(current_silva_sc_name)) if get_species(current_silva_sc_name)
#     # finish = Time.now
#     # diff = finish - start
#     # print "parse(get_species...: "
#     # p diff.round(2)
#     
#     is_correct_rank = false
# 
#     to_print  = "*" * 10
#     to_print += "\n"
#     to_print += dd["supplied_name_string"]
#     to_print += "\n"  
#     to_print += current_silva_r unless current_silva_r.nil?  
#     to_print += "\n"
# 
#     # start = Time.now
#     to_print = to_print_NCBI_IF(to_print, parsed)
#     # finish = Time.now
#     # diff = finish - start
#     # print "to_print_NCBI_IF...: "
#     # p diff.round(2)
#     
#     to_print += "\n"
#     to_print += "\n"
# 
#     current_tax_str  = ""
#     previous_tax_str = ""
# 
#     # start1 = Time.now
#     # p "-=" * 10
# 
#     unless dd["results"].nil?
#       sort_by_taxonomy_ids(dd["results"]).each do |res| 
#         # print "is_correct_rank = "
#         # p is_correct_rank
#         if is_correct_rank == false
#           # p "FROM INSIDE IF"
#           # start = Time.now
#           is_correct_rank = true if is_tax_rank(res, rank_check) == true
#           # finish = Time.now
#           # diff = finish - start
#           # print "is_tax_rank...: "
#           # p diff.round(2)
#           # is_correct_rank = true if (get_2tax_rank(res, rank_check, "NCBI") == true || get_2tax_rank(res, rank_check, "GBIF Backbone Taxonomy") == true)
#           # is_correct_rank = true if ((res["classification_path_ranks"].split('|')[-1] == rank_check) && (res["data_source_title"] == "NCBI"))
# 
#           current_tax_str = res["classification_path"]
# 
#           to_print += make_to_print_csv(res) if current_tax_str != previous_tax_str
#           to_print.sub! 'NCBI;;', 'NCBI;'
#         end
# 
#         previous_tax_str = current_tax_str
#       end
#     end
#     # p to_print
#     # finish1 = Time.now
#     # diff1 = finish1 - start1
#     # print 'unless dd["results"].nil...: '
#     # p diff1.round(2)
#     
# 
#   return to_print, is_correct_rank
# end
#   
# begin
#   n = -1
#   mysql_read_default_file="~/.my.cnf"
#   dsn = "DBI:Mysql:host=newbpcdb2;mysql_read_default_group=client"
#   dbh = DBI.connect(dsn,nil,nil)
# 
# # --- main ---
#   file_in_name, file_out_name, rank_check = use_args()
#   file_in = open(file_in_name)
#   json    = file_in.read
#   parsed  = JSON.parse(json)
#   file_out = File.open(file_out_name, "w")
#   # p "HERE, parsed = "
#   # p parsed
#   
#   # add headers to csv
#   file_out.write(";Kingdom;Phylum;Class;Order;Family;Genus;Species\n")
#   parsed["data"].each do |dd|
#     to_print, is_correct_rank = circle_json(dd, rank_check, dbh)
#     unless is_correct_rank
#       n += 1
#       file_out.write(n)
#       # file_out.write("\n")
#       file_out.write(to_print)   
#       get_genus(dd, rank_check) 
#     end
#   end
# # --- main ends ---
# 
#   rescue DBI::DatabaseError => e
#     puts "An error occurred"
#     puts "Error code: #{e.err}"
#     puts "Error message: #{e.errstr}"
#   ensure
#     # disconnect from server
#     dbh.disconnect if dbh    
# end
# 
# file_out.close       unless file_out       == nil
