import os
from datetime import datetime
import csv
import argparse
import re
from termcolor import colored  

class WeatherDataLoader:
    def __init__(self, columns, folder_path):
        self.columns = columns
        self.folder_path = folder_path
        self.data = []

    def get_valid_files(self, year):
        valid_files = []
        for file in os.listdir(self.folder_path):
            if file.endswith('txt') and str(year) in file:
                valid_files.append(os.path.join(self.folder_path, file))
        return valid_files

    def load_data_from_files(self, files):
        for file_path in files:
            self.file_reading(file_path)

    def file_reading(self, file_path): 
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            if not all(col in reader.fieldnames for col in self.columns):
                return

            raw_data = [row for row in reader]
            self.filter_data(raw_data)

    def filter_data(self, raw_data):
        for row in raw_data:
            try:
                max_temp = float(row['Max TemperatureC'])
                min_temp = float(row['Min TemperatureC'])
                max_humid = float(row['Max Humidity'])
                pkt = row['PKT']

                self.data.append({
                    'max_temp': max_temp,
                    'min_temp': min_temp,
                    'humidity': max_humid,
                    'time': pkt
                })
            except ValueError:
                continue


class WeatherReportGenerator:
    
    def generate_annual_report(self, data, year):
        if not data:
            print(f"No data available for the year {year}.")
            return
        
        max_temp_record = max(data, key=lambda x: x['max_temp'])
        min_temp_record = min(data, key=lambda x: x['min_temp'])
        max_humid_record = max(data, key=lambda x: x['humidity'])
        
        max_temp_date = datetime.strptime(max_temp_record['time'], '%Y-%m-%d')
        min_temp_date = datetime.strptime(min_temp_record['time'], '%Y-%m-%d')
        max_humid_date = datetime.strptime(max_humid_record['time'], '%Y-%m-%d')

        formatted_max_date = max_temp_date.strftime('%B %d')
        formatted_min_date = min_temp_date.strftime('%B %d')
        formatted_max_humid = max_humid_date.strftime('%B %d')

        print(f"Highest: {max_temp_record['max_temp']}C on {formatted_max_date}")
        print(f"Lowest: {min_temp_record['min_temp']}C on {formatted_min_date}")
        print(f"Humidity: {max_humid_record['humidity']}% on {formatted_max_humid}")
       
    
    def generate_monthly_report(self,data,month):
        monthly_data = [record for record in data if datetime.strptime(record['time'], '%Y-%m-%d').month == month]
        
        if not monthly_data:
            print(f"No data available")
            return
        
        avg_max_temp = sum(record['max_temp'] for record in monthly_data) / len(monthly_data)
        avg_min_temp = sum(record['min_temp'] for record in monthly_data) / len(monthly_data)
        avg_mean_humidity = sum(record['humidity'] for record in monthly_data) / len(monthly_data)

        print(f"Highest Average: {avg_max_temp:.1f}C")
        print(f"Lowest Average: {avg_min_temp:.1f}C")
        print(f"Average Mean Humidity: {avg_mean_humidity:.1f}%")
       
        WeatherReportGenerator.print_colorful_report(monthly_data)

   
    def print_colorful_report(data):
        for r in data:
            min_temp = int(r['min_temp'])
            max_temp = int(r['max_temp'])
            day = datetime.strptime(r['time'], '%Y-%m-%d').strftime('%d')
            print(f"{day} {colored('+' * min_temp, 'blue')}{colored('+' * max_temp, 'red')} {min_temp}-{max_temp}")

def check_by_month(value):
    try:
        return datetime.strptime(value, '%Y/%m')
    except ValueError:
        raise argparse.ArgumentTypeError(f'Invalid month format')

def check_by_year(value):
    if not re.match(r'^\d{4}$', value):
        raise argparse.ArgumentTypeError(f'Invalid year format')
    return value

class WeatherManAnalyzer:
    def __init__(self, columns, folder_path):
        self.loader = WeatherDataLoader(columns, folder_path)
        self.report_generator = WeatherReportGenerator()
    
    def generate_report(self, year, report_type, month):
        if not (2000 <= int(year) <= datetime.now().year):
            raise ValueError(f"Invalid year")
        
        if report_type == 'monthly':
            if month is None:
                raise ValueError("Month is required for monthly reports.")
            if not (1 <= month <= 12):
                raise ValueError(f"Invalid month: {month}. Valid months are between 1 and 12.")
        
        valid_files = self.loader.get_valid_files(year)
        self.loader.load_data_from_files(valid_files)
        
        if report_type == 'annual':
            self.report_generator.generate_annual_report(self.loader.data, year)

        elif report_type == 'monthly':
            self.report_generator.generate_monthly_report(self.loader.data, month)

        elif report_type == 'multiple':
            self.report_generator.generate_annual_report(self.loader.data, year)
            self.report_generator.generate_monthly_report(self.loader.data, month)

        else:
            raise ValueError("Invalid report type. Please enter 'annual' or 'monthly'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weather Reports")
    parser.add_argument('folder_path', type=str, help="Path to the folder")
    parser.add_argument('year', type=check_by_year, help="Year for the report")
    parser.add_argument('report_type', choices=['annual', 'monthly', 'multiple'], help="Type of report: 'annual' or 'monthly' or multiple")
    parser.add_argument('--month', type=check_by_month, help="Month for the report")
    

    args = parser.parse_args()
    
    columns_to_extract = ['PKT', 'Max TemperatureC', 'Min TemperatureC', 'Max Humidity']
    weather_man = WeatherManAnalyzer(columns_to_extract, args.folder_path)
    
    if args.report_type == 'monthly':
        month = int(input("Enter your month to show Weather Data Analyzer:"))
        weather_man.generate_report(args.year, args.report_type,month)
    if args.report_type == 'annual':
        weather_man.generate_report(args.year,args.report_type)
    else:
        weather_man.generate_report(args.year, args.report_type,args.month)
        month = int(input("Enter your month to show Weather Data Analyzer:"))
        weather_man.generate_report(args.year,args.report_type, month)
