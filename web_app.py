from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
import os
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

@app.route('/photos')
def photos_view():
    # Find all files in photos dir
    dir = os.path.join(os.path.curdir, 'photos')
    photos = [filename for filename in os.listdir(dir)]

    data = {
        'photos': photos,
    }

    return render_template('photos.html', data=data)

@app.route('/photos/<path:filename>')
def send_photo(filename):
    return send_from_directory('photos', filename, as_attachment=True)


if __name__ == '__main__':
    app.run('localhost')