# Tool for exporting the corpus content into tab-separated files.
#
# The output is a ZIP file ("la_quotidiana.zip") with a single
# tab-seprated plaintext file (*.tsv) for each language variant.
#
# The individual files have the following columns:
#
# * paragraph_id: an identifier for the paragraph.
#
# * publication_year: the year of publication, such as 2004.
#
# * text: the text of the paragraph.

from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET
import zipfile

def export_plaintext():
    path = Path(__file__).parent / "la_quotidiana"
    out = {}
    for root, _, files in path.walk():
        for f in sorted(files):
            if m := re.search(r'^rm_quotidiana_(\d{4}).xml$', f):
                year = m.group(1)
                tree = ET.parse(root / f).getroot()
                for doc in tree.findall('DOC'):
                    id = doc.attrib["id"]
                    lang = doc.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                    if lang not in out:
                        out[lang] = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
                        out[lang].write("paragraph_id\tpublication_year\ttext\n")
                    for p in doc.find("TEXT").findall("P"):
                        text = " ".join(p.text.split())
                        out[lang].write("\t".join([id, year, text]) + "\n")
    with zipfile.ZipFile(
            "la_quotidiana.zip",
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
    ) as zf:
        for lang, fp in sorted(out.items()):
            fp.seek(0)
            zf.writestr(f"{lang}.tsv", fp.read())

if __name__ == "__main__":
    export_plaintext()

