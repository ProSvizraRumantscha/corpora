import re
from pathlib import Path
import xml.etree.ElementTree as ET
from joblib import load
from tqdm import tqdm

START_YEAR = 1997
END_YEAR = 2008

def preprocess_text(text: str) -> str:
    text = text.strip().replace("\n", " ")
    if text.startswith("■ "):
        text = text[2:]
    # Remove page number references and any leading space
    text = re.sub(r'\s*\(p\.\s*\d+\)', '', text)
    # Remove leading parenthetical references like (anr/grc)
    text = re.sub(r'^\s*\([^)]+\)\s*', '', text).strip()
    return text

if __name__ == "__main__":
    svm_classifier = load(Path(__file__).parent / "classification_model" / "svm_char_word.joblib")
    doc_to_variety_map = dict()
    for year in range(START_YEAR, END_YEAR + 1):
        xml_file = Path(__file__).parent.parent / "la_quotidiana" / f"rm_quotidiana_{year}.xml"
        assert xml_file.exists()
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for doc in tqdm(list(root.findall('DOC')), desc=f"Processing year {year}"):
            text_parts = []
            for p in doc.find('TEXT').findall('P'):
                if p.text:
                    text = preprocess_text(p.text)
                    text_parts.append(text)
            article = "\n".join(text_parts).strip()
            doc_id = doc.attrib['id']
            predicted_label = svm_classifier.predict([article])[0]
            doc_to_variety_map[doc_id] = predicted_label

    # Update the XML files with predicted varieties
    for year in range(START_YEAR, END_YEAR + 1):
        xml_file = Path(__file__).parent.parent / "la_quotidiana" / f"rm_quotidiana_{year}.xml"
        tree = ET.parse(xml_file)
        root = tree.getroot()

        for doc in root.findall('DOC'):
            doc_id = doc.attrib['id']
            if doc_id in doc_to_variety_map:
                # Set the xml:lang attribute to the predicted variety
                doc.set('{http://www.w3.org/XML/1998/namespace}lang', doc_to_variety_map[doc_id])

        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        print(f"Updated language attributes in {xml_file}")
