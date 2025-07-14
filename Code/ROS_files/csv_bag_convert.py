import os
import csv
import rclpy
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
import numpy as np
import re
from pathlib import Path

def extract_message_fields(message, prefix=""):
    """Extract fields from a ROS message into a flat dictionary"""
    fields = {}
    
    if hasattr(message, '__slots__'):
        for field_name in message.__slots__:
            if field_name.startswith('_'):
                field_name = field_name[1:]  # Remove leading underscore
            
            value = getattr(message, field_name)
            full_field_name = f"{prefix}{field_name}" if prefix else field_name
            
            # Handle nested messages
            if hasattr(value, '__slots__'):
                nested_fields = extract_message_fields(value, f"{full_field_name}.")
                fields.update(nested_fields)
            # Handle numpy arrays
            elif isinstance(value, np.ndarray):
                if value.size <= 9:  # For small arrays like covariance matrices
                    for i, val in enumerate(value.flatten()):
                        fields[f"{full_field_name}[{i}]"] = float(val)
                else:
                    fields[f"{full_field_name}_mean"] = float(np.mean(value))
                    fields[f"{full_field_name}_std"] = float(np.std(value))
            # Handle lists/arrays
            elif hasattr(value, '__iter__') and not isinstance(value, str):
                try:
                    for i, val in enumerate(value):
                        fields[f"{full_field_name}[{i}]"] = float(val) if isinstance(val, (int, float)) else str(val)
                except:
                    fields[full_field_name] = str(value)
            # Handle basic types
            else:
                if isinstance(value, (int, float)):
                    fields[full_field_name] = float(value)
                else:
                    fields[full_field_name] = str(value)
    
    return fields

def get_message_headers(message):
    """Get all possible field names from a message for CSV headers"""
    sample_fields = extract_message_fields(message)
    return ['timestamp'] + list(sample_fields.keys())

def extract_rosbag_to_csv(bag_path, output_dir, merge_option="default", apply_column_filter=True):
    rclpy.init()

    # Create the reader for the bag file
    reader = SequentialReader()
    storage_options = StorageOptions(uri=bag_path, storage_id='sqlite3')
    converter_options = ConverterOptions(input_serialization_format='cdr', output_serialization_format='cdr')
    reader.open(storage_options, converter_options)

    # Get the list of topics and their types
    topic_types = reader.get_all_topics_and_types()
    topics = {topic.name: get_message(topic.type) for topic in topic_types}

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Prepare a CSV file for each topic
    writers = {}
    csv_files = {}
    headers_written = {}

    for topic_name in topics.keys():
        csv_file_path = os.path.join(output_dir, f"{topic_name.replace('/', '_')}.csv")
        csv_file = open(csv_file_path, mode='w', newline='')
        writers[topic_name] = csv.writer(csv_file)
        csv_files[topic_name] = csv_file
        headers_written[topic_name] = False

    # Read all messages
    while reader.has_next():
        (topic_name, serialized_data, timestamp) = reader.read_next()

        # Deserialize the message
        msg_type = topics[topic_name]
        message = deserialize_message(serialized_data, msg_type)

        # Extract fields from the message
        fields = extract_message_fields(message)
        
        # Write headers if not already written
        if not headers_written[topic_name]:
            headers = ['timestamp'] + list(fields.keys())
            writers[topic_name].writerow(headers)
            headers_written[topic_name] = True

        # Write data row
        row = [timestamp] + list(fields.values())
        writers[topic_name].writerow(row)

    # Close all CSV files
    for csv_file in csv_files.values():
        csv_file.close()

    rclpy.shutdown()
    
    print(f"Successfully extracted {len(topics)} topics to CSV files in {output_dir}")
    for topic_name in topics.keys():
        print(f"  - {topic_name.replace('/', '_')}.csv")
    
    # Handle different merge options
    if merge_option == "none":
        print(f"\n💡 Skipped creating merged file (--no-merge specified)")
    elif merge_option == "all":
        # Merge ALL CSV files into one
        merged_file = merge_all_csv_files(output_dir, apply_column_filter)
        if merged_file:
            print(f"\n✅ Successfully merged all CSV files into one file!")
        else:
            print(f"\n⚠️  Could not create merged file")
    elif merge_option == "default":
        # Create merged flight data file (current behavior)
        merged_file = create_merged_flight_data(output_dir)
        if merged_file:
            print(f"\n✅ Successfully created merged flight data file!")
        else:
            print(f"\n⚠️  Could not create merged flight data file (missing required topics)")

def load_csv_manually(file_path):
    """Load CSV file using Python's csv module for merging"""
    data = []
    headers = []
    
    try:
        with open(file_path, 'r', newline='') as csvfile:
            # Try multiple strategies to read the CSV
            reader = None
            
            # Strategy 1: Try to detect the dialect
            try:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample)
                reader = csv.reader(csvfile, dialect)
            except:
                # Strategy 2: Use standard comma delimiter
                csvfile.seek(0)
                reader = csv.reader(csvfile, delimiter=',')
            
            if reader is None:
                # Strategy 3: Try semicolon delimiter
                csvfile.seek(0)
                reader = csv.reader(csvfile, delimiter=';')
            
            # Read headers
            headers = next(reader)
            
            # Read data
            for row in reader:
                if len(row) == len(headers):  # Only keep complete rows
                    try:
                        # Convert to appropriate types
                        converted_row = []
                        for i, value in enumerate(row):
                            if headers[i] == 'timestamp':
                                converted_row.append(int(float(value)))  # timestamp as int
                            else:
                                try:
                                    # Try to convert to float first
                                    float_val = float(value)
                                    converted_row.append(float_val)
                                except (ValueError, TypeError):
                                    # If float conversion fails, try to handle special cases
                                    if value.strip() == '' or value.lower() in ['nan', 'inf', '-inf']:
                                        converted_row.append(0.0)  # Use 0.0 for empty/invalid values
                                    else:
                                        # For truly non-numeric data, try to extract a number or use 0
                                        try:
                                            # Try to extract first number from string
                                            numbers = re.findall(r'-?\d+\.?\d*', str(value))
                                            if numbers:
                                                converted_row.append(float(numbers[0]))
                                            else:
                                                converted_row.append(0.0)
                                        except:
                                            converted_row.append(0.0)
                        data.append(converted_row)
                    except (ValueError, TypeError):
                        continue  # Skip rows with conversion errors
        
        return headers, data
    
    except Exception as e:
        print(f"  Error loading {file_path} for merging: {e}")
        return None, None

def interpolate_data(timestamps, values, target_timestamps):
    """Simple linear interpolation for numeric data"""
    try:
        # Convert to numpy arrays and ensure they're numeric
        timestamps = np.array(timestamps, dtype=float)
        values = np.array(values, dtype=float)
        target_timestamps = np.array(target_timestamps, dtype=float)
        
        return np.interp(target_timestamps, timestamps, values)
    except (ValueError, TypeError) as e:
        # If interpolation fails (e.g., non-numeric data), return the closest value
        if len(values) > 0:
            # Find the closest timestamp
            closest_idx = np.argmin(np.abs(np.array(timestamps, dtype=float) - target_timestamps[0]))
            return [values[closest_idx]]
        else:
            return [0.0]  # Default value if no data available

def create_merged_flight_data(output_dir):
    """Create a merged flight data file from the individual CSV files"""
    output_dir = Path(output_dir)
    
    # Define the files we need for the merged data (essential flight data only)
    data_sources = {
        'angular': '_euler_angles_data.csv',
        'motors': '_motor_pwm.csv', 
        'power': '_drone_header.csv',
        'lidar': '_current_lidar_distance.csv'
    }
    
    print("\nCreating merged flight data file...")
    print("  Using only essential flight data (ignoring logs, debug data, etc.)")
    
    # Load all data
    all_data = {}
    
    for source_name, filename in data_sources.items():
        file_path = output_dir / filename
        
        if not file_path.exists():
            print(f"  Warning: {file_path} not found. Skipping {source_name} data.")
            continue
        
        print(f"  Loading {source_name} data from {filename}")
        headers, data = load_csv_manually(file_path)
        
        if headers and data:
            all_data[source_name] = {'headers': headers, 'data': data}
            print(f"    Loaded {len(data)} rows")
        else:
            print(f"    Failed to load {source_name} data")
    
    if not all_data:
        print("  No valid data sources found for merging!")
        return None
    
    # Find common timestamp range
    all_timestamps = []
    for source_name, source_data in all_data.items():
        timestamps = [row[0] for row in source_data['data']]  # timestamp is first column
        all_timestamps.extend(timestamps)
    
    min_timestamp = min(all_timestamps)
    max_timestamp = max(all_timestamps)
    
    # Create common timestamp grid (50Hz = 20ms intervals)
    timestamp_step = 20_000_000  # 20ms in nanoseconds
    common_timestamps = np.arange(min_timestamp, max_timestamp, timestamp_step)
    
    print(f"  Creating common timeline with {len(common_timestamps)} points")
    print(f"  Time range: {(max_timestamp - min_timestamp)/1e9:.2f} seconds")
    
    # Prepare output data
    output_headers = ['timestamp', 'time_sec']
    output_data = []
    
    # Add headers for each data source
    for source_name, source_data in all_data.items():
        headers = source_data['headers']
        for header in headers[1:]:  # Skip timestamp column
            if source_name == 'power':
                # Only keep voltage and current from power data
                if header in ['voltage', 'current']:
                    output_headers.append(header)
            else:
                output_headers.append(header)
    
    # Interpolate each data source to common timestamps
    for i, common_ts in enumerate(common_timestamps):
        row = [common_ts, (common_ts - min_timestamp) / 1e9]  # timestamp and time_sec
        
        for source_name, source_data in all_data.items():
            headers = source_data['headers']
            data = source_data['data']
            
            # Extract timestamps and values for this source
            source_timestamps = [row[0] for row in data]
            
            # Interpolate each column (skip timestamp column)
            for col_idx in range(1, len(headers)):
                header = headers[col_idx]
                
                # Skip non-essential columns from power data
                if source_name == 'power' and header not in ['voltage', 'current']:
                    continue
                
                values = [row[col_idx] for row in data]
                interpolated_value = interpolate_data(source_timestamps, values, [common_ts])[0]
                row.append(interpolated_value)
        
        output_data.append(row)
    
    # Write merged CSV
    merged_file_path = output_dir / 'merged_flight_data.csv'
    with open(merged_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_headers)
        writer.writerows(output_data)
    
    print(f"  Merged flight data saved to: merged_flight_data.csv")
    print(f"  Total records: {len(output_data)}")
    print(f"  Columns: {output_headers}")
    
    return merged_file_path

def merge_all_csv_files(output_dir, apply_column_filter=True):
    """Merge ALL CSV files into a single CSV file with timestamps"""
    output_dir = Path(output_dir)
    
    print("\nMerging all CSV files into one...")
    if apply_column_filter:
        print("  Applying column filtering to remove unwanted data")
    
    # Define files to ignore during merging
    ignore_files = {
        '_rosout.csv',
        '_parameter_events.csv', 
        '_pid_loaded.csv',
        '_pid_to_flash.csv',
        '_magnetometer_data.csv',
        '_filter_to_flash.csv',
        '_events_write_split.csv',
        '_current_magwick_return_data.csv',
        'merged_flight_data.csv',
        'merged_all_data.csv',
        'merged_all_data_filtered.csv'
    }
    
    # Find all CSV files in the directory
    csv_files = list(output_dir.glob("*.csv"))
    
    if not csv_files:
        print("  No CSV files found to merge!")
        return None
    
    # Filter out ignored files
    csv_files = [f for f in csv_files if f.name not in ignore_files]
    
    print(f"  Found {len(csv_files)} CSV files to merge (after filtering)")
    if len(ignore_files) > 2:  # More than just the merged files
        print(f"  Ignoring {len(ignore_files) - 2} files: {', '.join(sorted([f for f in ignore_files if not f.startswith('merged_')]))}")
    
    # Load all data with topic names as prefixes
    all_data = {}
    all_timestamps = []
    
    for csv_file in csv_files:
        topic_name = csv_file.stem  # filename without extension
        print(f"  Loading {topic_name}")
        
        headers, data = load_csv_manually(csv_file)
        
        if headers and data:
            all_data[topic_name] = {'headers': headers, 'data': data}
            # Collect timestamps
            timestamps = [row[0] for row in data]
            all_timestamps.extend(timestamps)
            print(f"    Loaded {len(data)} rows")
        else:
            print(f"    Failed to load {topic_name}")
    
    if not all_data:
        print("  No valid data found for merging!")
        return None
    
    # Find common timestamp range
    min_timestamp = min(all_timestamps)
    max_timestamp = max(all_timestamps)
    
    # Create common timestamp grid (50Hz = 20ms intervals)
    timestamp_step = 20_000_000  # 20ms in nanoseconds
    common_timestamps = np.arange(min_timestamp, max_timestamp, timestamp_step)
    
    print(f"  Creating common timeline with {len(common_timestamps)} points")
    print(f"  Time range: {(max_timestamp - min_timestamp)/1e9:.2f} seconds")
    
    # Prepare output headers
    output_headers = ['timestamp', 'time_sec']
    
    # Add all headers from all files with topic prefixes
    for topic_name, topic_data in all_data.items():
        headers = topic_data['headers']
        for header in headers[1:]:  # Skip timestamp column
            # Add topic prefix to avoid column name conflicts
            prefixed_header = f"{topic_name}_{header}"
            output_headers.append(prefixed_header)
    
    # Apply column filtering if requested
    if apply_column_filter:
        columns_to_keep, removed_columns = filter_columns(output_headers, apply_column_filter)
        filtered_headers = [output_headers[i] for i in columns_to_keep]
        
        if removed_columns:
            print(f"  Filtering out {len(removed_columns)} unwanted columns:")
            for col in sorted(removed_columns):
                print(f"    - {col}")
        
        output_headers = filtered_headers
    
    # Interpolate each data source to common timestamps
    output_data = []
    
    for i, common_ts in enumerate(common_timestamps):
        row = [common_ts, (common_ts - min_timestamp) / 1e9]  # timestamp and time_sec
        
        # Add data from each topic
        for topic_name, topic_data in all_data.items():
            headers = topic_data['headers']
            data = topic_data['data']
            
            # Extract timestamps and values for this topic
            source_timestamps = [row[0] for row in data]
            
            # Interpolate each column (skip timestamp column)
            for col_idx in range(1, len(headers)):
                # Check if this column should be included after filtering
                prefixed_header = f"{topic_name}_{headers[col_idx]}"
                if apply_column_filter and prefixed_header not in output_headers:
                    continue  # Skip filtered out columns
                
                values = [row[col_idx] for row in data]
                interpolated_value = interpolate_data(source_timestamps, values, [common_ts])[0]
                row.append(interpolated_value)
        
        output_data.append(row)
    
    # Write merged CSV
    output_filename = 'merged_all_data_filtered.csv' if apply_column_filter else 'merged_all_data.csv'
    merged_file_path = output_dir / output_filename
    with open(merged_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(output_headers)
        writer.writerows(output_data)
    
    print(f"  All data merged and saved to: {output_filename}")
    print(f"  Total records: {len(output_data)}")
    print(f"  Total columns: {len(output_headers)}")
    
    return merged_file_path

def filter_columns(headers, apply_filter=True):
    """Filter out unwanted columns from headers list"""
    if not apply_filter:
        return list(range(len(headers))), []
    
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
    
    return columns_to_keep, removed_columns

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Extract ROS2 bag data into separate CSV files for each topic.")
    parser.add_argument('--bag', required=True, help="Path to the ROS2 bag file")
    parser.add_argument('--output', required=True, help="Directory to save the output CSV files")
    
    # Merge options - mutually exclusive group
    merge_group = parser.add_mutually_exclusive_group()
    merge_group.add_argument('--merge', choices=['all'], help="Merge options: 'all' = merge all CSV files into one")
    merge_group.add_argument('--no-merge', action='store_true', help="Skip creating any merged files")
    
    # Column filtering option
    parser.add_argument('--no-filter', action='store_true', help="Skip column filtering (keep all columns)")

    args = parser.parse_args()

    # Determine merge option
    if args.no_merge:
        merge_option = "none"
    elif args.merge == "all":
        merge_option = "all"
    else:
        merge_option = "default"  # Default: create merged flight data file
    
    # Determine column filtering
    apply_column_filter = not args.no_filter

    extract_rosbag_to_csv(args.bag, args.output, merge_option, apply_column_filter)
