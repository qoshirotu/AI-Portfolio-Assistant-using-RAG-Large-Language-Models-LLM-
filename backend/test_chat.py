from app.chat_service import chat

question = "who is qoshi?"

answer = chat(question)

print("=" * 80)
print("PERTANYAAN")
print(question)

print("\n")

print("JAWABAN")
print(answer)

