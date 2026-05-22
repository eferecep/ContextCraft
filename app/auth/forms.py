from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

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
