from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.utils import allowed_file


class ProjectForm(FlaskForm):
    name = StringField(
        "Proje Adı",
        validators=[
            DataRequired(message="Proje adı zorunludur."),
            Length(max=128, message="Proje adı en fazla 128 karakter olabilir."),
        ],
    )
    description = TextAreaField(
        "Açıklama",
        validators=[
            Optional(),
            Length(max=512, message="Açıklama en fazla 512 karakter olabilir."),
        ],
    )
    files = MultipleFileField("Proje Dosyaları")
    submit = SubmitField("Proje Oluştur")

    def validate_files(self, field):
        if not field.data:
            raise ValidationError("En az bir dosya yüklemelisiniz.")

        for file_storage in field.data:
            if not file_storage or not file_storage.filename:
                raise ValidationError("Boş dosya yüklenemez.")

            if not allowed_file(file_storage.filename):
                raise ValidationError(
                    f"İzin verilmeyen dosya türü: {file_storage.filename}"
                )
