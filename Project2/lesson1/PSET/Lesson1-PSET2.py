# -*- coding: utf-8 -*-
# Find the time and value of max load for each of the regions
# COAST, EAST, FAR_WEST, NORTH, NORTH_C, SOUTHERN, SOUTH_C, WEST
# and write the result out in a csv file, using pipe character | as the delimiter.
# An example output can be seen in the "example.csv" file.

import xlrd
import os
import csv
import ast
from zipfile import ZipFile

datafile = "2013_ERCOT_Hourly_Load_Data.xls"
outfile = "2013_Max_Loads.csv"


def open_zip(datafile):
    with ZipFile('{0}.zip'.format(datafile), 'r') as myzip:
        myzip.extractall()


def parse_file(datafile):
    workbook = xlrd.open_workbook(datafile)
    sheet = workbook.sheet_by_index(0)
    headers = sheet.row_values(0, start_colx=0, end_colx=None)
    ans = []
    for col in range(1, sheet.ncols-1):
		col_vals = sheet.col_values(col, start_rowx=1, end_rowx=None)
		max_val = max(col_vals)
		max_index = col_vals.index(max_val)
		max_date = xlrd.xldate_as_tuple(sheet.cell_value(max_index+1, 0),0)
		ans.append({'Station': headers[col], 'Max Load': max_val, 'Year': max_date[0], 'Month': max_date[1], 'Day': max_date[2], 'Hour': max_date[3]})
		
    return ans
	
	
def save_file(data, filename):
	#Station|Year|Month|Day|Hour|Max Load
	fields = ["Station", "Year", "Month", "Day", "Hour", "Max Load"]
	with open(filename, 'wb') as the_file:
		writer = csv.DictWriter(the_file, delimiter='|', fieldnames=fields)
		writer.writeheader()
		for row in data:
			writer.writerow(row)

    
def test():
    open_zip(datafile)
    data = parse_file(datafile)
    save_file(data, outfile)

    number_of_rows = 0
    stations = []

    ans = {'FAR_WEST': {'Max Load': '2281.2722140000024',
                        'Year': '2013',
                        'Month': '6',
                        'Day': '26',
                        'Hour': '17'}}
    correct_stations = ['COAST', 'EAST', 'FAR_WEST', 'NORTH',
                        'NORTH_C', 'SOUTHERN', 'SOUTH_C', 'WEST']
    fields = ['Year', 'Month', 'Day', 'Hour', 'Max Load']

    with open(outfile) as of:
        csvfile = csv.DictReader(of, delimiter="|")
        for line in csvfile:
            station = line['Station']
            if station == 'FAR_WEST':
                for field in fields:
                    # Check if 'Max Load' is within .1 of answer
                    if field == 'Max Load':
                        max_answer = round(float(ans[station][field]), 1)
                        max_line = round(float(line[field]), 1)
                        assert max_answer == max_line

                    # Otherwise check for equality
                    else:
                        assert ans[station][field] == line[field]

            number_of_rows += 1
            stations.append(station)

        # Output should be 8 lines not including header
        
        assert number_of_rows == 8

        # Check Station Names
        
        assert set(stations) == set(correct_stations)

        
if __name__ == "__main__":
    test()
