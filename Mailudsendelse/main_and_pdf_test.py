# -*- coding: utf-8 -*-

import smtplib
import os
import tika
import sys


#update to java8
#pip install install-jdk
#pip install tika
from tika import parser
from os.path import basename
# Remember to install "PyPDF2"
from PyPDF2 import PdfReader, PdfWriter

from read_contacts import get_contacts
from read_contacts import read_template
from read_contacts import get_filenames

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Manual:
#   1. Indskriv i "contacts_real.txt" navn og email i rækkefølge svarende til 
#      den rækkefølge der findes på economics for konti
#   2. Hent pdf af kontoplaner for alle alumnerne fra economics
#   3. Kør kommandoen fra pdf_splitter.text i terminalen i den korrekte mappe. 
#      Alle 61 pdf sider er nu individuelle filer hhv 1.pdf, 2.pdf
#   4. Kør dette script. Alle e-mails er nu sendt

#%% PDF Splitter:

# Importing the PDF and get data:
pdf_file = open('1182586 - G. A. Hagemanns Kollegium_filtered.pdf', 'rb')  # Open PDF
pdf_reader = PdfReader(pdf_file)    # Read PDF
pageNumbers = len(pdf_reader.pages)  # Get page numbers

# Loop over page numbers:
for i in range(pageNumbers):
    pdf_writer = PdfWriter() 
    pdf_writer.add_page(pdf_reader.pages[i])
    split_motive = open(str(i + 1) + '.pdf', 'wb')
    pdf_writer.write(split_motive)
    split_motive.close()

# Close PDF file:
pdf_file.close()

#%% Send mails
    
def main():
    # Read info:
    names,emails = get_contacts('contacts.txt')     # Read contacts
    # names,emails = get_contacts('contacts.txt')   # Read contacts
    message_template = read_template('message.txt') # Read message template
    file_names       = get_filenames(names)

    # Set up SMTP server
    s               = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    login,password  = 'RegnskabGAHK@gmail.com' , 'xtioqqoypowwdsyd'     # Login and password
    s.login(login,password)                                             # Use login and password

    # Change the file names from numbers to the name of the person the bill belongs to
    for filename in file_names:
        k = int(filename) - 1                               # Index
        raw_text    = parser.from_file(filename + ".pdf")   # PDF text
        raw_text    = (raw_text['content'])
        Split_Name  = names[k].split('-')                   # Split name string
        First_Name  = Split_Name[0]                         # Define first name
        
        # Check with 'contacts':
        if First_Name not in raw_text:
            print("Fejl ved række", k,",", First_Name)
            sys.exit("Fejl i contacts.txt - matcher ikke med PDFerne. Se detaljer herover (p.s. du skylder en bajer)") 
        os.rename(filename + ".pdf", names[k] + ".pdf")

    # For each contact send email
    for name, email in zip(names,emails):
        msg     = MIMEMultipart()                                       # Create message
        message = message_template.substitute(PERSON_NAME=name.title()) # Add person name in the template
        print(message)                                                  # Print message to verify

        # Setup email parameters (from,to,subject)
        # msg['From']='RegnskabGAHK@gmail.com'
        msg['From'] = 'Regnskabsgruppen'    # Sender
        msg['To'] = email                   # E-mail address of "alumne"
        msg['Subject'] = 'Alumneregning'    # Mail Subject

        # Add message-text-body to the constructed message
        msg.attach(MIMEText(message, 'plain'))

        # Construct the file attachment and
        with open(name+".pdf", 'rb') as regning_pdf:
            part1 = MIMEApplication( regning_pdf.read() , Name=basename(name+".pdf")
            )
        part1['Content-Disposition'] = 'attachment; filename="%s"' % basename(name+".pdf")
        msg.attach(part1)

        with open('TV-Redaktionen.pdf', 'rb') as skabelon:
            part2 = MIMEApplication( skabelon.read(), Name=basename('TV-Redaktionen.pdf')
            )
            part2['Content-Disposition'] = 'attachment; filename="%s"' % basename('TV-Redaktionen.pdf')
        msg.attach(part2)

        # Send the email
        s.send_message(msg)

        # Delete the email
        del msg

    # Close connection
    s.quit()

# Run the script using this command
if __name__ == '__main__':
    main()

#%% Displaying end note:
print("\nScript is finished")
