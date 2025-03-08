from flask import Flask, render_template, request, send_from_directory, redirect, abort
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired
from wtforms import FileField, ValidationError, StringField
from PIL import Image
import json
import re
import os
import subprocess

from utils.system_manager import add_wifi_nmcli


app = Flask('weather')
app.config['SECRET_KEY'] = os.urandom(24)


class NewPhotoForm(FlaskForm):
    file = FileField('Plik obrazu', validators=[FileRequired()])

    @staticmethod
    def validate_file(form, field):
        if not re.match(r'.+\.(jpg|jpeg|bmp|png|tiff)', field.data.filename):
            raise ValidationError('Dozwolone typy plików to: jpg, bmp, tiff i png')
        else:
            return True
        

class RemovePhotoForm(FlaskForm):
    file_name = StringField('Nazwa pliku do usuniecia')


@app.route('/')
def home_view():
    return render_template('index.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings_view():
    if request.method == 'POST':
        data = request.form
        if "update" in data:
            subprocess.Popen(["python3", "weather_station.py", "screen"])
        elif "clear" in data:
            subprocess.Popen(["python3", "weather_station.py", "clear"])

    return render_template('settings.html')

@app.route('/photos', methods=['GET', 'POST'])
def photos_view():
    new_photo_form = NewPhotoForm()
    remove_photo_form = RemovePhotoForm()

    photo_dir = os.path.join(os.path.curdir, 'photos')
    ACTIVE_IMG_FILENAME = 'active_images.json'

    # Read active images
    active_imgs_path = os.path.join(photo_dir, ACTIVE_IMG_FILENAME)
    if os.path.exists(active_imgs_path):
        with open(active_imgs_path) as file:
            active_images = json.load(file)
    else:
        active_images = []

    if request.method == 'POST':
        if 'new-photo-form' in request.form and new_photo_form.validate_on_submit():
            file = new_photo_form.data['file']
            img = Image.open(file)
            new_height = 240
            new_width = int(round(img.size[0] * 240 / img.size[1]))
            img = img.resize((new_width, new_height))
            img.save(os.path.join(photo_dir, file.filename))
            if file.filename not in active_images: active_images.append(file.filename)

        if 'remove-photo-form' in request.form:
            file_name = remove_photo_form.data['file_name']
            file_path = os.path.join(photo_dir, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                if file_name in active_images: active_images.remove(file_name)

        if 'activation-image' in request.form:
            img_name = request.form['image_name']
            if 'active' in request.form:
                active_images.append(img_name)
            else:
                if img_name in active_images: active_images.remove(img_name)

        if 'active-all' in request.form:
            active_images = [file for file in os.listdir(photo_dir) if ".json" not in file]

        if 'deactive-all' in request.form:
            active_images = []

        # Save active images
        with open(os.path.join(photo_dir, ACTIVE_IMG_FILENAME), 'w') as file:
            file.write(json.dumps(active_images))

    # Find all files in photos dir
    photos = [filename for filename in os.listdir(photo_dir) if filename != ACTIVE_IMG_FILENAME]

    data = {
        'photos': photos,
        'active_images': active_images,
        'new_photo_form': new_photo_form,
        'remove_photo_form': remove_photo_form,
    }

    return render_template('photos.html', data=data)


@app.route('/photos/<path:filename>')
def send_photo(filename):
    return send_from_directory('photos', filename, as_attachment=True)


@app.route('/result_image.bmp')
def send_result_image():
    return send_from_directory('.', 'result_image.bmp', as_attachment=True)


@app.route('/add_wifi', methods=['POST'])
def add_wifi():
    ssid = request.form.get('ssid')
    password = request.form.get('password')

    if not ssid or not password:
        return "SSID and password are required", 400

    try:
        result, error = add_wifi_nmcli(ssid, password)
        if result == 0:
            return redirect('/settings')
        else:
            raise abort(500, error)
    except Exception as e:
        raise abort(500, e)
    

@app.route('/shutdown', methods=['POST'])
def shutdown():
    try:
        os.system('sudo shutdown now')
        return "Shutting down...", 200
    except Exception as e:
        return f"Error: {str(e)}", 500
    

@app.route('/restart', methods=['POST'])
def restart():
    try:
        os.system('sudo reboot')
        return "Restarting...", 200
    except Exception as e:
        return f"Error: {str(e)}", 500




if __name__ == '__main__':
    app.run('127.0.0.1')