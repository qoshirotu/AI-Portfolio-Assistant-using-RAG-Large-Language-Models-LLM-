from pprint import pprint

from builder.cv_reader import CVReader

from builder.section_extractor import SectionExtractor


reader = CVReader()

extractor = SectionExtractor()

resume = reader.read(

    "uploads/cv.pdf"

)

sections = extractor.extract(

    resume

)

pprint(sections)