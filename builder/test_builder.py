from builder.llm_builder import KnowledgeBuilder

builder = KnowledgeBuilder()

text = """

IT Consultant Internship

Implemented Zoho CRM

Implemented Zoho Creator

Implemented Zoho Analytics

Created dashboard

Supported ERP implementation

"""

knowledge = builder.generate(

    text

)

print()

print("="*60)

print(knowledge)