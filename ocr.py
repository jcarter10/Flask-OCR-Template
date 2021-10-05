import os
import cv2
import matplotlib.pyplot as plt
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

# main
def startProcess(pdf_path):
    # vars
    poppler_path = os.getcwd() + "/poppler/poppler-0.68.0/bin"
    pdf_path = '/' + pdf_path
    temp_path = '/temp'
    result_string = ''

    # convert the pdf file to image object
    pages = convert_from_path(os.getcwd() + pdf_path, poppler_path=poppler_path)
    
    # save each pdf page as a JPG image
    i = 1
    for page in pages: 
        # create name + path 
        page_path = os.getcwd() + temp_path + '/' + os.path.basename(pdf_path).replace('.pdf', '') + "_Page_" + str(i) + ".jpg"

        # save image object (page) to output folder temporarioly
        page.save(page_path , "JPEG")

        # start OCR to get result string for current pdf page
        result_string += performOCR(page_path)

        # remove image once OCR is done
        os.remove(page_path)

        i += 1  

    # extract job titles from the pdfs string
    job_titles = extractJobTitles(result_string)

    return job_titles

# performs OCR using Tesseract from an image path
def performOCR(image_path):

    # load image from path
    image = cv2.imread(image_path)

    # convert the image to black and white for better OCR
    ret, thresh1 = cv2.threshold(image, 120, 255, cv2.THRESH_BINARY)

    # converts image to string form
    pdf_string = str(pytesseract.image_to_string(thresh1, config='--psm 6'))

    return pdf_string


# extracts job titles from a given string based off of a list of job titles
def extractJobTitles(pdf_text):
    
    # vars
    file_list = ['job_titles.txt']
    job_list = []
    results = []

    # read each job title from each file in list
    for current_file in file_list:

        # validate file
        if os.path.splitext(current_file)[1] not in ['.txt', '.lst']: 
            return 'Error: The file \'' + current_file + '\' is broken or wrong extension.'
        if os.path.isfile(current_file) == False:
            return 'Error: The file ' + current_file + ' does not exist.'

        # open file for reading
        with open(current_file, 'r') as file:
            # parse each line
            for line in file:
                # removes NOC from list (special case)
                if ':NOC' in line:
                    job_list.append(line[0: line.index(':NOC')])
                # basic case
                else:
                    job_list.append(line)
    
    # make list lowercase
    for i in range(len(job_list)):
        job_list[i] = job_list[i].lower()

    # remove duplicates
    job_list = list(dict.fromkeys(job_list))

    # lowercasing pdf_text for comparisons (so we don't have to do it each iteration)
    pdf_text = pdf_text.lower()

    # compare each job in job_list to pdf text to find matches
    for job in job_list:
        if job.lower() in pdf_text:
            results.append(job)

    # clean results before return
    results =  [job.replace('\n', '') for job in results]

    return results
    

# incase user is calling script from command prompt, must manually enter pdf path
if __name__ == '__main__':
    print('Enter a pdf path (absolute path): ')
    pdf_path = input()
    startProcess(pdf_path)
































# # function for region marking, reference --> https://gist.github.com/akash-ch2812/d42acf86e4d6562819cf4cd37d1195e7#file-marking_roi-py
# def mark_region(image_path):
    
#     image = cv2.imread(image_path)

#     # define threshold of regions to ignore
#     THRESHOLD_REGION_IGNORE = 40

#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     blur = cv2.GaussianBlur(gray, (9,9), 0)
#     thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)

#     # Dilate to combine adjacent text contours
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
#     dilate = cv2.dilate(thresh, kernel, iterations=4)

#     # Find contours, highlight text areas, and extract ROIs
#     cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     cnts = cnts[0] if len(cnts) == 2 else cnts[1]

#     line_items_coordinates = []
#     for c in cnts:
#         area = cv2.contourArea(c)
#         x, y, w, h = cv2.boundingRect(c)
        
#         if w < THRESHOLD_REGION_IGNORE or h < THRESHOLD_REGION_IGNORE:
#             continue
        
#         image = cv2.rectangle(image, (x,y), (x+w, y+h), color=(255,0,255), thickness=3)
#         line_items_coordinates.append([(x,y), (x+w, y+h)])

#     return image, line_items_coordinates
