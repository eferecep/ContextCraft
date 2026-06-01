from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, ValidationError

from app.models import User


class RegisterForm(FlaskForm):
    username = StringField(
        "Kullanıcı Adı",
        validators=[DataRequired(message="Kullanıcı adı zorunludur."), Length(min=3, max=32)],
    )
    email = StringField(
        "E-posta",
        validators=[DataRequired(message="E-posta zorunludur."), Email(message="Geçerli bir e-posta girin.")],
    )
    password = PasswordField(
        "Şifre",
        validators=[DataRequired(message="Şifre zorunludur."), Length(min=6, message="Şifre en az 6 karakter olmalıdır.")],
    )
    password2 = PasswordField(
        "Şifre Tekrar",
        validators=[
            DataRequired(message="Şifre tekrarı zorunludur."),
            EqualTo("password", message="Şifreler eşleşmiyor."),
        ],
    )
    submit = SubmitField("Kayıt Ol")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Bu e-posta adresi zaten kayıtlı.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Bu kullanıcı adı zaten alınmış.")


class LoginForm(FlaskForm):
    email = StringField(
        "E-posta",
        validators=[DataRequired(message="E-posta zorunludur."), Email(message="Geçerli bir e-posta girin.")],
    )
    password = PasswordField(
        "Şifre",
        validators=[DataRequired(message="Şifre zorunludur.")],
    )
    remember_me = BooleanField("Beni hatırla")
    submit = SubmitField("Giriş Yap")


class ProfileForm(FlaskForm):
    bio = TextAreaField(
        "Hakkımda",
        validators=[
            Optional(),
            Length(max=256, message="Bio en fazla 256 karakter olabilir."),
        ],
    )
    submit = SubmitField("Profili Kaydet")


class AvatarForm(FlaskForm):
    avatar = FileField(
        "Avatar",
        validators=[
            FileRequired(message="Avatar dosyası seçmelisiniz."),
            FileAllowed(
                ["png", "jpg", "jpeg", "gif", "webp"],
                message="Geçersiz format. İzin verilen: png, jpg, jpeg, gif, webp.",
            ),
        ],
    )
    submit = SubmitField("Avatar Yükle")

    def validate_avatar(self, field):
        if not field.data or not field.data.filename:
            return

        from flask import current_app

        max_bytes = current_app.config.get("AVATAR_MAX_BYTES", 2 * 1024 * 1024)
        field.data.stream.seek(0, 2)
        size = field.data.stream.tell()
        field.data.stream.seek(0)
        if size > max_bytes:
            raise ValidationError("Avatar dosyası en fazla 2 MB olabilir.")
