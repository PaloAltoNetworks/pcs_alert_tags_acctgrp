# -*- coding: utf-8 -*-
import csv

class CsvWriters(object):
    @staticmethod
    def write(output):
        filename = "output_IAM.csv"
        with open(filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(output)

    @staticmethod
    def append(output):
        filename = "output_IAM.csv"
        with open(filename, "a", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(output)
