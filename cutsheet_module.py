from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from box_module import eosBox
from io import BytesIO


class Stamp:
    FORMATS = ["%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"]

    def __init__(self, stamp_data: dict):

        print(f'stamp_data: {stamp_data}')

        self.buffer = BytesIO()
        self.folder_id = stamp_data["folderID"]
        self.project_name = stamp_data["projectName"]
        self.project_number = stamp_data["projectNumber"]
        self.prepared_by = stamp_data["preparedBy"]
        self.prepared_for = stamp_data["preparedFor"]
        self.is_revision = stamp_data["isRevision"]
        self.revision_number = stamp_data["revisionNumber"]
        self.date = stamp_data["date"]
        self.note = stamp_data["note"]

        self.page_width, self.page_height = A4
        self.pdf_canvas = canvas.Canvas(self.buffer)

        pdfmetrics.registerFont(TTFont('Karla-Medium', 'static/karla-medium.ttf'))
        self.pdf_canvas.setFont('Karla-Medium', 12)

    def _draw_box(self, origin: tuple, size: tuple, color):
        self.pdf_canvas.setFillColor(color)
        self.pdf_canvas.rect(origin[0], origin[1], size[0], size[1], fill=True)

    def _get_logo(self):
        if self.prepared_by == 0:
            return "eos-logo.png"
        elif self.prepared_by == 1:
            return "abn-logo.png"

    def _place_logo(self):
        logo = self._get_logo()
        logo_img = ImageReader(logo)
        self.pdf_canvas.drawImage(logo_img, self.page_width - 100, 10, 80, 80)

    def apply_stamp_to_img(self, device_img, device_type: str, page_num: int, page_total: int):
        self._draw_box((0, 0), (self.page_width, self.page_height * 0.15), 'black')
        self._draw_box((5, 30), (self.page_width - 10, (self.page_height * 0.15) - 35), 'white')

        self.pdf_canvas.setFillColor('grey')

        self.pdf_canvas.drawString(15, 110, 'TYPE')
        self.pdf_canvas.drawString(200, 100, 'PROJECT NAME')
        self.pdf_canvas.drawString(200, 80, 'JOB CODE')
        self.pdf_canvas.drawString(200, 60, 'PREPARED FOR')
        self.pdf_canvas.drawString(200, 40, 'PROJECT PHASE')

        self.pdf_canvas.setFillColor('black')

        self.pdf_canvas.drawString(300, 100, str(self.project_name).upper())
        self.pdf_canvas.drawString(300, 80, str(self.project_number).upper())
        self.pdf_canvas.drawString(300, 60, str(self.prepared_for).upper())
        self.pdf_canvas.drawString(300, 40, str(self.note).upper())

        # Type

        self.pdf_canvas.setFillColor('white')
        self.pdf_canvas.setFont('Karla-Medium', 10)

        self.pdf_canvas.drawString(
            15,
            15,
            f"{['ISSUED DATE: ', 'REVISED DATE: '][int(self.is_revision)]}{self.date}")

        self.pdf_canvas.drawString(500, 15, f"PAGE {page_num:02} OF {page_total:02}")

        self.pdf_canvas.showPage()

    def save_pdf(self):
        self.pdf_canvas.save()
        pdf_bytes = self.buffer.getvalue()
        self.buffer.close()
        return pdf_bytes


if __name__ == '__main__':
    CLIENT_ID = 'ek7onbev0qocf7rtfuov0h8xo17picca'
    CLIENT_SECRET = 'IXlVDtc03kOdwskeVfXkbz2Urj6jLnR3'

    box = eosBox(CLIENT_ID, CLIENT_SECRET, 'http://localhost:8000/api/auth')
    print(f'url: {box.auth_url}')
    code = input('authorization code: ')
    box.authenticate_client(code)

    packet = "output.pdf"
    stamp_data = {
        "folderID": "240776517305",
        "projectName": "Project X",
        "projectNumber": "12345",
        "preparedBy": "John Doe",
        "preparedFor": "Jane Smith",
        "client": "ACME Corp",
        "isRevision": True,
        "revisionNumber": 2,
        "date": "DEC / 15 / 2023",
        "jobPhase": "Phase 1",
    }

    # get items in folder
    items = box.get_files_in_folder(stamp_data['folderId'])
    pdfs = box.get_pdfs_in_folder(stamp_data['folderId'])
    print(f'{len(items)} items')
    print(f'{len(pdfs)} pdfs')

    stamp = Stamp(stamp_data)
    img = "image.jpg"
    stamp.apply_stamp_to_img(img, 'EG01', 1, 2)
    stamp.pdf_canvas.save()
