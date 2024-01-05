from flask import Flask
from flask import render_template
from flask import request
import weather_station

app = Flask('weather')

@app.route('/')
def home_view():
    return render_template('index.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings_view():
    if request.method == 'POST':
        weather_station.main('screen')

    return render_template('settings.html')


if __name__ == '__main__':
    app.run('localhost')