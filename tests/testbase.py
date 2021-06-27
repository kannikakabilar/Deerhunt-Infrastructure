import os
import re


EMAIL_URL_REGEX = re.compile(r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}| \
                                www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?! \
                                www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})')

def filter_link(data):
    return re.sub(EMAIL_URL_REGEX, '<CODE>', data)

def read_link(data):
    return re.search(EMAIL_URL_REGEX, data).group(1)

class BaseTester:
    '''
    Parent class for all diff based testing.
    '''

    def __init__(self):
        self.basedir = os.getcwd()
        self.outdir = f'{self.basedir}/out'
        self.refdir = f'{self.basedir}/ref'
        self.vardir = f'{self.basedir}/var'

    def __enter__(self):
        self.create_dirs()
        return self
        

    def __exit__(self, type, value, tb):
        pass


    def create_dirs(self) -> None:
        '''
        Creates out/ directory if doesn't exist.
        '''
        if not os.path.isdir(self.outdir):
            os.mkdir(self.outdir)
        if not os.path.isdir(self.vardir):
            os.mkdir(self.vardir)

    def save_var(self, new_var: str, data):
        with open(f'{self.vardir}/vars.txt', 'w+') as file:
            file.write(f'{new_var}={data}\n')

    def get_var(self, var: str):
        with open(f'{self.vardir}/vars.txt', 'r') as file:
            lines = file.readlines()
            for i in lines:
                temp = i.split('=')
                if var == temp[0]:
                    return temp[1]


    def run(self, testname, result) -> None:
        '''
        Writes test result to outfile
        '''
        with open('{}/{}.out'.format(self.outdir, testname), 'w') as f:
            f.write(result)
        self.diff_check(testname)
        

    def diff_check(self, testname) -> None:
        '''
        Checks if received test output matches refence file output.
        '''
        with open('{}/{}.ref'.format(self.refdir, testname), 'r') as ref, \
            open('{}/{}.out'.format(self.outdir, testname), 'r') as out:
            ref_text = ref.read()
            out_text = out.read()
            if (ref_text == out_text):
                assert True
                os.remove('{}/{}.out'.format(self.outdir, testname))
            else:
                assert ref_text == out_text
