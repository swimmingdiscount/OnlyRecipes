from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, current_app as app
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, RecipeRequest, RecipeReply, recipe_ingredients, Ingredient
from app.forms import LoginForm, RegistrationForm, RecipeRequestForm, RecipeReplyForm

bp = Blueprint('main', __name__)  # 'main' is the name of your blueprint

@bp.route('/')
def root():
    return render_template('index.html')  # Render the home page directly

@bp.route('/home')
def home():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/account')
@login_required
def account():
    return render_template('account.html')

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# RECIPE REQUESTS

@bp.route('/create_recipe_request', methods=['POST'])
@login_required
def create_recipe_request():
    form = RecipeRequestForm()
    if form.validate_on_submit():
        recipe_request = RecipeRequest(
            title=form.title.data,
            description=form.description.data,
            meal_type=form.meal_type.data,
            user_id=current_user.id
        )
        db.session.add(recipe_request)
        db.session.commit()
        flash('Your recipe request has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_recipe_request.html', title='New Recipe Request', form=form)

@bp.route('/update_recipe_request/<int:id>', methods=['GET', 'POST'])
@login_required
def update_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.author != current_user:
        abort(403)
    form = RecipeRequestForm()
    if form.validate_on_submit():
        recipe_request.title = form.title.data
        recipe_request.description = form.description.data
        recipe_request.meal_type = form.meal_type.data
        db.session.commit()
        flash('Your recipe request has been updated!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.title.data = recipe_request.title
        form.description.data = recipe_request.description
        form.meal_type.data = recipe_request.meal_type
    return render_template('create_recipe_request.html', title='Update Recipe Request', form=form)

@bp.route('/delete_recipe_request/<int:id>', methods=['POST'])
@login_required
def delete_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.author != current_user:
        abort(403)
    db.session.delete(recipe_request)
    db.session.commit()
    flash('Your recipe request has been deleted!', 'success')
    return redirect(url_for('main.home'))

# RECIPE REPLIES

@bp.route('/create-reply/<int:request_id>', methods=['GET', 'POST'])
@login_required
def create_reply(request_id):
    form = RecipeReplyForm()
    if form.validate_on_submit():
        reply = RecipeReply(
            content=form.content.data,
            request_id=request_id,
            author=current_user
        )
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been posted!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_reply.html', title='New Reply', form=form)

@bp.route('/update-reply/<int:id>', methods=['GET', 'POST'])
@login_required
def update_reply(id):
    reply = RecipeReply.query.get_or_404(id)
    if reply.author != current_user:
        abort(403)
    form = RecipeReplyForm()
    if form.validate_on_submit():
        reply.content = form.content.data
        db.session.commit()
        flash('Your reply has been updated!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.content.data = reply.content
    return render_template('update_reply.html', title='Update Reply', form=form)

@bp.route('/delete-reply/<int:id>', methods=['POST'])
@login_required
def delete_reply(id):
    reply = RecipeReply.query.get_or_404(id)
    if reply.author != current_user:
        abort(403)
    db.session.delete(reply)
    db.session.commit()
    flash('Your reply has been deleted!', 'success')
    return redirect(url_for('main.home'))

# SEARCH

@bp.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.args.get('search_query', '')
        meal_type = request.args.get('meal_type', '')
        search_query = request.form.get('search_query', '')
        return redirect(url_for('main.search', search_query=search_query))
    else:
        search_query = request.form.get('search_query', '')
        meal_type = request.form.get('meal_type', '')
        if search_query:
            search_terms = [term.strip() for term in search_query.split(',')]
            matching_requests = RecipeRequest.query \
                .join(recipe_ingredients) \
                .join(Ingredient) \
                .filter(Ingredient.name.in_(search_terms)) \
                .group_by(RecipeRequest.id) \
                .order_by(db.func.count(Ingredient.id).desc()) \
                .all()
        else:
            matching_requests = []

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Partial refresh: Return JSON response
            return jsonify({
            'requests': [{
                'title': request.title,
                'description': request.description,
                'ingredients': [ingredient.name for ingredient in request.ingredients],
                'url': url_for('main.recipe_requests', id=request.id)  # Replace with actual URL
            } for request in matching_requests]
        })
        else:
        # Full page refresh: Render HTML template
            return render_template('index.html', requests=matching_requests)