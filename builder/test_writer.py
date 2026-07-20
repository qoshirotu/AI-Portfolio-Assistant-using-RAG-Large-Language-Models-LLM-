from builder.llm_builder import KnowledgeBuilder
from builder.parser import KnowledgeParser
from builder.writer import KnowledgeWriter

builder = KnowledgeBuilder()

parser = KnowledgeParser()

writer = KnowledgeWriter()

text = """

Real-Time Plastic Waste Detection

Developed AI system using YOLO.

"""

knowledge = builder.generate(text)

parsed = parser.parse(knowledge)

if parser.validate(parsed):

    result = writer.save(parsed)

    print()

    print("TXT")

    print(result["txt"])

    print()

    print("JSON")

    print(result["json"])

else:

    print("Knowledge Invalid")