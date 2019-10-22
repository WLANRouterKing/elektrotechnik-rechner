import os
from flask import Flask, request, render_template, redirect
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from response import Response
from system import System
from encryption import Encryption
from user import User
from loginform import LoginForm

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)
csrf = CSRFProtect()
login_manager = LoginManager()
csrf.init_app(app)
login_manager.init_app(app)

system = System()
encryption = Encryption()

if not system.file_exists("sym.key"):
    encryption.setup_sym_key()
if not system.file_exists("priv.key") or not system.file_exists("pub.key"):
    encryption.setup_async_keys()


@app.route('/server_public_key', methods=["POST"])
def server_public_key():
    public_key = system.read_file("pub.key")
    response = Response()
    response.set("public_key", encryption.as_base_64(public_key))
    return response.get_json_response()


@app.route('/backend', methods=["POST", "GET"])
def backend():
    form = LoginForm()
    if request.method == "GET":
        return render_template("/backend/login.html", form=form)
    if request.method == "POST":
        print("test")
        if form.validate_on_submit():
            user = User()
            username = form.username.data
            id = user.get_user_id_by_name(username)
            password = form.password.data
            if id > 0:
                if user.create_instance_by_user_id(id):
                    if user.validate_login(password):
                        if login_user(user):
                            return redirect("/backend/dashboard", current_user=current_user())
    return render_template("/backend/login.html", form=form, message="Login nicht erfolgreich")


@app.route("/backend/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("/backend/dashboard.html")


@app.route("/test", methods=["GET"])
def test():
    user = User()
    user.set("id", 1)
    user.load()
    return user.get_json_response()


@app.route("/backend/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return redirect("/backend")


@login_manager.user_loader
def load_user(user_id):
    if user_id != "":
        user = User()
        user.set("id", user_id)
        user.load()
        return user
    else:
        return None


if __name__ == '__main__':
    app.run()
