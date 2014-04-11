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
  file_out_name = ARGV[1] ||= file_in_name + ".check.csv"

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
    WHERE taxonomy regexp BINARY '#{name}'"
end

def make_query_to_silva(name)
  "SELECT DISTINCT taxslv_silva_modified, silva_fullname
  FROM env454.refssu_115_from_file
   WHERE silva_fullname REGEXP '[[:<:]]#{name}[[:>:]]'
   AND deleted = 0
  AND taxonomy = ''
  "
end

def get_its_info(dbh, name)
  its_res = run_query(dbh, make_query_to_its(name))    
  if its_res[0].nil?
    genus_name = name.split()[0]
    # print "genus_name = "
    # p genus_name
    its_res = run_query(dbh, make_query_to_its(genus_name))      
  end
  return its_res
end

def check_sim(row)
  row[:check] = ""
  begin
    if (row[:its] == row[:taxslv_silva_modified])
      row[:check] = "same"
    elsif row[:its].start_with?(row[:taxslv_silva_modified])
      row[:check] = "in its"      
    elsif row[:taxslv_silva_modified].start_with?(row[:its])
      row[:check] = "in silva"      
    end
  rescue Exception => e  
    print "check_sim failed for row: "
    p row
    puts e.message  
    puts e.backtrace.inspect 
  end
  return row
end
  
begin
  n = 1
  mysql_read_default_file="~/.my.cnf"
  dsn = "DBI:Mysql:host=newbpcdb2;mysql_read_default_group=client"
  dbh = DBI.connect(dsn,nil,nil)

# --- main ---
  file_in_name, file_out_name = use_args()
  file_in  = open(file_in_name)
  content  = file_in.readlines.collect{|x| x.strip.gsub(/"/,"")}
  file_out = File.open(file_out_name, "w")
  results  = []
  
  content.each do |name|
    row = Hash.new
    
    row[:name] = name
    row[:num]  = n
    n += 1

    # print "HERE, name = "
    # p name
    
    its_res = get_its_info(dbh, name)
    its_res[0].nil? ? row[:its] = "" : row[:its] = its_res[0][0]
    
    current_silva = run_query(dbh, make_query_to_silva(name))
    unless current_silva[0].nil?  
      row[:taxslv_silva_modified] = current_silva[0][0]
      row[:silva_fullname]        = current_silva[0][1]
    end

    row = check_sim(row)
    print "HERE, row = "
    p row

    
    results << row
    
    # file_out.write(n)
    # file_out.write(to_print)   

  end
  p "-" * 10
  # print "HERE, results = "
  # p results
  
  # what to do with the result:
    # 1) its = silva: print taxonomy
    # 2) its starts with silva 
    # 3) its != silva
    
  # results.each do |row|
  #   row[:check] = ""
  #   unless row[:its].nil?
  #     if (row[:its] == row[:taxslv_silva_modified])
  #       row[:check] = "same"
  #     elsif row[:its].start_with?(row[:taxslv_silva_modified])
  #       row[:check] = "in its"      
  #     elsif row[:taxslv_silva_modified].start_with?(row[:its])
  #       row[:check] = "in silva"      
  #     end
  #   end
  # end
  
    # 1,same,Eukarya;Fungi_Ascomycota;Lecanoromycetes;Acarosporales;Acarosporaceae;Acarospora,Eukarya;Fungi_Ascomycota;Lecanoromycetes;Acarosporales;Acarosporaceae;Acarospora,Acarospora smaragdula var. lesdainii,Acarospora smaragdula,smaragdula
        
  file_out.write(",check,its taxonomy,taxslv_silva_modified,silva_fullname,genus?,species?\n")

  results.each do |row|    
    file_out.write(row[:num]) 
    file_out.write(",") 
    file_out.write(row[:check]) 
    file_out.write(",") 
    file_out.write(row[:its]) 
    file_out.write(",") 
    file_out.write(row[:taxslv_silva_modified]) 
    file_out.write(",") 
    file_out.write(row[:silva_fullname]) 
    file_out.write(",") 
    file_out.write(row[:name])     
    file_out.write(",") 
    file_out.write(row[:name].split()[1])     
    file_out.write("\n") 
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

file_out.close       unless file_out       == nil
