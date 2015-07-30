def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)

def check_if_bad(word):
  bad_list = ["uncultured", "unknown", "group", "family", "symbiont", "mitochondria", "unidentified", "metagenome", "agent", "sample" "(", ")"]
  return len([l for l in bad_list if l.lower() in word.lower()]) > 0 or word.lower().startswith("sub") or hasNumbers(word)
  
""" main """
fname   = "newbpcdb2_119_empty_clean_7-30-15.csv"
my_dict = {}

with open(fname) as f:
    content = f.readlines()

for line in content:
   # print line.split(',')[1].split(';')
   my_dict[line.split(',')[0]] = line.split(',')[1].split(';')

prev_name = ""
curr_name = ""
        
out_file_name = "out_to_search.txt"
out_file = open(out_file_name, "w")

for k, v in my_dict.iteritems():
    for name in v:
      curr_name = name
      if check_if_bad(name):
        break
      else:
        prev_name = name
    out_file.write(prev_name + "\n")
