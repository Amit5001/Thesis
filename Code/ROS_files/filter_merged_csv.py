#!/usr/bin/env python3
"""
Script to filter out unwanted columns from the merged CSV file
"""
import csv
import re
from pathlib import Path

def filter_merged_csv(input_file, output_file=None):
    """Filter out unwanted columns from merged CSV file"""
    
    input_path = Path(input_file)
    if output_file is None:
        output_file = input_path.parent / f"{input_path.stem}_filtered.csv"
    else:
        output_file = Path(output_file)
    
    # Define columns to remove
    columns_to_remove = [
        '_imu_data_orientation_covariance',
        '_imu_data_header',
        '_imu_data_angular_velocity_covariance', 
        '_imu_data_linear_acceleration_covariance',
        '_desire_stab_layout.data_offset',
        '_rc_channel_data_layout.data_offset'
    ]
    
    # Patterns for columns to remove (for complex patterns like all _imu_filter acc,gyro,mag)
    column_patterns_to_remove = [
        r'_imu_filter_.*acc.*',  # All _imu_filter columns containing 'acc'
        r'_imu_filter_.*gyro.*', # All _imu_filter columns containing 'gyro' 
        r'_imu_filter_.*mag.*'   # All _imu_filter columns containing 'mag'
    ]
    
    print(f"Filtering columns from: {input_file}")
    print(f"Output will be saved to: {output_file}")
    
    # Read the input CSV
    with open(input_path, 'r', newline='') as infile:
        reader = csv.reader(infile)
        headers = next(reader)
        
        print(f"Original file has {len(headers)} columns")
        
        # Determine which columns to keep
        columns_to_keep = []
        removed_columns = []
        
        for i, header in enumerate(headers):
            should_remove = False
            
            # Check exact matches
            if header in columns_to_remove:
                should_remove = True
                removed_columns.append(header)
            
            # Check pattern matches
            for pattern in column_patterns_to_remove:
                if re.match(pattern, header):
                    should_remove = True
                    removed_columns.append(header)
                    break
            
            if not should_remove:
                columns_to_keep.append(i)
        
        print(f"Removing {len(removed_columns)} columns:")
        for col in sorted(removed_columns):
            print(f"  - {col}")
        
        print(f"Keeping {len(columns_to_keep)} columns")
        
        # Write filtered CSV
        with open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # Write filtered headers
            filtered_headers = [headers[i] for i in columns_to_keep]
            writer.writerow(filtered_headers)
            
            # Write filtered data rows
            row_count = 0
            for row in reader:
                filtered_row = [row[i] if i < len(row) else '' for i in columns_to_keep]
                writer.writerow(filtered_row)
                row_count += 1
            
            print(f"Filtered data written to: {output_file}")
            print(f"Total rows: {row_count}")
            print(f"Total columns: {len(filtered_headers)}")
    
    return output_file

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Filter unwanted columns from merged CSV file")
    parser.add_argument('--input', required=True, help="Input CSV file path")
    parser.add_argument('--output', help="Output CSV file path (optional)")
    
    args = parser.parse_args()
    
    filter_merged_csv(args.input, args.output)
