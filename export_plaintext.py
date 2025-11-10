# Tool for exporting the corpus content into plaintext files.
#
# The output is a ZIP file ("la_quotidiana.zip") with a single
# plaintext file for each language variant. The individual files
# have the text of each paragraph on a seprate line.

from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import zipfile

def export_plaintext():
    path = Path(__file__).parent / "la_quotidiana"
    out = {}
    for root, _, files in path.walk():
        for f in sorted(files):
            if f.endswith('.xml'):
                tree = ET.parse(root / f).getroot()
                for doc in tree.findall('DOC'):
                    lang = doc.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
                    if lang not in out:
                        out[lang] = tempfile.TemporaryFile(mode="w+", encoding="utf-8")
                    for p in doc.find("TEXT").findall("P"):
                        text = " ".join(p.text.split())
                        out[lang].write(text + "\n")
    with zipfile.ZipFile(
            "la_quotidiana.zip",
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
    ) as zf:
        for lang, fp in sorted(out.items()):
            fp.seek(0)
            zf.writestr(f"{lang}.txt", fp.read())

if __name__ == "__main__":
    export_plaintext()

