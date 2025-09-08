from pathlib import Path
import xml.etree.ElementTree as ET
import re
from collections import Counter

from classify_varieties import preprocess_text

START_YEAR = 1997
END_YEAR = 2008
variety_token_counts = Counter()

def tokenize(text):
    # Tokenize based on whitespace and punctuation
    return re.findall(r'\w+', text)

for year in range(START_YEAR, END_YEAR + 1):
    xml_file = Path(__file__).parent.parent / "la_quotidiana" / f"rm_quotidiana_{year}.xml"
    assert xml_file.exists()
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for doc in root.findall('DOC'):
        text_parts = []
        for p in doc.find('TEXT').findall('P'):
            if p.text:
                text = preprocess_text(p.text)
                text_parts.append(text)
        article = "\n".join(text_parts).strip()
        variety = doc.get('{http://www.w3.org/XML/1998/namespace}lang', 'unknown')
        tokens = tokenize(article)
        variety_token_counts[variety] += len(tokens)

# Print the statistics in a formatted table
print("\n| Language variant     | IETF BCP47 language code |          Corpus size  |")
print("| -------------------- | ------------------------ | --------------------- |")

language_names = {
    'rm-sursilv': 'Rumantsch Sursilvan',
    'rm-vallader': 'Rumantsch Vallader',
    'rm-rumgr': 'Rumantsch Grischun',
    'rm-surmiran': 'Rumantsch Surmiran',
    'rm-puter': 'Rumantsch Puter',
    'rm-sutsilv': 'Rumantsch Sutsilvan',
    'unknown': 'Unknown'
}

# Sort varieties by token count (descending)
for variety, count in sorted(variety_token_counts.items(), key=lambda x: x[1], reverse=True):
    if variety in language_names:
        count_in_millions = count / 1_000_000
        formatted_count = f"{count_in_millions:.1f} million tokens"
        print(f"| {language_names[variety]:<20} | `{variety}`{' ' * (24 - len(variety))} | {formatted_count:>21} |")
