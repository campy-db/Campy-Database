"""
 BatchUploader.py
"""
import pandas as pd
from .shared.clean_triple_writers import *

class BatchUploader(object):
    def __init__(self, fname):
        dir_ = r"/home/student/Campy/CampyDatabase/WebApp/app/uploads/{}".format(fname)
        self.filename = fname
        self.data_frame = pd.read_csv(dir_)
        self.max_rows = len(self.data_frame.index)
        """
        for row in range(self.max_rows):
            df_row = self.data_frame.loc[row]
            print df_row["Person"]
        """
