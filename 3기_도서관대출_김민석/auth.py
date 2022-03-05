from datetime import date

from email_validator import EmailNotValidError, validate_email
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.security import check_password_hash, generate_password_hash

from db_connect import db
from models import User

from . import login_manager

bp = Blueprint("auth", __name__, url_prefix="/")


@login_manager.user_loader
def load_user(user_email):
    return User.query.filter_by(user_email=user_email).first()


@bp.route("/", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        flash("이미 로그인 된 유저입니다. 메인페이지로 이동합니다.")
        return redirect(url_for("main.home"))

    if request.method == "POST":
        user_email = request.form.get("email", None)
        pw = request.form.get("password", None)

        if user_email is None:
            flash("아이디(이메일)가 입력되지 않았습니다.")
            return render_template("login.html")
        else:
            try:
                validate_email(user_email)
            except EmailNotValidError:
                flash("이메일 형식이 아닙니다.")
                return render_template("login.html")

        if pw is None:
            flash("패스워드(암호)를 입력하지 않았습니다.")
            return render_template("login.html")

        if len(pw) < 8:
            flash("패스워드는 최소 8글자 이상 입력해주세요.")
            return render_template("login.html")

        user = User.query.filter_by(user_email=user_email).first()

        if user is None:
            flash("등록되지 않은 계정입니다.")
            return render_template("login.html")
        elif not check_password_hash(user.pw, pw):
            flash("비밀번호가 틀렸습니다.")
        else:
            login_user(user)
            login_manager.login_message = "로그인 성공!"
            return redirect(url_for("main.home"))
            # 원래는 redirect로 구현했는데 위에 prefix로 user를 해놔서 이걸 해제시키고 해야함. 방법 강구해보기.
    return render_template("login.html")


@bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form.get("username", None)
        user_email = request.form.get("user_email", None)
        password1 = request.form.get("password1", None)
        password2 = request.form.get("password2", None)

        if user_email is None:
            flash("이메일을 입력해주세요")
            return render_template("register.html")
        else:
            try:
                validate_email(user_email)
            except EmailNotValidError:
                flash("이메일 형식이 아닙니다.")
                return render_template("register.html")

        special_char = "`~!@#$%^&*()_+|\\}{[]\":;'?><,./"

        if username is None:
            flash("이름을 입력해주세요")
            return render_template("register.html")

        if (
            username is not None
            and any(char.isdigit() for char in username)
            or any(char in special_char for char in username)
        ):
            flash("이름은 한글 또는 영문만 작성 가능합니다.")
            return render_template("register.html")

        if password1 is None or password2 is None:
            flash("비밀번호를 입력해주세요")
            return render_template("register.html")
        if password1 != password2:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template("register.html")
        if len(password1) < 8:
            flash("password는 8자 이상이여야합니다.")
            return render_template("register.html")

        if not any(char.isdigit() for char in password1):
            flash("숫자가 포함되어야합니다.")
            return render_template("register.html")

        if not any(char in special_char for char in password1):
            flash("특수문자가 포함되어야합니다.")
            return render_template("register.html")

        user = User.query.filter_by(user_email=user_email).first()

        if user is not None:
            flash("이미 존재하는 유저입니다.")
            return render_template("register.html")

        user = User(
            user_email=user_email,
            pw=generate_password_hash(password1),
            username=username,
        )
        db.session.add(user)
        db.session.commit()
        flash("회원가입 성공")
        return redirect("/")
    return render_template("register.html")


@bp.route("/logout")
def logout():
    logout_user()
    # session.clear()
    return redirect("/")
