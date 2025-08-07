import os

from flask import render_template, redirect, url_for, request, current_app, Blueprint, jsonify, json
from marshmallow import ValidationError
from werkzeug.utils import secure_filename

from app import db
from app.models import Record
from app.schemas import FileRecordSchema

bp = Blueprint('main', __name__, template_folder='templates')


@bp.route('/', methods=['GET'])
def index():
    records = Record.query.all()
    return render_template('index.html', records=records)


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.json'):
        return "Недопустимый файл. Требуется JSON файл.", 400

    raw = file.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return " Не верный JSON файл", 400

    schema = FileRecordSchema(many=True)
    try:
        items = schema.load(data)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400

    # Сохраняем.
    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    with open(save_path, 'wb') as f:
        f.write(raw)

    # Сохраняем в БД
    for rec in items:
        r = Record(name=rec['name'], date=rec['date'])
        db.session.add(r)
    db.session.commit()

    return redirect(url_for('main.upload_success', name=filename))


@bp.route('/upload/success', methods=['GET'])
def upload_success():
    name = request.args.get('name', '')
    return f'Файл {name} успешно загружен!'
