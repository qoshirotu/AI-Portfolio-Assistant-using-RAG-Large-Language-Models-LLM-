from builder.llm_builder import KnowledgeBuilder
from builder.parser import KnowledgeParser
from builder.writer import KnowledgeWriter


class KnowledgePipeline:

    def __init__(self):

        self.builder = KnowledgeBuilder()
        self.parser = KnowledgeParser()
        self.writer = KnowledgeWriter()

    # ==========================================================
    # Build satu knowledge item
    # ==========================================================

    def build(
        self,
        category: str,
        title: str,
        content: str,
        organization: str = "",
        date: str = ""
    ):

        print("=" * 70)
        print(f"{category.upper()} | {title}")
        print("=" * 70)

        knowledge = self.builder.generate(

            category=category,
            title=title,
            content=content,
            organization=organization,
            date=date

        )

        parsed = self.parser.parse(

            knowledge

        )

        if not self.parser.validate(parsed):

            raise Exception(

                "Knowledge validation failed."

            )

        result = self.writer.save(

            parsed

        )

        print("SUCCESS")
        print(result["txt"])
        print(result["json"])
        print()

        return result

    # ==========================================================
    # Build seluruh section hasil extractor
    # ==========================================================

    def build_sections(self, sections):

        print()
        print("=" * 70)
        print("BUILDING KNOWLEDGE")
        print("=" * 70)

        success = 0
        failed = 0

        # ----------------------------
        # Profile
        # ----------------------------

        if sections.get("profile"):

            try:

                self.build(

                    category="profile",

                    title="About",

                    content=sections["profile"]

                )

                success += 1

            except Exception as e:

                failed += 1
                print(e)

        # ----------------------------
        # Education
        # ----------------------------

        if sections.get("education"):

            try:

                self.build(

                    category="education",

                    title="Education",

                    content=sections["education"]

                )

                success += 1

            except Exception as e:

                failed += 1
                print(e)

        # ----------------------------
        # Skills
        # ----------------------------

        if sections.get("skills"):

            try:

                self.build(

                    category="skills",

                    title="Skills",

                    content=sections["skills"]

                )

                success += 1

            except Exception as e:

                failed += 1
                print(e)

        # ----------------------------
        # Certifications
        # ----------------------------

        if sections.get("certifications"):

            try:

                self.build(

                    category="certifications",

                    title="Certifications",

                    content=sections["certifications"]

                )

                success += 1

            except Exception as e:

                failed += 1
                print(e)

        # ----------------------------
        # Contact
        # ----------------------------

        if sections.get("contact"):

            try:

                self.build(

                    category="contact",

                    title="Contact Information",

                    content=sections["contact"]

                )

                success += 1

            except Exception as e:

                failed += 1
                print(e)

        # ----------------------------
        # Experience
        # ----------------------------

        for exp in sections.get("experience", []):

            try:

                self.build(

                    category="experience",

                    title=exp.get("title", "Experience"),

                    content=exp.get("content", ""),

                    organization=exp.get(

                        "organization",

                        ""

                    ),

                    date=exp.get(

                        "date",

                        ""

                    )

                )

                success += 1

            except Exception as e:

                failed += 1

                print(e)

        # ----------------------------
        # Projects
        # ----------------------------

        for project in sections.get("projects", []):

            try:

                self.build(

                    category="projects",

                    title=project.get(

                        "title",

                        "Project"

                    ),

                    content=project.get(

                        "content",

                        ""

                    )

                )

                success += 1

            except Exception as e:

                failed += 1

                print(e)

        print()
        print("=" * 70)
        print("BUILD FINISHED")
        print("=" * 70)
        print(f"Success : {success}")
        print(f"Failed  : {failed}")
        print("=" * 70)

        return {

            "success": success,

            "failed": failed

        }