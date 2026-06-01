from flask_babel import gettext as _, lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import MultipleFileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

from app.utils import allowed_file


class ProjectForm(FlaskForm):
    name = StringField(
        _l("Proje Adı"),
        validators=[
            DataRequired(message=_l("Proje adı zorunludur.")),
            Length(max=128, message=_l("Proje adı en fazla 128 karakter olabilir.")),
        ],
    )
    description = TextAreaField(
        _l("Açıklama"),
        validators=[
            Optional(),
            Length(max=512, message=_l("Açıklama en fazla 512 karakter olabilir.")),
        ],
    )
    files = MultipleFileField(_l("Proje Dosyaları"))
    submit = SubmitField(_l("Proje Oluştur"))

    def validate_files(self, field):
        if not field.data:
            raise ValidationError(_l("En az bir dosya yüklemelisiniz."))

        for file_storage in field.data:
            if not file_storage or not file_storage.filename:
                raise ValidationError(_l("Boş dosya yüklenemez."))

            if not allowed_file(file_storage.filename):
                raise ValidationError(
                    _("İzin verilmeyen dosya türü: %(filename)s", filename=file_storage.filename)
                )


class PromptForm(FlaskForm):
    prompt = TextAreaField(
        _l("Prompt"),
        validators=[
            DataRequired(message=_l("Prompt metni zorunludur.")),
            Length(
                min=3,
                max=2000,
                message=_l("Prompt 3 ile 2000 karakter arasında olmalıdır."),
            ),
        ],
    )
    submit = SubmitField(_l("Prompt Oluştur"))
