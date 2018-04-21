from flask import Flask, g, render_template, flash, redirect, url_for, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import check_password_hash

import forms
import models

app = Flask(__name__)
app.secret_key = '08\x9d\xbd-.\r \xa9\xf6\xea\t|\xdd\xbf\x07\x19\x95\x18\x91\x92\xf0r\x8e'

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'


@loginManager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """connect to the database before each request"""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """close the database connection after each request"""
    g.db.close()
    return response


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    articles = models.Article.select()
    return render_template('articles.html', articles=articles)


@app.route('/article/<string:id>/')
def article(id):
    article = models.Article.select().where(models.Article.id == id).get()
    return render_template('article.html', article=article)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered successfully! Please login.", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash('Your email or password does not match!', 'danger')
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Your email or password does not match!', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come back soon!", "success")
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    articles = models.Article.select()
    if articles:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = "No article found!"
        return render_template('dashboard.html', msg=msg)


@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    form = forms.ArticleForm()
    if form.validate_on_submit():
        models.Article.create(author=current_user.username,
                              title=form.title.data, body=form.body.data)
        flash("Article posted!", "success")
        return redirect(url_for('dashboard'))
    return render_template('add_article.html', form=form)


@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@login_required
def edit_article(id):
    article = models.Article.select().where(models.Article.id == id).get()
    form = forms.ArticleForm()
    form.title.data = article.title
    form.body.data = article.body

    if form.validate_on_submit():
        models.Article.update(title=request.form['title'],
                              body=request.form['body']).where(models.Article.id == id).execute()
        flash("Article updated!", "success")
        return redirect(url_for('dashboard'))
    return render_template('edit_article.html', form=form)


@app.route('/delete_article/<string:id>')
@login_required
def delete_article(id):
    models.Article.get(models.Article.id == id).delete_instance()
    flash("Article Deleted", "success")
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    models.initialize()
    app.run(debug=True)
