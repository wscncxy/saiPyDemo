import csv

class CsvUtils:
    def __init__(self,filePath):
        self.filePath=filePath

    def read(self):
        with open(self.filePath, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)