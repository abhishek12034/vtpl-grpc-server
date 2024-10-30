import os
import subprocess
import json
from pylatex import Document, Section, NoEscape, Package, Command
import json

# from pymongo import MongoClient
import cv2
import numpy as np


class GenerateReport:

    def __init__(self, config_file, db_descriptions):
        self.config_file = config_file
        self.db_descriptions = db_descriptions

    # def load_db_data():
    #     # Connect to MongoDB
    #     client = MongoClient("mongodb://localhost:27017/")
    #     db = client["report"]
    #     collection = db["report_db"]

    #     # Retrieve all documents from the collection
    #     documents = collection.find()

    #     # Convert documents to a list of dictionaries
    #     data = [doc for doc in documents]

    #     return data[0]

    def load_config(self):
        with open(self.config_file, "r") as f:
            config = json.load(f)
            # todo:we have to sort the process names based on process index. future development
            process_names = [process["process_name"] for process in config["Processes"]]
            print("Processes Name :", process_names)

        return process_names, config["Processes_meta"]["input_output_image_show_report"]

    def load_description_config(self):
        with open(self.db_descriptions, "r") as f:
            descriptions = json.load(f)

        return descriptions

    def generate_report(self, output_dir="report"):
        output_dir = os.path.abspath(output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Load configuration
        process_names, show_report = self.load_config()
        print("Show Report Flag :", show_report)

        geometry_options = {"margin": "2.54cm", "includeheadfoot": True}
        doc = Document(geometry_options=geometry_options)

        # Add packages with enhanced styling
        doc.packages.append(Package("graphicx"))
        doc.packages.append(Package("float"))
        doc.packages.append(Package("xcolor"))  # For custom colors
        doc.packages.append(Package("geometry"))
        doc.packages.append(Package("fancyhdr"))  # For headers and footers
        doc.packages.append(Package("titlesec"))  # For section formatting
        doc.packages.append(Package("enumitem"))  # For list customization
        doc.packages.append(Package("hyperref"))  # For clickable links and TOC

        # Enhanced document styling
        doc.preamble.append(NoEscape(r"\usepackage{xcolor}"))
        doc.preamble.append(NoEscape(r"\definecolor{titlecolor}{RGB}{0,51,102}"))
        doc.preamble.append(NoEscape(r"\definecolor{sectioncolor}{RGB}{0,51,102}"))

        # Custom section styling
        doc.preamble.append(
            NoEscape(
                r"\titleformat{\section}{\color{sectioncolor}\Large\bfseries}{\thesection}{1em}{}"
            )
        )

        # Headers and footers
        doc.preamble.append(NoEscape(r"\pagestyle{fancy}"))
        doc.preamble.append(
            NoEscape(r"\fancyhead[L]{Videonetics Technologies Pvt. Ltd.}")
        )
        doc.preamble.append(NoEscape(r"\fancyhead[R]{\thepage}"))
        # doc.preamble.append(NoEscape(r'\fancyfoot[C]{Image Adjustment Operations Report}'))

        # Document preamble
        doc.preamble.append(
            Command(
                "title",
                NoEscape(r"\textcolor{titlecolor}{Image Adjustment Operations Report}"),
            )
        )
        doc.preamble.append(Command("author", "Videonetics Technologies Pvt. Ltd."))
        doc.preamble.append(Command("date", NoEscape(r"\today")))

        # Create title page
        doc.append(NoEscape(r"\begin{titlepage}"))
        doc.append(NoEscape(r"\maketitle"))
        doc.append(NoEscape(r"\thispagestyle{empty}"))
        # Add logo at the bottom center
        doc.append(NoEscape(r"\vfill"))
        doc.append(NoEscape(r"\begin{center}"))
        # Use forward slashes in the path
        doc.append(
            NoEscape(
                r"\includegraphics[width=0.28\textwidth]{D:/Projects/Forensic/vtpl-grpc-server/report_generator/images/videonetics_logo.jpg}"
            )
        )
        doc.append(NoEscape(r"\\[0.2in]"))  # Separate line break command
        # doc.append(NoEscape(r'\Large{Videonetics}'))
        doc.append(NoEscape(r"\end{center}"))
        doc.append(NoEscape(r"\end{titlepage}"))

        # Add table of contents
        doc.append(NoEscape(r"\tableofcontents"))
        doc.append(NoEscape(r"\newpage"))

        def add_operation_section(title, description, input_img_path, output_img_path):
            with doc.create(Section(title)):
                doc.append("\n\n")
                # doc.append(NoEscape(r'\textcolor{black}{' + description + '}'))
                doc.append(NoEscape(r"\begin{justify}"))  # Start justification
                doc.append(NoEscape(r"\large " + description))  # Change size here
                doc.append(NoEscape(r"\end{justify}"))  # End justification
                doc.append("\n\n\n")

                if show_report == "True":
                    print("INSIDE IF Condition :")
                    doc.append(NoEscape(r"\vspace{2em}"))  # Add some vertical space
                    doc.append(NoEscape(r"\noindent\begin{minipage}{0.45\textwidth}"))
                    doc.append(NoEscape(r"\centering"))
                    doc.append(
                        NoEscape(
                            r"\includegraphics[width=\textwidth]{"
                            + input_img_path
                            + "}"
                        )
                    )
                    doc.append(NoEscape(r"\\Input"))  # Simple text label
                    doc.append(NoEscape(r"\end{minipage}"))
                    doc.append(
                        NoEscape(r"\hfill")
                    )  # Add horizontal space between images
                    doc.append(NoEscape(r"\begin{minipage}{0.45\textwidth}"))
                    doc.append(NoEscape(r"\centering"))
                    doc.append(
                        NoEscape(
                            r"\includegraphics[width=\textwidth]{"
                            + output_img_path
                            + "}"
                        )
                    )
                    doc.append(NoEscape(r"\\Output"))  # Simple text label
                    doc.append(NoEscape(r"\end{minipage}"))
                    doc.append(
                        NoEscape(r"\vspace{1em}")
                    )  # Add some vertical space after images

        # Define the operations2 dictionary
        operations2 = self.load_description_config()

        # Add each operation to the document
        for process_name in process_names:
            if process_name in operations2:
                operation = operations2[process_name]

                print(f"Processing: {process_name}")

                title = operation.get(process_name, operation["title"])
                description = operation.get(
                    f"{process_name}_description", operation["description"]
                )
                input_image_path = f'./channels_images/input_images/input_{process_name.lower().replace(" ", "_")}.jpg'
                output_image_path = f'./channels_images/output_images/output_{process_name.lower().replace(" ", "_")}.jpg'

                add_operation_section(
                    title, description, input_image_path, output_image_path
                )

        # Generate TEX file
        tex_filename = "color_channels_report.tex"
        tex_fullpath = os.path.join(output_dir, tex_filename)

        # Save the TEX file
        doc.generate_tex(os.path.splitext(tex_fullpath)[0])

        # Compile the TEX file to PDF
        # pdflatex_path = (
        #     r"C:\Users\katan\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe"
        # )
        try:
            for _ in range(2):
                process = subprocess.run(
                    [pdflatex, "-interaction=nonstopmode", tex_filename],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=output_dir,
                    text=True,
                )
                print(process.stdout)

            pdf_path = os.path.join(output_dir, "color_channels_report.pdf")
            if os.path.exists(pdf_path):
                print(f"PDF generated successfully: {pdf_path}")
            else:
                print(f"PDF file not found at expected location: {pdf_path}")

        except subprocess.CalledProcessError as e:
            print(f"Error compiling PDF: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Output directory: {output_dir}")
            print(f"TEX file exists: {os.path.exists(tex_fullpath)}")


if __name__ == "__main__":
    report_obj = GenerateReport(
        config_file="./config.json", db_descriptions="./new_descriptions.json"
    )
    report_obj.generate_report()
