'''
* Poll the database for "transmission" entries in the queue
* When there are some entries:
    * check for if there is a reference source list
    * if there is not:
        * find the reference image
        * extract the source catalogue
    * find the files on disk
    * extract the sources
'''


class Job(object):

    def __init__(self, filename):
        self.filename = filename

    def __eq__(self, other):
        return self.filename == other.filename


def fetch_transmission_jobs():
    filename = '/ngts/das03/action106267_observeField/IMAGE80520150920234004.fits'
    return iter([Job(filename)])
