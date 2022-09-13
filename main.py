import os
import zipfile
import base64
import io
import shapefile as shp
import matplotlib.pyplot as plt

from flask import Flask, render_template, send_file, request
from flask_wtf import FlaskForm

from werkzeug.utils import secure_filename
from wtforms import FileField

# properties
app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))

upload_folder = "uploads/"
app.config['UPLOAD_FOLDER'] = upload_folder

if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

if not os.path.exists(upload_folder):
    os.mkdir('temp')


class MyForm(FlaskForm):
    file = FileField()


# check type file
def check_file_extension(filename):
    return 'zip' in filename.split('.')[-1]


# if file is zip unzip it
def unzip_if_true(file):
    if '.zip' in file.filename:
        with zipfile.ZipFile(f'uploads/{file.filename}', 'r') as zipObj:
            zipObj.extractall('temp')
    elif '.zip' not in file.filename:
        return '</br><h1>You need upload a .zip</h1>'


# convert plot result to base64
def coloring_map(file):
    sf = shp.Reader(file)
    plt.figure(dpi=1500)
    for shape in sf.shapeRecords():
        x = []
        y = []

        for i in shape.shape.points:
            x.append(i[0])
        for i in shape.shape.points:
            y.append(i[1])

        plt.plot(x, y)
    return convert_in_base64(plt)


def convert_in_base64(plt):
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read())

    return my_base64_jpgData


# convert base64 to png
def base64_in_png(file, filename):
    image_binary = base64.b64decode(file)
    return image_binary


def save_file(path, data,type):
    if type == 'base64':
        type = 'txt'
    with open(path+'.'+type, 'wb') as f:
        f.write(data)


# clear folders
def clear_files():
    for e in os.listdir('temp'):
        os.remove('temp/' + e)
    for e in os.listdir('uploads'):
        os.remove('uploads/' + e)

# send file to user
def send_file_user(file_type,file_name):
    if file_type == 'txt':
        return file_name+'.txt'
    else:
        return file_name+'.png'

# show page to user
@app.route('/')
def render_html():
    types = ['base64', 'png']
    return render_template('sumbit.html', form=MyForm, types=types)


# upload file to convert
@app.route('/upload', methods=['GET', 'POST'])
def uploadfile():
    file = request.files['file']
    file_type = request.form.get('comp_select')

    # check file type and download file local
    if check_file_extension(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        return downloadfile([file, file_type])
    else:
        return 'The file extension is not allowed'


# sending the file to the user
@app.route('/download', methods=['GET', 'POST'])
def downloadfile(list_args):
    file = list_args[0]
    file_type = list_args[1]
    if file_type == 'base64':
        file_type = 'txt'

    # тут в мене питання, який саме файл потрібно відкривати із архіву?
    # якщо це не важливо то я відкриваю 1-ий файл із архіву(я тестив що якщо відкрити будь-який то воно все-одно працює)

    unzip_if_true(file)
    temp_list = os.listdir('temp')
    file_name = f'temp/{temp_list[0].split(".")[0]}'

    file_base64 = coloring_map(file_name)
    file_binary = base64_in_png(file_base64, file_name)

    save_file(file_name, file_base64, type=file_type)
    save_file(file_name, file_binary, type=file_type)

    file_result = send_file_user(file_type, file_name)

    try:
        responce = send_file(file_result, as_attachment=True)
        return responce
    finally:
        clear_files()


