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


class student_information:

    def __int__(self):
        self.pdf = None

    def create_pdf(self):
        self.pdf = FPDF()

    def set_font(self, font_style, font_size):
        self.pdf.add_page()
        self.pdf.set_font(font_style, size=font_size)

    def write_html(self, details, align):
        self.pdf.cell(200, 10, txt=details, ln=1, align=align)

        data = models.Student.objects.all()
        pdf = student_information()
        # pdf.set_font_size(16)
        # pdf.add_page()
        #pdf.write_html(details, align)


    def generate_pdf(self, name):
        self.pdf.output(f'{name}.pdf')



        #pdf.generate_pdf('table_html.pdf')
