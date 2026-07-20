from builder.cv_reader import CVReader

reader = CVReader()

text = reader.read(

    "uploads/cv.pdf"

)

print(text)