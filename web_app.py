from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField, validators, ValidationError, StringField
from PIL import Image
import re
import os
import weather_station

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
        weather_station.main('screen')

    return render_template('settings.html')

@app.route('/photos', methods=['GET', 'POST'])
def photos_view():
    new_photo_form = NewPhotoForm()
    remove_photo_form = RemovePhotoForm()

    photo_dir = os.path.join(os.path.curdir, 'photos')

    if request.method == 'POST':
        if 'new-photo-form' in request.form and new_photo_form.validate_on_submit():
            file = new_photo_form.data['file']
            img = Image.open(file)
            new_height = 240
            new_width = int(round(img.size[0] * 240 / img.size[1]))
            img = img.resize((new_width, new_height))
            img.save(os.path.join(photo_dir, file.filename))

        if 'remove-photo-form' in request.form:
            file_name = remove_photo_form.data['file_name']
            file_path = os.path.join(photo_dir, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)

    # Find all files in photos dir
    photos = [filename for filename in os.listdir(photo_dir)]

    data = {
        'photos': photos,
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


if __name__ == '__main__':
    app.run('localhost')