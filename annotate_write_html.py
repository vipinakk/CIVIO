import urllib.request, urllib.error, urllib.parse
import json
import os
from pprint import pprint
import re
import copy
from nltk import tokenize

REST_URL = "http://data.bioontology.org"
API_KEY = "14d2e3b0-3b42-47c2-87eb-f39f238ecd81"

highlighter = {}

def get_json(url):
    opener = urllib.request.build_opener()
    opener.addheaders = [('Authorization', 'apikey token=' + API_KEY)]
    return json.loads(opener.open(url).read())

def print_annotations(annotations, get_class=True):
    highlighter.clear()
    for result in annotations:
        class_details = result["annotatedClass"]
        if get_class:
            try:
                class_details = get_json(result["annotatedClass"]["links"]["self"])
            except urllib.error.HTTPError:
                print(f"Error retrieving {result['annotatedClass']['@id']}")
                continue
        #print("Class details")
        #print("\tid: " + class_details["@id"])
        #print("\tprefLabel: " + class_details["prefLabel"])
        #print("\tontology: " + class_details["links"]["ontology"])

        #print("Annotation details")
        for annotation in result["annotations"]:
            #print("\ttext: " + annotation["text"])
            #print("\tfrom: " + str(annotation["from"]))
            #print("\tto: " + str(annotation["to"]))
            #print("\tmatch type: " + annotation["matchType"])

            span = (annotation["from"], annotation["to"])

            if span not in highlighter:
                highlighter[span] = annotation["text"]

        #print("\n\n")

path = 'data\\dialogue_dataset\\'
write_path = 'results\\dialogue_dataset\\'

long_sent_count = 0

for filename in os.listdir(path):
    if os.stat(path+filename).st_size != 0:
        with open(path+filename, 'r') as readfile:
            print('opening', filename)
            wrt_fname = filename.split('.')[0] + '.html'
            with open(write_path+wrt_fname, 'w', encoding='utf-8') as out_file:
                out_file.write('<html>')
                out_file.write('<body>')

                for line in readfile:
                    if len(line) > 1:
                        if line.startswith('id=') or line.startswith('https:'):
                            continue

                        line = re.sub(r"\[\*\*([A-Za-z0-9- ()]+)\*\*\]", "$$DEID$$", line)

                        text_to_annotate = line
                        try:
                            annotations = get_json(REST_URL + "/annotator?ontologies=CIVIO_1&longest_only=true&text=" + urllib.parse.quote(text_to_annotate))
                                
                            print_annotations(annotations)
                            #print(highlighter)

                            valid_high = copy.deepcopy(highlighter)

                            for k1 in highlighter:
                                for k2 in highlighter:
                                    if k1 != k2:
                                        if k1[0] <= k2[0] and k1[1] >= k2[1]:
                                            if k2 in valid_high:
                                                del valid_high[k2]

                            #print(valid_high)

                            sorted_spans = sorted(valid_high)
                            sorted_spans_matched = [(i[0]-1, i[1]-1) for i in sorted_spans]
                            print(sorted_spans)
                            begin_spans = [b-1 for (b,e) in sorted_spans]
                            end_spans = [e-1 for (b,e) in sorted_spans]
                                
                            text_annotated = ''
                            word = ''
                            i=0
                            while i < len(text_to_annotate):
                                flag = False
                                for s in sorted_spans_matched:
                                    word = text_to_annotate[s[0]:s[1]+1]
                                    if s[0] <= i <= s[1]:
                                        flag = True
                                        break
                                if flag is True:
                                    out_file.write('<mark><b>%s</b></mark>' %text_to_annotate[i])
                                    i = i+len(word)
                                else:
                                    out_file.write('%s' %text_to_annotate[i])
                                    i += 1

                            out_file.write('<br>')
                        except:
                            long_sent_count +=1
                            pass
                    else:
                        out_file.write('<br>')
                        #out_file.flush()
                out_file.write('</body>')
                out_file.write('</html>')      
            #out_file.close()
        readfile.close()

print(long_sent_count)
