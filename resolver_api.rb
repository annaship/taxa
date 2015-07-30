#!/usr/bin/env ruby
# file with names separated by newline as an argument
require 'rest-client'
require 'open-uri'

# puts RestClient.get(URI.escape("http://resolver.globalnames.org/name_resolvers.json?names=Plantago major&resolve_once=false&data_source_ids=1|3"))


# puts "GET request\n"
# puts RestClient.get(URI.escape("http://resolver.globalnames.org/name_resolvers.json?names=Plantago major|Monohamus galloprovincialis|Felis concolor&resolve_once=false&data_source_ids=1|3"))

# puts "\n\nPOST request with names and supplied IDs using 'names' parameter' \n"
# puts RestClient.post(resource_url, :format => "json", :names =>"Plantago major|Pardosa moesta L.|Felis concolor", :resolve_once => false, :data_source_ids => "1")

# puts "\n\nPOST request with names and supplied IDs using 'data' parameter' \n"
# puts RestClient.post(resource_url, :format => "json", :data =>"1|Plantago major\n2|Pardosa moesta L.\n3|Felis concolor", :resolve_once => false, :data_source_ids => "1")
# 
# if File.exists?('names_list.txt')
#     puts "\n\nPOST request with an uploaded file\n"
#     puts RestClient.post(URI.escape("http://resolver.globalnames.org/name_resolvers"), :format => "json", :file =>File.new("names_list.txt", "r:utf-8"), :resolve_once => false, :data_source_ids => "1")
# end

# 4	NCBI
# 11  GBIF Backbone Taxonomy

file_name = ARGV[0]
if File.exists?(file_name)
    puts RestClient.post(URI.escape("http://resolver.globalnames.org/name_resolvers"), :format => "json", :file =>File.new(file_name), :data_source_ids => "4", :best_match_only => true)
end

# file_name = ARGV[0]
# if File.exists?(file_name)
#     puts RestClient.post(URI.escape("http://resolver.globalnames.org/name_resolvers"), :format => "json", :file =>File.new(file_name), :data_source_ids => "4|11|5", :resolve_once => false, :preferred_data_sources => "4|11|5", :best_match_only => true)
# end

# if File.exists?(file_name)
#     puts RestClient.post(URI.escape("http://resolver.globalnames.org/name_resolvers"), :format => "json", :file =>File.new(file_name), :data_source_ids => "4", :resolve_once => true, :best_match_only => true)
# end
# , :best_match_only => true

# puts RestClient.post(URI.escape("http://resolver.globalnames.org/name_resolvers"), :format => "json", :file =>File.new(file_name), :resolve_once => false, :data_source_ids => "4|1|5|8|9|11")
