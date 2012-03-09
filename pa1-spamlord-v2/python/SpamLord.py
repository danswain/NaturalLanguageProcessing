import sys
import os
import re
import pprint
    

""" 
TODO
This function takes in a filename along with the file object (or
an iterable of strings) and scans its contents against regex patterns.
It returns a list of (filename, type, value) tuples where type is either
and 'e' or a 'p' for e-mail or phone, and value is the formatted phone
number or e-mail.  The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***, as it will be called directly by
the submit script
"""
def process_file(name, f):
    res = []

    for line in f:
        email_results = process_email(name,line)
        phone_results = process_phone(name,line)    
        res.extend(email_results)
        res.extend(phone_results)   
        
        email_num = len(email_results)
        phone_num = len(phone_results)
        #if email_num >0 or phone_num >0:
        #    sys.stderr.write('email->%s phone->%s result->%s -- %s\r\n' % (email_num,phone_num,len(res),name))    
    
    return res



def process_email(name, line):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []

    email_pattern = '([\w.]+)\s?@\s?([\w.]+).edu'
    matches = re.findall(email_pattern,line, re.IGNORECASE)

    hyphenated_matches = process_hyphenated_email(name,line)
    matches.extend(hyphenated_matches)
    
    language_matches = process_language_based_email(name,line)
    matches.extend(language_matches)

    words_for_symbols_matches = process_words_for_symbols_email(name,line)
    matches.extend(words_for_symbols_matches)
    
    javascript_matches = process_javascript_email(name,line)
    matches.extend(javascript_matches)

    simple_at_word_matches = process_simple_at_word(name,line)
    matches.extend(simple_at_word_matches)
    
    for m in matches:
        email = '%s@%s.edu' % m
        res.append((name,'e',email))
    return res

def process_simple_at_word(name,line):
    return []
    pattern = '([a-z]+) at ([a-z.]+).edu'
    results = re.findall(name,line,re.IGNORECASE)
    return results

def process_javascript_email(name,line):
    matches = []
    pattern = "'([a-z]+)\.edu','([a-z]+)'"
    results = re.findall(pattern,line,re.IGNORECASE)
    
    for match in results:        
        beforeAt = match[1]
        afterAt = match[0]
        sys.stderr.write('%s @ %s' % (beforeAt,afterAt))
        matches.append((beforeAt,afterAt))

    return matches    

def process_words_for_symbols_email(name,line):
    matches = []
    #pattern = '([a-z]+) at([a-z ]+)dot edu'
    pattern = '([a-z]+) at([a-z; ]+)(dot |;)edu'
    results = re.findall(pattern,line,re.IGNORECASE)
    for match in results:
        beforeAt = match[0].replace("dot",'.').replace(';','.').replace(' ','')
        afterAt = match[1].replace("dot",'.').replace(';','.').replace(' ','')
        matches.append((beforeAt,afterAt))
    return matches

def process_language_based_email(name,line):
    pattern = '(\w+) [A-Z]+ ([a-z]+) [A-Z]+ edu'
    matches = []    

    results = re.findall(pattern,line);
    
    return results

def process_hyphenated_email(name,line):    
    matches = []
    hyphenated_email_pattern = '([.a-z-]+)@([.a-z-]+)\.[-edu]+'
    hyphenated_matches = re.findall(hyphenated_email_pattern,line,re.IGNORECASE);
    
    for hyphenated_match in hyphenated_matches:
        #sys.stderr.write(hyphenated_match[1])
        beforeAt = hyphenated_match[0].replace('-','')
        afterAt =  hyphenated_match[1].replace('-','')       
        #sys.stderr.write('%s ----- %s %s == %s\r\n' % (hyphenated_match,beforeAt,afterAt,name))
        matches.append((beforeAt,afterAt))
    return matches

def process_phone(name, line):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    phone_number_pattern = '(\d{3})[\) -][ ]?(\d{3})[\) -](\d{4})'
    
    matches = re.findall(phone_number_pattern,line)
    for m in matches:
        phone = '%s-%s-%s' % m
        res.append((name,'p',phone))
    return res


"""
You should not need to edit this function, nor should you alter
its interface as it will be called directly by the submit script
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
          continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print 'True Positives (%d): ' % len(tp)
    pp.pprint(tp)
    print 'False Positives (%d): ' % len(fp)
    pp.pprint(fp)
    print 'False Negatives (%d): ' % len(fn)
    pp.pprint(fn)
    print 'Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print 'usage:\tSpamLord.py <data_dir> <gold_file>'
        sys.exit(0)
    main(sys.argv[1],sys.argv[2])
    raw_input('Press Enter to CLOSE')
