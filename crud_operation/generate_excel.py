import xlsxwriter


class Writer:
    def __int__(self):
        self.workbook = None
        self.worksheet = None

    def create_writer(self, name):
        self.workbook = xlsxwriter.Workbook(name)
        self.worksheet = self.workbook.add_worksheet()

    def write_excel(self, row, col, stu_data):
        self.worksheet.write(row, col, stu_data)

    def close_excel(self):
        self.workbook.close()
