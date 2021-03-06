#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Note: this is a copy of a tool from pdfminer. May be modified in the future.
import sys
from tempfile import TemporaryFile

from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice#, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.layout import LAParams

#from pdfminer.pdftypes import resolve1

def remove_ligatures(text):
    # Replaces ligatures (fancy symbols combining several letters) with letter combinations.
    text = text.replace("ﬃ", "ffi")
    text = text.replace("ﬁ", "fi")
    text = text.replace("ﬀ", "ff")
    text = text.replace("ﬂ", "fl")
    return text

def get_page_text(interpreter, page, tmp, rotation = 0):
    # Extract text from a page with given rotation. These variables are required and must be setup in parent function:
    # interpreter - interpreter used by PDFMiner.
    # page - page object.
    # tmp - temporary file use to get processed text. Stack Overflow advices to create a new tmp file each time, but it must be specified when creating PDFMiner device object, so i'm not sure if that's possible.
    page.rotate = (page.rotate+rotation) % 360
    interpreter.process_page(page)
    tmp.seek(0)
    text = remove_ligatures(tmp.read())
#    newlines = []
#    for l in lines:
#        newlines.append(remove_ligatures(l))
    tmp.seek(0)
    tmp.truncate()
    return text

def mine_text(infname, page_numbers = False, outtype = "text", rotated_pages = [], folder = False):
    # Mine text from a PDF files. Find rotated pages if txt, rotate pages according to respective variable if xml.
#    inf = open(infname, "rb")
    with open(infname, "rb") as inf: # By using "with" we ensure that file gets closed if something goes wrong in this block.
    
        rsrcmngr = PDFResourceManager()

        tmp = TemporaryFile(mode="w+")
        laparams = LAParams()
    #    laparams.detect_vertical = True
    #    laparams.line_margin = 0.8
    #    laparams.word_margin = 0.1
    #    print laparams
    #    laparams.boxes_flow = -1.0

        extension = False
        if outtype == "text":
            device = TextConverter(rsrcmngr, tmp, codec='utf-8', laparams = laparams)
            extension = "txt"
            rotated_pages = []
        elif outtype == "xml":
            device = XMLConverter(rsrcmngr, tmp, codec='utf-8', laparams = laparams)
            extension = "xml"
        elif outtype == "html":
            device = HTMLConverter(rsrcmngr, tmp, codec='utf-8', laparams = laparams)
        interpreter = PDFPageInterpreter(rsrcmngr, device)

        n = 1
#        pages = {}
        for page in PDFPage.get_pages(inf):
    #        print n
            if not page_numbers or n in page_numbers:
                if outtype == "xml" and n in rotated_pages:
                    rotation = 90
                else:
                    rotation = 0
                text = get_page_text(interpreter, page, tmp, rotation)
                if outtype == "text":
                    single = 0
                    normal = 0
                    lines = text.split("\n")
                    for l in lines:
                        if not l.isspace():
                            l = l.strip()
                            if len(l) == 1:
                                single += 1
                            normal += 1
                    coef = float(single) / normal
    #                print "Page %d: %d/%d = %f lines contain a single character" % (n, single, normal, coef)
                    if coef > 0.6:
                        rotated_pages.append(n)
    #                    print "Page seems to be rotated"
                        text = get_page_text(interpreter, page, tmp, 90)
#                pages[n] = text
                if folder and extension:
                    with open(folder + "/%d.%s"%(n, extension), "w") as outf:
                        outf.write(text)
    #            outf.writelines(lines)            
            n += 1
#    inf.close()
    device.close()
    tmp.close()
    return [n - 1, rotated_pages]

if __name__ == "__main__":
    [pages, rotated_pages] = mine_text("C:/Work/papers_analysis/ATL-COM-PHYS-2014-1357.pdf", [201], "xml")
    for p in pages:
        print pages[p]
    
##    f = open("C:/Work/papers_analysis/ATL-COM-PHYS-2014-1430.pdf", "rb")
##
##    rsrcmngr = PDFResourceManager()
##
##    tmp = TemporaryFile(mode="w+")
##    laparams = LAParams()
##    device = TextConverter(rsrcmngr, tmp, codec='utf-8', laparams = laparams)
##    interpreter = PDFPageInterpreter(rsrcmngr, device)
##
##    n = 1
##    for page in PDFPage.get_pages(f):
##        lines = get_page_lines(interpreter, page, tmp)
##        single = 0
##        normal = 0
##        for l in lines:
##            if not l.isspace():
##                l = l.strip()
##                if len(l) == 1:
##                    single += 1
##                normal += 1
##        coef = float(single) / normal
##        print "Page %d: %d/%d = %f lines contain a single character" % (n, single, normal, coef)
##        if coef > 0.9:
##            print "Page seems to be rotated"
##            lines = get_page_lines(interpreter, page, tmp, 90)
##            print lines
##            
##        n += 1
##        if n == 10:
##            break
##    print n
##    f.close()
##    device.close()
##    tmp.close()
