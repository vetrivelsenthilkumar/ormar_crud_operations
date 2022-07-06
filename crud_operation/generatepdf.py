from fpdf import FPDF, HTMLMixin
import models


class student_details:
    def __int__(self):
        self.pdf = None

    def create_pdf(self):
        self.pdf = FPDF()

    def set_font(self, font_style, font_size):
        self.pdf.add_page()
        self.pdf.set_font(font_style, size=font_size)

    def write_pdf(self, details, align):
        self.pdf.cell(200, 10, txt=details, ln=1, align=align)

    def generate_pdf(self, name):
        self.pdf.output(f'{name}.pdf')
