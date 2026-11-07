from docx import Document
d = Document("技术方案_酒店人脸比对.docx")
h1 = [p.text for p in d.paragraphs if p.style.name == "Heading 1"]
print("H1:", len(h1))
for t in h1: print("  ", t)
print("H2:", sum(1 for p in d.paragraphs if p.style.name == "Heading 2"))
print("tables:", len(d.tables), " paragraphs:", len(d.paragraphs))
print("images:", len(d.inline_shapes))
