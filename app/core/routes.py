from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Project
from app.services.llamaindex_service import IndexBuildError, build_project_index
from app.services.prompt_optimizer import PromptOptimizeError, optimize_prompt
from app.utils import delete_project_files, delete_storage_dir, list_project_files, save_uploaded_file

from . import core_bp
from .forms import ProjectForm, PromptForm


def _get_user_project(project_id: int) -> Project:
    project = db.session.get(Project, project_id)
    if project is None or project.owner_id != current_user.id:
        abort(404)
    return project


def _render_project_detail(project, prompt_form=None, result=None):
    files = list_project_files(project.source_path or "")
    if prompt_form is None and project.status == "indexed":
        prompt_form = PromptForm()
    return render_template(
        "core/project_detail.html",
        project=project,
        files=files,
        prompt_form=prompt_form,
        result=result,
    )


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
    return _render_project_detail(project)


@core_bp.route("/projects/<int:project_id>/optimize", methods=["POST"])
@login_required
def project_optimize(project_id):
    project = _get_user_project(project_id)

    if project.status != "indexed":
        flash("Prompt oluşturmak için önce projeyi indeksleyin.", "danger")
        return redirect(url_for("core.project_detail", project_id=project.id))

    form = PromptForm()
    if not form.validate_on_submit():
        return _render_project_detail(project, prompt_form=form)

    try:
        result = optimize_prompt(project, form.prompt.data)
        flash("Prompt başarıyla oluşturuldu.", "success")
        return _render_project_detail(project, prompt_form=form, result=result)
    except PromptOptimizeError as exc:
        flash(str(exc), "danger")
        return _render_project_detail(project, prompt_form=form)
    except Exception as exc:
        flash(f"Prompt oluşturma hatası: {exc}", "danger")
        return _render_project_detail(project, prompt_form=form)


@core_bp.route("/projects/<int:project_id>/index", methods=["POST"])
@login_required
def project_index(project_id):
    project = _get_user_project(project_id)

    if not project.source_path:
        flash("İndekslenecek dosya bulunamadı.", "danger")
        return redirect(url_for("core.project_detail", project_id=project.id))

    if project.status == "indexing":
        flash("İndeksleme zaten devam ediyor.", "info")
        return redirect(url_for("core.project_detail", project_id=project.id))

    project.status = "indexing"
    db.session.commit()

    try:
        node_count = build_project_index(project)
        project.status = "indexed"
        db.session.commit()
        flash(
            f"'{project.name}' indekslendi ({node_count} parça).",
            "success",
        )
    except IndexBuildError as exc:
        db.session.rollback()
        project.status = "failed"
        db.session.commit()
        flash(str(exc), "danger")
    except Exception as exc:
        db.session.rollback()
        project.status = "failed"
        db.session.commit()
        flash(f"İndeksleme hatası: {exc}", "danger")

    return redirect(url_for("core.project_detail", project_id=project.id))


@core_bp.route("/projects/<int:project_id>/delete", methods=["POST"])
@login_required
def project_delete(project_id):
    project = _get_user_project(project_id)
    project_name = project.name

    if project.source_path:
        delete_project_files(project.source_path)

    delete_storage_dir(project.owner_id, project.id)

    db.session.delete(project)
    db.session.commit()
    flash(f"'{project_name}' projesi silindi.", "info")
    return redirect(url_for("core.project_list"))
