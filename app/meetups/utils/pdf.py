from fpdf import FPDF


class TablePDF(FPDF):
    def __init__(self, tittles, data_list, file_path, orientation, format,
                 font, size):
        super().__init__(orientation=orientation, format=format, unit='mm')
        self.font = font
        self.size = size
        self.tittles = tittles
        self.data_list = data_list
        self.file_path = file_path
        self.set_font(font, size=size)
        self.row_height = self.font_size * 1.1
        self.col_widths_list = [8, 40, 34, 66, 30, 30, 30, 39]

    def header(self):
        """ Heather. Determines the rendering of the table header with data
        on each page. """
        self.set_font(style="B", family=self.font, size=self.size)
        for i, tittle in enumerate(self.tittles):
            self.cell(w=self.col_widths_list[i], h=self.row_height,
                      txt=str(tittle), border=1, align="C")
        self.ln(self.row_height)
        self.set_font(style='', family=self.font)

    def footer(self):
        """ Footer. Specifies the display of the page number. """
        self.set_y(-15)
        self.cell(0, 10, str(self.page_no()), 0, 0, 'R')

    def calculate_line_height_coefficient(self, row):
        """ Method for calculating the line height factor. Specifies the
        maximum number of line breaks for a cell within a single line."""
        split_count_list = []
        for i, datum in enumerate(row):
            split_lines_list = self.multi_cell(
                txt=str(datum),
                split_only=True,
                h=self.row_height,
                w=self.col_widths_list[i],
                max_line_height=self.font_size
            )
            split_count_list.append(len(split_lines_list))
        return max(split_count_list)

    def draw_table(self):
        """ Method for creating a PDF file containing a table with data.
         Row heights scale automatically. """
        for row in self.data_list:
            height_coefficient = self.calculate_line_height_coefficient(row)
            line_height = self.row_height * height_coefficient
            for i, datum in enumerate(row):
                self.multi_cell(
                    border=1,
                    new_y="TOP",
                    new_x="RIGHT",
                    h=line_height,
                    txt=str(datum),
                    w=self.col_widths_list[i],
                    max_line_height=self.font_size
                )
            self.ln(line_height)
        self.output(self.file_path, 'F')
