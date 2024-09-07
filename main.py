import pygsheets
from datetime import datetime
from utils import get_data
import pandas as pd
import numpy as np
from flask import Flask
import httplib2shim
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

app = Flask(__name__)

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route('/', methods=['GET'])
def main():
    # http = httplib2shim.Http()
    client = pygsheets.authorize(service_account_file = 'service_account.json')

    ss = client.open_by_url('https://docs.google.com/spreadsheets/d/1j-1C5fcGCxZCT2ZsgQKOxkyEjNsNeYChsTvzxQWpgvE/edit#gid=0')
    print('Ss openned.')

    now = datetime.now()
    now_str = now.strftime('%Y-%m-%d')

    new_data = get_data(now_str)

    ws = ss.worksheet_by_title('Asia Store History')
    df = ws.get_as_df()

    print('Inserting data.')
    if now_str in df['Date'].unique():
        df = df[df['Date'] != now_str]
        df_new_data = pd.DataFrame(new_data, columns=df.columns)
        df_new_data = df_new_data.replace([np.inf, -np.inf], 0)
        df = pd.concat([df_new_data, df])
        print(f'Updating {len(new_data)} rows.')
        ws.set_dataframe(
            df,
            'A1'
        )

    else:
        df_new_data = pd.DataFrame(new_data, columns=df.columns)
        df_new_data = df_new_data.replace([np.inf, -np.inf], 0)
        print(f'Inserting {len(new_data)} rows.')
        ws.insert_rows(
            1,
            len(df_new_data),
            df_new_data.values.tolist(),
        )

    print('Success!')
    return 'Success!', 200
