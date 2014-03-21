#!/usr/bin/env ruby
require "rubygems"
require "json"
require "dbi"
require 'rest-client'
require 'uri'

# gem install dbd-mysql


def use_args()
  if ARGV[0].nil?
    print "Please provide an input file name in json format\n"
    exit
  end

  file_in_name  = ARGV[0]
  file_out_name = ARGV[1] ||= file_in_name + ".filered.csv"

  rank_check    = ARGV[2] ||= "class"
  return file_in_name, file_out_name, rank_check
end



# def make_to_print(res)
#   to_print = "-" * 10
#   to_print += "\n"
#   to_print += res["data_source_title"]
#   to_print += "\n"
#   to_print += res["classification_path"]
#   to_print += "\n"
#   to_print += res["classification_path_ranks"]
#   to_print += "\n"
#   to_print += res["taxon_id"]
#   to_print += "\n"
#   return to_print
# end

def pair_name_rank(res)
  # p "HERE"
  # p res["classification_path"]
  classification_path       = res["classification_path"].split("|")
  classification_path_ranks = res["classification_path_ranks"].split("|")
  arr_combined = classification_path.zip(classification_path_ranks).flatten.compact
  result = arr_combined.each_slice(2). # get every two elements
      map { |top| "#{top.first} (#{top.last})" unless (top.first == "" and top.last == "") }.  # create a string for each pair
      join(';')    # join them
      # => "Bacteria (kingdom);Verrucomicrobia (phylum);Verrucomicrobiae (class)"
      
  return result  
end

def make_to_print_csv(res)
  to_print = res["data_source_title"]
  to_print += ";"  
  to_print += pair_name_rank(res)
  to_print += "\n"
  return to_print
end

def sort_by_taxonomy_ids(results)
  # sort by taxonomy_ids in interest
  results.sort_by { |element| [4, 11, 5, 8, 9, 1].index(element["data_source_id"]) }
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

def find_scientific_name(current_silva)
  current_silva_sc_name = ""
  current_silva_r       = ""
  
  current_silva.each do |cur_s|
    if (cur_s[-1] == cur_s[-1].capitalize)
      return cur_s
    end
  end
end

def current_silva_res(supplied_name_string, dbh, rank_check)
  current_silva_sc_name = ""
  current_silva_r       = ""
  
  query = "SELECT DISTINCT accession_id, taxslv_silva_modified, silva_fullname
     FROM env454.refssu_115_from_file 
     JOIN env454.refssu_taxslv_silva_modified_ranks USING(accession_id, START, STOP)
     WHERE `" + rank_check + "` = '" + supplied_name_string + "'
     AND deleted = 0
     AND taxonomy = ''
     order by silva_fullname
     limit 10
     ;"

  current_silva = run_query(dbh, query)

  unless current_silva[0].nil?  
    scientific_name_entry = find_scientific_name(current_silva)
  
    if scientific_name_entry[0].class == String
      current_silva_sc_name = scientific_name_entry[-1]
      current_silva_r       = scientific_name_entry.join(";")       
    end
    
    if current_silva_sc_name.empty?
      current_silva_sc_name = current_silva[0][-1]
      current_silva_r       = current_silva[0].join(";")     
    end    
  end
  return current_silva_r, current_silva_sc_name
end

def get_species(sc_name)
  RestClient.get(URI.escape("http://resolver.globalnames.org/name_resolvers.json?names="+ sc_name +"&resolve_once=false&data_source_ids=4|5"))  
end

def get_2tax_rank(res, rank_check, taxonomy_name)
  return true if ((res["classification_path_ranks"].split('|')[-1] == rank_check) && (res["data_source_title"] == taxonomy_name)) 
end

def to_print_NCBI_IF(to_print, parsed)
  begin  
    unless (parsed["data"].nil? or parsed["data"][0].nil? or parsed["data"][0]["results"].nil?)
      to_print += make_to_print_csv(parsed["data"][0]["results"][0])       
      to_print += make_to_print_csv(parsed["data"][0]["results"][1]) unless parsed["data"][0]["results"][1].nil?      
    end
  rescue Exception => e  
    p "*" * 10
    puts 'I am rescued. parsed = '  
    p parsed
    puts e.message  
    puts e.backtrace.inspect 
  end    
  return to_print  
end


def circle_json(dd, rank_check, dbh)
    current_silva_r, current_silva_sc_name = current_silva_res(dd["supplied_name_string"], dbh, rank_check)
    parsed  = JSON.parse(get_species(current_silva_sc_name))
    
    is_ncbi_class = false

    to_print  = "*" * 10
    to_print += "\n"
    to_print += dd["supplied_name_string"]
    to_print += "\n"  
    to_print += current_silva_r unless current_silva_r.nil?  
    to_print += "\n"
    to_print = to_print_NCBI_IF(to_print, parsed)
    to_print += "\n"
    to_print += "\n"

    current_tax_str  = ""
    previous_tax_str = ""

    unless dd["results"].nil?
      sort_by_taxonomy_ids(dd["results"]).each do |res| 
        is_ncbi_class = true if (get_2tax_rank(res, rank_check, "NCBI") == true || get_2tax_rank(res, rank_check, "GBIF Backbone Taxonomy") == true)
        # is_ncbi_class = true if ((res["classification_path_ranks"].split('|')[-1] == rank_check) && (res["data_source_title"] == "NCBI"))

        current_tax_str = res["classification_path"]

        to_print += make_to_print_csv(res) if current_tax_str != previous_tax_str
        to_print.sub! 'NCBI;;', 'NCBI;'

        previous_tax_str = current_tax_str
      end
    end
    # p to_print
    

  return to_print, is_ncbi_class
end
  
begin
  n = -1
  mysql_read_default_file="~/.my.cnf"
  dsn = "DBI:Mysql:host=newbpcdb2;mysql_read_default_group=client"
  dbh = DBI.connect(dsn,nil,nil)

# --- main ---
  file_in_name, file_out_name, rank_check = use_args()
  file_in = open(file_in_name)
  json    = file_in.read
  parsed  = JSON.parse(json)
  file_out = File.open(file_out_name, "w")
  # p "HERE, parsed = "
  # p parsed
  
  # add headers to csv
  file_out.write(";Kingdom;Phylum;Class;Order;Family;Genus;Species\n")
  parsed["data"].each do |dd|
    to_print, is_ncbi_class = circle_json(dd, rank_check, dbh)
    unless is_ncbi_class
      n += 1
      file_out.write(n)
      # file_out.write("\n")
      file_out.write(to_print)    
    end
  end
# --- main ends ---

  rescue DBI::DatabaseError => e
    puts "An error occurred"
    puts "Error code: #{e.err}"
    puts "Error message: #{e.errstr}"
  ensure
    # disconnect from server
    dbh.disconnect if dbh    
end

file_out.close unless file_out == nil

