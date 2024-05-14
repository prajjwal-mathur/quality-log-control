from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json



app = Flask(__name__)

LOGS_DIR = 'logs/'


def filter_logs(logs, filters):

    filtered_logs = logs

    for key, value in filters.items():
        if key == 'level' and value:
            filtered_logs = [log for log in filtered_logs if log.get('level') == value]

        elif key == 'log_string' and value:
            filtered_logs = [log for log in filtered_logs if value.lower() in log.get('log_string', '').lower()]

        elif key == 'timestamp' and value:
            try:
                start_time, end_time = value.split(',')
                start_time = datetime.strptime(start_time.strip(), "%Y-%m-%dT%H:%M:%SZ")
                end_time = datetime.strptime(end_time.strip(), "%Y-%m-%dT%H:%M:%SZ")
                filtered_logs = [log for log in filtered_logs if
                                 is_within_time_range(log.get('timestamp'), start_time, end_time)]
            except ValueError:
                print("Invalid timestamp format. Expected ISO 8601 format (e.g., 2023-09-10T00:00:00Z).")

        elif key == 'source' and value:  # Apply source filter if value is provided
            filtered_logs = [log for log in filtered_logs if log.get('metadata', {}).get('source') == value]
    return filtered_logs


def is_within_time_range(log_timestamp, start_time, end_time):
    try:
        log_time = datetime.strptime(log_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        return start_time <= log_time <= end_time
    except ValueError:
        return False

def parse_log_file(log_file):
    logs = []
    with open(log_file, 'r') as file:
        for line in file:
            try:
                log = json.loads(line.strip())
                logs.append(log)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON in '{log_file}': {e}")
                continue

    return logs



def write_log_entry(log_file, log_data):
    if os.path.exists(log_file):
        raise FileExistsError(f"Error: Log file '{log_file}' already exists.")

    with open(log_file, 'w') as file:
        file.write(json.dumps(log_data) + '\n')

@app.route('/')
def index():
    return render_template('index.html')


from datetime import datetime

from datetime import datetime


@app.route('/search', methods=['GET'])
def search_logs():
    filters = {}

    # Process search filters
    level = request.args.get('level')
    if level:
        filters['level'] = level.lower()

    log_string = request.args.get('log_string')
    if log_string:
        filters['log_string'] = log_string.lower()

    timestamp = request.args.get('timestamp')
    if timestamp:
        try:
            start_time, end_time = timestamp.split(',')
            filters['timestamp'] = (start_time.strip(), end_time.strip())
        except ValueError:
            pass

    source = request.args.get('source')
    if source:
        filters['source'] = source

    # Filter logs based on filters
    log_files = [os.path.join(LOGS_DIR, file) for file in os.listdir(LOGS_DIR) if file.endswith('.log')]
    logs = []
    for log_file in log_files:
        logs.extend(parse_log_file(log_file))

    filtered_logs = filter_logs(logs, filters)
    return jsonify(results=filtered_logs)


@app.route('/create_log')
def log_form():
    return render_template('create_log.html')


@app.route('/create_log', methods=['POST'])
def create_log():
    log_level = request.form.get('level')
    log_message = request.form.get('log_message')
    source = request.form.get('source')

    if log_level and log_message and source:
        timestamp = datetime.utcnow().isoformat() + 'Z'
        log_data = {
            'level': log_level,
            'log_string': log_message,
            'timestamp': timestamp,
            'metadata': {
                'source': source
            }
        }
        log_file = os.path.join(LOGS_DIR, f"log_{source}.log")

        try:
            write_log_entry(log_file, log_data)
            return redirect(url_for('index', message="Log entry added successfully."))
        except FileExistsError as e:
            return str(e), 400
    else:
        return "Error: Incomplete log data submitted.", 400


if __name__ == '__main__':
    app.run(debug=True)
