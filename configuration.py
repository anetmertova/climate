import os
import datetime
import configparser
import argparse
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

def fetch_data(station_id, start_date, end_date, config):
    url = config['API']['URL'].format(station_id=station_id, start=start_date, end=end_date)
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    data = response.json()
    return pd.DataFrame(data)

def preprocess_data(data):
    data['date'] = pd.to_datetime(data['date'], utc=True)
    data.set_index('date', inplace=True)
    data['temperature'] = data['TL']
    data['precipitation'] = data['RR']
    return data

def plot_data(data, config, date):
    fig, ax = plt.subplots(figsize=(19.2, 10.8))

    output_file = config['Plot']['output_file']
    if date == "latest":
        output_file = 'latest_climate.png'
    else:
        output_file = f"{date}_climate.png"
    
    dpi = int(config['Plot']['dpi'])
    ax.plot(data.index, data['temperature'], label='Temperature', color=config['Style']['line_color'])
    ax.set_facecolor(config['Style']['background_color'])
    ax.set_title('Annually Accumulated Precipitation Sum', color=config['Style']['title_color'])
    plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
    plt.show()

def main(date=None):
    if date is None:
        date = datetime.datetime.now().strftime("%Y%m%d")
    
    config = load_config()
    station_id = config['API']['station_id']

    start_date = f"{date}T00:00:00Z"
    end_date = f"{date}T23:59:59Z"
    
    data = fetch_data(station_id, start_date, end_date, config)
    data = preprocess_data(data)
    plot_data(data, config, date)

if __name__ == "__main__":
    main()
