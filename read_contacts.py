from string import Template

#Import contacts from file function

def get_contacts(filename):
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

#Reading the template message function

def read_template(filename):
    with open(filename, 'r', encoding='utf8') as template_file:
        template_file_content = template_file.read()

    return Template(template_file_content)

def get_filenames(names):
    f = []
    for n in range(1,len(names)+1):
        f.append(str(n))
    return f
