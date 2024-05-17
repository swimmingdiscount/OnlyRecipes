from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, render_template_string
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, RecipeRequest, RecipeReply, recipe_ingredients, Ingredient, Recipe
from app.forms import LoginForm, RegistrationForm, RecipeRequestForm, RecipeReplyForm, UpdateAccountForm, RecipeForm
from datetime import datetime

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
    # Fetch user's recipe requests and replies
    recipe_requests = get_user_recipe_requests(current_user)
    recipe_replies = get_user_recipe_replies(current_user)
    return render_template('account.html', recipe_requests=recipe_requests, recipe_replies=recipe_replies, active_tab='main')

@bp.route('/account/security')
@login_required
def account_security():
    # Create and populate form with current user's data
    form = UpdateAccountForm()
    form.username.data = current_user.username
    form.email.data = current_user.email
    return render_template('partials/account_security.html', form=form, active_tab='security')

@bp.route('/account/security/update', methods=['POST'])
@login_required
def update_security():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        if user and user.check_password(form.current_password.data):
            current_user.username = form.username.data
            current_user.email = form.email.data
            if form.new_password.data:
                current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('main.account'))
        else:
            flash('Current password is incorrect.', 'danger')
    # Fetch user's recipe requests and replies again to display them in the account.html template
    recipe_requests = get_user_recipe_requests(current_user)
    recipe_replies = get_user_recipe_replies(current_user)
    return render_template('account.html', recipe_requests=recipe_requests, recipe_replies=recipe_replies, form=form, active_tab='security')

def get_user_recipe_requests(user):
    return RecipeRequest.query.filter_by(user_id=user.id).all()

def get_user_recipe_replies(user):
    return RecipeReply.query.filter_by(user_id=user.id).all()

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))

# RECIPE REQUESTS

@bp.route('/create_recipe_request', methods=['GET', 'POST'])
@login_required
def create_recipe_request():
    form = RecipeRequestForm()
    if request.method == 'POST' and form.validate_on_submit():
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
    return render_template('create_requests.html', title='New Recipe Request', form=form)

@bp.route('/update_recipe_request/<int:id>', methods=['GET', 'POST'])
@login_required
def update_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.user_id != current_user.id:
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
    return render_template('create_requests.html', title='Update Recipe Request', form=form)

@bp.route('/delete_recipe_request/<int:id>', methods=['POST'])
@login_required
def delete_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.user_id != current_user.id:
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
            user_id=current_user.id
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
    if reply.user_id != current_user.id:
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
    if reply.user_id != current_user.id:
        abort(403)
    db.session.delete(reply)
    db.session.commit()
    flash('Your reply has been deleted!', 'success')
    return redirect(url_for('main.home'))

# SEARCH

@bp.route('/search', methods=['GET', 'POST'])
def search():
    search_query = request.args.get('search_query', '')
    meal_type = request.args.get('meal_type', '')

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
        # Partial refresh: Generate HTML string
        rendered_html = render_template_string(
            """
            {% for request in requests %}
            <li class="list-group-item">
                <h5>{{ request.title }}</h5>
                <p>{{ request.description }}</p>
                <a href="{{ url_for('main.view_request', id=request.id) }}" class="btn btn-info">View Details</a>
            </li>
            {% else %}
            <li class="list-group-item">No recipe requests found.</li>
            {% endfor %}
            """,
            requests=matching_requests
        )
        return jsonify({
            'html': rendered_html,
            'search_query': search_query,
            'meal_type': meal_type
        })
    else:
        return render_template('search_results.html', requests=matching_requests, search_query=search_query, meal_type=meal_type)

@bp.route('/view_request/<int:id>')
@login_required
def view_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    return render_template('view_request.html', recipe_request=recipe_request)

@bp.route('/add_recipe', methods=['GET', 'POST'])
@login_required
def add_recipe():
    form = RecipeForm()
    if form.validate_on_submit():
        new_recipe = Recipe(
            title=form.title.data,
            ingredients=form.ingredients.data,
            instructions=form.instructions.data,
            created_at=datetime.utcnow(),  # Automatically set the created_at time
            user_id=current_user.id  
        )
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe added successfully!', 'success')
        return redirect(url_for('main.home'))  # Redirect to the main page or any other page

    return render_template('add_recipe.html', form=form)