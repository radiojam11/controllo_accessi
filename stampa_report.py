# TecnoGeppetto aka Valerio Tognozzi
# 
# Stampa Report Controllo Accessi#
# Questo programma consente di stampare il file di log "log_ufficiale.log" creato dal programma "accessi.py"
# su foglio A4 con carta intestata azinedale.
# Il programma crea un file "report.pdf" che contiene le pagine di report 24 righe per pagina,
#   e salva il file pdf chiamato "report_accessi.pdf" nella direttory corrente inserendo la carta intestata dellì'azienda
#   #

from reportlab.pdfgen import canvas
from datetime import datetime
import PyPDF2 

mio_pdf = canvas.Canvas('report.pdf')
mio_pdf.setFont("Helvetica", 10)
# —– imposta le dimensioni del modello
mio_pdf.setPageSize((595.2755905511812, 841.8897637795277))                    # —– scrive quello che voglio dove mi pare
f = open("log_ufficiale.log", "r")
righe = f.readlines()
coord=680
righe_ultima_p = 0
if len(righe)%24 == 0:
    pagine = int(len(righe)/24)
else:
    pagine =int(len(righe)/24)
    righe_ultima_p = len(righe) - pagine*24

for i in range(pagine):
    mio_pdf.setFont("Helvetica", 10)
    for q in range(1,25):
        print(i)
        print(q)
        print(i*24+q)
        riga = righe[(i*24)+q]
        
        mio_pdf.drawString(65,coord,riga[:-1])
        coord = coord - 20
    coord = 680
    mio_pdf.showPage()
if righe_ultima_p > 0:
    mio_pdf.setFont("Helvetica", 10)
    for i in range(righe_ultima_p):
        riga = righe[pagine*24 + i]
        print(riga)
        print(pagine*24 + i)
        mio_pdf.drawString(65,coord,riga[:-1])
        coord = coord - 20
    mio_pdf.showPage()
        
#mio_pdf.drawString(65,660,str(datetime.today()))
# —– genera e salva il pdf

mio_pdf.save()
pdf_file = "report.pdf"
watermark = "modello.pdf"
merged_file = "report_accessi.pdf"
input_file = open(pdf_file,'rb')
input_pdf = PyPDF2.PdfFileReader(pdf_file)
watermark_file = open(watermark,'rb')
watermark_pdf = PyPDF2.PdfFileReader(watermark_file)
output = PyPDF2.PdfFileWriter()
for page in range(input_pdf.getNumPages()):
    pdf_page = input_pdf.getPage(page)
    watermark_page = watermark_pdf.getPage(0)
    pdf_page.mergePage(watermark_page)
    output.addPage(pdf_page)
merged_file = open(merged_file,'wb')
output.write(merged_file)
merged_file.close()
watermark_file.close()
input_file.close()
