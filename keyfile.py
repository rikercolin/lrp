from genericpath import isfile
import os
import datetime
import uuid
import json
from urllib.request import urlopen
from urllib.error import HTTPError


class Document:
    def __init__(self, doc_url, doc_id, answers, data_folder):
        self.doc_url = doc_url
        self.doc_id = doc_id
        self.answers = answers
        self.data_folder = data_folder

    def to_tuple(self):
        return (self.doc_url, str(self.doc_id), self.answers)

    def download(self):
        try:
            with urlopen(self.doc_url) as webpage:
                doc_text = webpage.read().decode()
                doc_filename = '{}/{}.txt'.format(
                    self.data_folder, self.doc_id)
                print("Downloading: {}".format(self.doc_id))
                with open(doc_filename, 'w', encoding='utf-8') as f:
                    f.write(doc_text)
                    f.close()
        except UnicodeEncodeError:
            print('Error 1')
        except HTTPError:
            print('Error 2')

    def read(self):
        uri = '{}/{}.txt'.format(self.data_folder, self.doc_id)
        with open(uri, 'r', encoding='utf-8') as f:
            text = f.read()
            f.close
            return text


class KeyFile:
    def __init__(self, category, data_folder, documents):
        self.documents = documents
        self.category = category
        self.data_folder = data_folder

    def data_folder_integratity(self):
        print("[Validating Keyfile]")
        redownload = []
        if os.path.exists(self.data_folder):
            for document in self.documents:
                p = '{}/{}.txt'.format(self.data_folder, document.doc_id)
                if not os.path.exists(p):
                    redownload.append(document)
                #else:
                    #print(p + " Found!")

        else:
            os.makedirs(self.data_folder)
            redownload = self.documents

        for document in redownload:
            document.download()


class KeyFileEncoder(json.JSONEncoder):
    ''' Default() is the implemntation for the json encoding of Key files and
    the underlying datatypes.
    '''

    def default(self, obj):
        if isinstance(obj, KeyFile):
            docs = []
            for document in obj.documents:
                docs.append(document.to_tuple())

            return (obj.category, obj.data_folder, docs)


''' Read() takes an already existing keyfile from disk and reads it into
memory. While also checking the integrity of the datafolder that belongs to it.'''


def read(key_filename):
    print("[Reading Keyfile]")
    with open(key_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
        documents = []
        for document in data[2]:
            documents.append(
                Document(document[0], document[1], document[2], data[1]))

        return KeyFile(data[0], data[1], documents)


''' Build() creates a new keyfile from the source file based on the provided
category. It writes it into a json file and returns the new keyfile.'''


def build(category, source):
    print("[Building Keyfile]")
    date = datetime.datetime.now().date()
    filename = "{}_{}.json".format(category, date)
    documents = []

    if os.path.exists(filename):
        print("Key file exists")
        return

    if os.path.isdir(source):
        for file in os.listdir(source):
            path = '{}/{}'.format(source, file)
            documents.extend(read_labelbox_file(path, category))

    elif os.path.isfile(source):
        documents = read_labelbox_file(source, category)

    key_file = KeyFile(category, str(category) + str(date), documents)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json.dumps(key_file, cls=KeyFileEncoder))
        return f


def read_labelbox_file(file, category):
    with open(file, 'r', encoding='utf-8') as f:
        labelbox_file = json.load(f)
        documents = []
        for document in labelbox_file:
            doc_url = document['Labeled Data']
            answers = []

            for answer in document['Label']['objects']:
                if answer['title'] == category:
                    answers.append(answer['data'])

            documents.append(Document(doc_url, uuid.uuid4(), answers, None))
        return documents
