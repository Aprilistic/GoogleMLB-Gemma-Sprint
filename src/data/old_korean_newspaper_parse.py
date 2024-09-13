# Import necessary libraries
import rdflib
import csv
import re
from tqdm import tqdm

# Define the prefixes used in the Turtle data
prefixes = '''
@prefix nlk: <http://example.org/nlk#> .
@prefix nlon: <http://example.org/nlon#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dc: <http://purl.org/dc/elements/1.1/> .
@prefix dcterms: <http://purl.org/dc/terms/> .
'''

# Read the file content with appropriate encoding
with open('test.ttl', 'r', encoding='utf-8') as f:
    content = f.read()

# Split the content into individual elements separated by blank lines
elements = re.split(r'\n\s*\n', content.strip())

# Define the namespaces
nlon = rdflib.Namespace('http://example.org/nlon#')
nlk = rdflib.Namespace('http://example.org/nlk#')

# List to hold all data dictionaries
data_list = []

# Process each element
for element in tqdm(elements, desc="Processing elements"):
    # Combine prefixes with the element data
    data = prefixes + '\n' + element
    g = rdflib.Graph()
    try:
        # Parse the data using rdflib
        g.parse(data=data, format='turtle')
    except Exception as e:
        print('Error parsing element:', e)
        continue
    
    # Identify the main subjects (those with specific types)
    main_subjects = set()
    # Collect subjects with type nlon:OnlineMaterial or nlon:ElectronicJournal
    for s in g.subjects(rdflib.RDF.type, nlon.OnlineMaterial):
        main_subjects.add(s)
    for s in g.subjects(rdflib.RDF.type, nlon.ElectronicJournal):
        main_subjects.add(s)
    
    # For each main subject, extract data
    for s in main_subjects:
        data_dict = {}
        data_dict['id'] = s.n3(g.namespace_manager)
        for p, o in g.predicate_objects(subject=s):
            pred = p.n3(g.namespace_manager)
            # Check if the object is a Literal or URIRef
            if isinstance(o, rdflib.term.Literal):
                value = str(o)
            else:
                value = o.n3(g.namespace_manager)
            # Handle multiple values for the same predicate
            if pred in data_dict:
                data_dict[pred] += '; ' + value
            else:
                data_dict[pred] = value
        data_list.append(data_dict)

# Collect all field names
fieldnames = set()
for data_dict in data_list:
    fieldnames.update(data_dict.keys())
fieldnames = list(fieldnames)

# Write the data into a CSV file
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for data_dict in data_list:
        writer.writerow(data_dict)

print("Data has been successfully converted to 'output.csv'.")