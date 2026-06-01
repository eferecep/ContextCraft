from flask import abort, flash, redirect, render_template, request, send_file, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import db
from app.models import Project, User
from app.utils.avatar_helpers import delete_avatar_files, get_avatar_absolute_path, save_avatar

from . import auth_bp
from .forms import AvatarForm, LoginForm, ProfileForm, RegisterForm


def _render_profile(profile_form=None, avatar_form=None):
    if profile_form is None:
        profile_form = ProfileForm()
        profile_form.bio.data = current_user.bio or ""
    if avatar_form is None:
        avatar_form = AvatarForm()

    project_count = Project.query.filter_by(owner_id=current_user.id).count()
    avatar_url = (
        url_for("auth.serve_avatar", user_id=current_user.id)
        if current_user.has_avatar
        else None
    )

    return render_template(
        "auth/profile.html",
        profile_form=profile_form,
        avatar_form=avatar_form,
        project_count=project_count,
        avatar_url=avatar_url,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_("Kayıt başarılı! Giriş yapabilirsiniz."), "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(_("E-posta veya şifre hatalı."), "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        flash(_("Hoş geldiniz, %(username)s!", username=user.username), "success")

        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("main.index")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash(_("Başarıyla çıkış yaptınız."), "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm()
    avatar_form = AvatarForm()

    if profile_form.validate_on_submit():
        bio = (profile_form.bio.data or "").strip()
        current_user.bio = bio or None
        db.session.commit()
        flash(_("Profiliniz güncellendi."), "success")
        return redirect(url_for("auth.profile"))

    if request.method == "GET":
        profile_form.bio.data = current_user.bio or ""

    return _render_profile(profile_form=profile_form, avatar_form=avatar_form)


@auth_bp.route("/profile/avatar", methods=["POST"])
@login_required
def profile_avatar():
    avatar_form = AvatarForm()
    if avatar_form.validate_on_submit():
        try:
            current_user.avatar_path = save_avatar(
                avatar_form.avatar.data,
                current_user.id,
            )
            db.session.commit()
            flash(_("Avatar yüklendi."), "success")
        except ValueError as exc:
            flash(str(exc), "danger")  # mesaj avatar_helpers'te _l ile üretilir
    else:
        for errors in avatar_form.errors.values():
            for message in errors:
                flash(message, "danger")

    return redirect(url_for("auth.profile"))


@auth_bp.route("/profile/avatar/delete", methods=["POST"])
@login_required
def profile_avatar_delete():
    delete_avatar_files(current_user.id)
    current_user.avatar_path = None
    db.session.commit()
    flash(_("Avatar kaldırıldı."), "info")
    return redirect(url_for("auth.profile"))


@auth_bp.route("/avatars/<int:user_id>")
def serve_avatar(user_id):
    user = db.session.get(User, user_id)
    if user is None or not user.avatar_path:
        abort(404)

    absolute_path = get_avatar_absolute_path(user.avatar_path)
    if absolute_path is None:
        abort(404)

    return send_file(absolute_path)
