from flask_babel import lazy_gettext as _l
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        _l("Kullanıcı Adı"),
        validators=[DataRequired(message=_l("Kullanıcı adı zorunludur.")), Length(min=3, max=32)],
    )
    email = StringField(
        _l("E-posta"),
        validators=[
            DataRequired(message=_l("E-posta zorunludur.")),
            Email(message=_l("Geçerli bir e-posta girin.")),
        ],
    )
    password = PasswordField(
        _l("Şifre"),
        validators=[
            DataRequired(message=_l("Şifre zorunludur.")),
            Length(min=6, message=_l("Şifre en az 6 karakter olmalıdır.")),
        ],
    )
    password2 = PasswordField(
        _l("Şifre Tekrar"),
        validators=[
            DataRequired(message=_l("Şifre tekrarı zorunludur.")),
            EqualTo("password", message=_l("Şifreler eşleşmiyor.")),
        ],
    )
    submit = SubmitField(_l("Kayıt Ol"))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(_l("Bu e-posta adresi zaten kayıtlı."))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(_l("Bu kullanıcı adı zaten alınmış."))


class LoginForm(FlaskForm):
    email = StringField(
        _l("E-posta"),
        validators=[
            DataRequired(message=_l("E-posta zorunludur.")),
            Email(message=_l("Geçerli bir e-posta girin.")),
        ],
    )
    password = PasswordField(
        _l("Şifre"),
        validators=[DataRequired(message=_l("Şifre zorunludur."))],
    )
    remember_me = BooleanField(_l("Beni hatırla"))
    submit = SubmitField(_l("Giriş Yap"))


class ProfileForm(FlaskForm):
    bio = TextAreaField(
        _l("Hakkımda"),
        validators=[
            Optional(),
            Length(max=256, message=_l("Bio en fazla 256 karakter olabilir.")),
        ],
    )
    submit = SubmitField(_l("Profili Kaydet"))


class AvatarForm(FlaskForm):
    avatar = FileField(
        _l("Avatar"),
        validators=[
            FileRequired(message=_l("Avatar dosyası seçmelisiniz.")),
            FileAllowed(
                ["png", "jpg", "jpeg", "gif", "webp"],
                message=_l("Geçersiz format. İzin verilen: png, jpg, jpeg, gif, webp."),
            ),
        ],
    )
    submit = SubmitField(_l("Avatar Yükle"))

    def validate_avatar(self, field):
        if not field.data or not field.data.filename:
            return

        from flask import current_app

        max_bytes = current_app.config.get("AVATAR_MAX_BYTES", 2 * 1024 * 1024)
        field.data.stream.seek(0, 2)
        size = field.data.stream.tell()
        field.data.stream.seek(0)
        if size > max_bytes:
            raise ValidationError(_l("Avatar dosyası en fazla 2 MB olabilir."))
