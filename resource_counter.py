#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 21:47:13 2021

@author: Max Harder
"""

# standard library imports
import argparse  # command-line
import os  # operating system interfaces
from datetime import date  # today's date

# related third party imports
import requests  # HTTP library
from bs4 import BeautifulSoup  # pull data
from tqdm import tqdm  # progress bar
from pandas import DataFrame  # tabular data
from pandas import read_excel
from matplotlib import pyplot as plt
from matplotlib import cm

# local application/library specific imports
from data.resource_lists import all_urls  # 88 URLs
from data.resource_lists import resource_categories  # 11 categories
from data.resource_lists import resource_types  # 8 types


DESCRIPTION = '''
Scrape data from URLs and return count values of list items in XSLX file.

The XLSX file includes 12 columns (for 11 resource categories plus totals)
and 9 rows (for 8 resource types plus totals).'''
EPILOG= 'Made with love for Vikalp Sangam (https://vikalpsangam.org/).'
DEFAULT_PATH=os.path.join('output', date.today().strftime('%Y-%m-%d')+'.xlsx')
parser = argparse.ArgumentParser(prog='ResourceCounter',
                                 description=DESCRIPTION,
                                 epilog=EPILOG)
parser.add_argument('Path', nargs='?', default=DEFAULT_PATH, type=str,
                    help='Path for output file', metavar='path')
args = parser.parse_args()
my_file = args.Path

def welcome():
    """Welcome the user."""
    print(r''' ____                                     ____                  _
|  _ \ ___  ___  ___  _   _ _ __ ___ ___ / ___|___  _   _ _ __ | |_ ___ _ __
| |_) / _ \/ __|/ _ \| | | | '__/ __/ _ \ |   / _ \| | | | '_ \| __/ _ \ '__|
|  _ <  __/\__ \ (_) | |_| | | | (_|  __/ |__| (_) | |_| | | | | ||  __/ |
|_| \_\___||___/\___/ \__,_|_|  \___\___|\____\___/ \__,_|_| |_|\__\___|_|

Max Harder, mail@max-har.de (January 2021)
''')

def file_management():
    """Create necessary folders.

    output: full path of output file"""
    cwd = os.getcwd()
    file_path, file_name = my_file.rsplit('/', 1)
    absolute_path = os.path.join(cwd, file_path)
    file_format = '.xlsx'
    try:
        if not os.path.exists(absolute_path):
            os.makedirs(absolute_path)
        if not file_name.endswith(file_format):
            file_name = file_name+file_format
    except (OSError, IOError):
        print('Error: document name or path is not valid')
    this_path = os.path.join(absolute_path, file_name)
    print(f'Output file: {this_path}\n')
    return this_path

def counter():
    """Count resources on websites.

    output: list containing a count values list for each resource category
    """
    count_data = []
    for cat_urls in tqdm(all_urls):
        myvalues = []
        for url in cat_urls:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            ol_tags = [ol for ol in soup.findAll('ol')
                       if ol.parent.name != 'li']
            if ol_tags:
                for ol_tag in ol_tags:
                    mylist = [1 for li in ol_tag.findAll('li')]
                    myvalues.append(sum(mylist))
            else:
                myvalues.append(0)
            if len(ol_tags) == 2:
                myvalues.append(0)
        print(myvalues)
        count_data.append(myvalues)
        if len(myvalues) != 8:
            print('Error: incorrect length')
    return count_data

def transfer(count_data, output_path):
    """Transfer data to excel sheet.

    param1: list containing a count values list for each resource category
    output: None
    """
# totals column
    for cnt_list in count_data:
        cnt_list.append(sum(cnt_list))
# totals row
    row_sums = []
    for num in range(len(resource_types)):
        row_sums.append([cnt_list[num] for cnt_list in count_data])
    row_totals = [sum(element) for element in row_sums]
    row_totals.append(sum(row_totals))
# data frame
    count_data.append(row_totals)
    resource_df = DataFrame(zip(*count_data))
# write
    resource_categories.append('Total')
    resource_types.append('Total')
    resource_df.index = resource_types
    resource_df.columns = resource_categories
    resource_df.to_excel(output_path)

# plotting
def plotter(path_of_output_file):
    """Read data and plot charts.

    param1:
    """
    # read data
    excel_df = read_excel(path_of_output_file, header=0, index_col=0)
    totals_all = excel_df.iloc[:8, :11]
    totals_col = excel_df.iloc[8, :11]
    totals_row = excel_df.iloc[:8, 11]
    # plot charts
    plot_bar(totals_all, path_of_output_file)
    plot_pie(totals_col, totals_row, path_of_output_file)

def plot_bar(totals_all, path_of_output_file):
    """Plot bar chart.

    param1:
    param2:
    """
    cmap = cm.get_cmap('Spectral')  # colour map
    totals_all.plot.barh(figsize=(26, 10), stacked=True, cmap=cmap, fontsize=16)
    plt.suptitle('Resource Categories per Resource Type', fontsize=20)
    plt.legend(fontsize=16)
    plt.tight_layout()
    plt.savefig(path_of_output_file[:-5]+'_bar.png', format='png')

def plot_pie(totals_col, totals_row, path_of_output_file):
    """Plots pie charts.

    param1:
    param2:
    param3:
    """
    cmap = cm.get_cmap('Spectral')   # colour map
    fig = plt.figure()
    # subplot 1
    ax1 = fig.add_subplot(121)  # nrows, ncols, and index
    totals_col.plot.pie(figsize=(26, 10), legend=False, cmap=cmap, fontsize=16)
    ax1.set_title('Resource Categories', fontsize=20)
    plt.axis('off')
    # subplot 2
    ax2 = fig.add_subplot(122)  # nrows, ncols, and index
    totals_row.plot.pie(figsize=(26, 10), legend=False, cmap=cmap, fontsize=16)
    ax2.set_title('Resource Types', fontsize=20)
    plt.axis('off')
    # save
    plt.tight_layout()
    plt.savefig(path_of_output_file[:-5]+'_pie.png', format='png')


if __name__ == '__main__':
    # code below is only executed when the module is run directly
    welcome()
    full_path = file_management()
    cnt_data = counter()
    transfer(cnt_data, full_path)
    plotter(full_path)
