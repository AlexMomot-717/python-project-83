import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from page_analyzer.utils.db import (
    create_check,
    create_url,
    get_checks_data,
    get_url_by_name,
    get_url_context,
    get_urls_data,
)
from page_analyzer.utils.url import normalize, validate

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.route("/urls", methods=["POST"])
def add_url() -> Any:
    url_name = request.form["url"]
    errors = validate(url_name)
    if errors:
        flash(errors["name"], "danger")
        return render_template("index.html", url_name=url_name), 422
    url_name = normalize(url_name)
    url_id = get_url_by_name(url_name)
    if url_id:
        flash("Страница уже существует", "info")
        return redirect(url_for("show_url", id=url_id))
    url_id = create_url(url_name)
    flash("Страница успешно добавлена", "success")
    return redirect(url_for("show_url", id=url_id), code=302)


@app.route("/urls/<int:id>")
def show_url(id: int) -> str:
    url_data = get_url_context(id)
    if not url_data:
        return render_template("page_not_found.html")
    checks = get_checks_data(id)
    return render_template("url.html", url=url_data, checks=checks)


@app.route("/urls")
def list_urls() -> str:
    urls_data_list = get_urls_data()
    return render_template(
        "urls.html",
        urls=urls_data_list,
    )


@app.route("/urls/<int:id>/checks", methods=["POST"])
def add_url_check(id: int) -> Any:
    check_context = create_check(id)
    if not check_context:
        flash("Произошла ошибка при проверке", "danger")
    else:
        flash("Страница успешно проверена", "success")
    return redirect(url_for("show_url", id=id))
