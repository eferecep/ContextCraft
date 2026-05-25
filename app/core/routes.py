from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Project
from app.utils import delete_project_files, list_project_files, save_uploaded_file

from . import core_bp
from .forms import ProjectForm


def _get_user_project(project_id: int) -> Project:
    project = db.session.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        abort(404)
    return project


@core_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def project_new():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data or None,
            owner_id=current_user.id,
            status="pending",
        )
        db.session.add(project)
        db.session.flush()

        source_path = None
        try:
            for file_storage in form.files.data:
                source_path = save_uploaded_file(
                    file_storage,
                    current_user.id,
                    project.id,
                )

            project.source_path = source_path
            db.session.commit()
            flash(f"'{project.name}' projesi başarıyla oluşturuldu.", "success")
            return redirect(url_for("core.project_list"))

        except ValueError as exc:
            db.session.rollback()
            if source_path:
                delete_project_files(source_path)
            flash(str(exc), "danger")

        except OSError:
            db.session.rollback()
            if source_path:
                delete_project_files(source_path)
            flash("Dosyalar kaydedilirken bir hata oluştu.", "danger")

    return render_template("core/project_form.html", form=form)


@core_bp.route("/projects")
@login_required
def project_list():
    projects = (
        Project.query.filter_by(owner_id=current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return render_template("core/project_list.html", projects=projects)


@core_bp.route("/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = _get_user_project(project_id)
    files = list_project_files(project.source_path or "")
    return render_template(
        "core/project_detail.html",
        project=project,
        files=files,
    )


@core_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def project_delete(project_id):
    project = _get_user_project(project_id)
    project_name = project.name

    if project.source_path:
        delete_project_files(project.source_path)

    db.session.delete(project)
    db.session.commit()
    flash(f"'{project_name}' projesi silindi.", "info")
    return redirect(url_for("core.project_list"))
