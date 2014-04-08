#!/usr/bin/env ruby
require "rubygems"
require "json"
require "dbi"
require 'rest-client'
require 'uri'
require 'open-uri'

# gem install dbd-mysql
# todo: get all mysql results in one query

def use_args()
  if ARGV[0].nil?
    print "Please provide an input file name\n"
    exit
  end

  file_in_name  = ARGV[0]
  file_out_name = ARGV[1] ||= file_in_name + ".filered.csv"

  return file_in_name, file_out_name
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

def make_query_to_its(name)
  "SELECT DISTINCT taxonomy FROM env454.taxonomy JOIN env454.refhvr_its1 USING(taxonomy_id)
    WHERE taxonomy regexp BINARY " + name
end

def make_query_to_all_silva(content)
  query = "SELECT DISTINCT taxslv_silva_modified, silva_fullname
  FROM env454.refssu_115_from_file
   WHERE (silva_fullname REGEXP '[[:<:]]"
     
  content.each do |name|
    query += (name.strip.gsub(/"/,"")) + "[[:>:]]'"
    unless (name == content[content.size - 1])
      query += "OR silva_fullname REGEXP '[[:<:]]"     
    end
  end
  query += ") AND deleted = 0
  AND taxonomy = ''
  "
  return query
end


def time_method(method, *args)
  beginning_time = Time.now
  self.send(method, args)
  end_time = Time.now
  puts "Time elapsed #{(end_time - beginning_time)*1000} milliseconds"
end

def make_query_to_silva(name)
  "SELECT DISTINCT taxslv_silva_modified, silva_fullname
  FROM env454.refssu_115_from_file
   WHERE silva_fullname REGEXP '[[:<:]]" + name + "[[:>:]]'
   AND deleted = 0
  AND taxonomy = ''
  "
end

def get_its_info(dbh, name)
  its_res = run_query(dbh, make_query_to_its(name.strip))    
  if its_res[0].nil?
    genus_name = "'" + name.strip.gsub(/"/,"").split()[0] + "'"
    # print "genus_name = "
    # p genus_name
    its_res = run_query(dbh, make_query_to_its(genus_name))      
  end
  return its_res
end

begin
  n = 1
  mysql_read_default_file="~/.my.cnf"
  dsn = "DBI:Mysql:host=newbpcdb2;mysql_read_default_group=client"
  dbh = DBI.connect(dsn,nil,nil)

# --- main ---
  file_in_name, file_out_name = use_args()
  file_in  = open(file_in_name)
  content  = file_in.readlines
  file_out = File.open(file_out_name, "w")
  results  = []
  
  query_to_all_silva = make_query_to_all_silva(content)
  p "-" * 10
  beginning_time = Time.now
  res1 = run_query(dbh, query_to_all_silva)
  end_time = Time.now
  puts "Time 1 elapsed #{(end_time - beginning_time)*1000} milliseconds"
  print "res1 = "
  p res1
  
  p "+" * 10
  
  
  # time_method(run_query(dbh, query_to_all_silva))
  
  
  beginning_time = Time.now
  content.each do |name|
    row = Hash.new
    # testArray[i] = Hash.new
    # testArray[i][:value] = i
    
    row[:num] = n
    n += 1

    # print "HERE, name = "
    # p name.strip.gsub(/"/,"")
    
    # its_res = get_its_info(dbh, name)
    # its_res[0].nil? ? row[:its] = "" : row[:its] = its_res[0][0]
    
    current_silva = run_query(dbh, make_query_to_silva(name.strip.gsub(/"/,"")))
    unless current_silva[0].nil?  
      row[:taxslv_silva_modified] = current_silva[0][0]
      row[:silva_fullname]        = current_silva[0][1]
    end

    # print "HERE1, row = "
    # p row
    results << row
    
    # file_out.write(n)
    # file_out.write(to_print)   

  end
  end_time = Time.now
  puts "Time 2 elapsed #{(end_time - beginning_time)*1000} milliseconds"
  
  p "-" * 10
  print "HERE, results = "
  p results
  
  # what to do with the result:
    # 1) its = silva: print taxonomy
    # 2) its starts with silva 
    # 3) its != silva
  
# --- main ends ---

  rescue DBI::DatabaseError => e
    puts "An error occurred"
    puts "Error code: #{e.err}"
    puts "Error message: #{e.errstr}"
  ensure
    # disconnect from server
    dbh.disconnect if dbh    
end

file_out.close       unless file_out       == nil



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
# # def make_to_print(res)
# #   to_print = "-" * 10
# #   to_print += "\n"
# #   to_print += res["data_source_title"]
# #   to_print += "\n"
# #   to_print += res["classification_path"]
# #   to_print += "\n"
# #   to_print += res["classification_path_ranks"]
# #   to_print += "\n"
# #   to_print += res["taxon_id"]
# #   to_print += "\n"
# #   return to_print
# # end
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
