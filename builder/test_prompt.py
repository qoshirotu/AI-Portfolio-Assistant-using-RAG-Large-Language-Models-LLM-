from builder.prompt import PromptBuilder

builder = PromptBuilder()

text = """

IT Consultant Internship

Implemented Zoho CRM
Implemented Zoho Creator
Implemented Zoho Analytics

"""

prompt = builder.build(text)

print(prompt)