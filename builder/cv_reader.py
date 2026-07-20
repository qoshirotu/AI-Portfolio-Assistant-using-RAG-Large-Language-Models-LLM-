from pathlib import Path
import fitz


class CVReader:

    def read(self, file_path):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(file_path)

        suffix = file_path.suffix.lower()

        if suffix == ".pdf":

            return self.read_pdf(file_path)

        elif suffix == ".txt":

            return self.read_txt(file_path)

        else:

            raise Exception(
                f"Unsupported file type : {suffix}"
            )

    # ============================================

    def read_pdf(self, file_path):

        doc = fitz.open(file_path)

        pages = []

        for page in doc:

            pages.append(

                page.get_text()

            )

        doc.close()

        return "\n".join(pages)

    # ============================================

    def read_txt(self, file_path):

        with open(

            file_path,

            "r",

            encoding="utf-8"

        ) as f:

            return f.read()