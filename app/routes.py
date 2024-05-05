from flask import render_template, url_for, flash, redirect, request, jsonify, Flask
from app import app, db
from app.models import User, RecipeRequest, Ingredient, recipe_ingredients, db
from app.forms import LoginForm, RegistrationForm, RecipeRequestForm
from flask_login import login_user, logout_user, current_user, login_required

@app.route('/home')
def home():
  return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redirect to home if already logged in
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # Redirect to home if already logged in
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

#
#RECIPE REQUESTS
#

@app.route('/create_recipe_request', methods=['POST'])
def create_recipe_request():
    data = request.json
    
    # Validate that all required fields are present
    if 'title' not in data or 'description' not in data or 'meal_type' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate the meal_type field
    meal_type = data.get('meal_type', 'other')
    valid_meal_types = ['breakfast', 'lunch', 'dinner', 'snack']
    if meal_type not in valid_meal_types:
        meal_type = 'other'

    # Create a new RecipeRequest object and insert it into the database
    recipe_request = RecipeRequest(
        title=data['title'],
        description=data['description'],
        meal_type=data['meal_type'],
        user_id=current_user.id  # Assuming you have a current_user object
    )
    db.session.add(recipe_request)
    db.session.commit()

    return jsonify({'message': 'Recipe request created successfully'}), 200
@app.route('/recipe-requests')
def recipe_requests():
    query = request.args.get('query', '')  # Get the search keyword from the query parameters
    meal_type = request.args.get('meal_type', '')  # Get meal type if specified

    if meal_type:
        requests = RecipeRequest.query.filter(RecipeRequest.meal_type == meal_type)
    else:
        requests = RecipeRequest.query.all()

    if query:
        requests = requests.filter(RecipeRequest.title.like(f'%{query}%') | RecipeRequest.description.like(f'%{query}%'))

    return render_template('find_requests.html', requests=requests)
@app.route('/update-recipe-request/<int:id>', methods=['GET', 'POST'])
@login_required
def update_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.author != current_user:
        abort(403)  # Forbidden access if not the author
    form = RecipeRequestForm()
    if form.validate_on_submit():
        recipe_request.title = form.title.data
        recipe_request.description = form.description.data
        recipe_request.meal_type = form.meal_type.data
        db.session.commit()
        flash('Your recipe request has been updated!', 'success')
        return redirect(url_for('recipe_requests'))
    elif request.method == 'GET':
        form.title.data = recipe_request.title
        form.description.data = recipe_request.description
        form.meal_type.data = recipe_request.meal_type
    return render_template('create_recipe_request.html', title='Update Recipe Request', form=form)
@app.route('/delete-recipe-request/<int:id>', methods=['POST'])
@login_required
def delete_recipe_request(id):
    recipe_request = RecipeRequest.query.get_or_404(id)
    if recipe_request.author != current_user:
        abort(403)
    db.session.delete(recipe_request)
    db.session.commit()
    flash('Your recipe request has been deleted!', 'success')
    return redirect(url_for('recipe_requests'))

#
#RECIPE REPLIES
#

@app.route('/create-reply/<int:request_id>', methods=['GET', 'POST'])
@login_required
def create_reply(request_id):
    form = RecipeReplyForm()  
    if form.validate_on_submit():
        reply = RecipeReply(content=form.content.data, request_id=request_id, replier=current_user)
        db.session.add(reply)
        db.session.commit()
        flash('Your reply has been posted!', 'success')
        return redirect(url_for('recipe_requests'))
    return render_template('create_reply.html', title='New Reply', form=form)
@app.route('/update-reply/<int:id>', methods=['GET', 'POST'])
@login_required
def update_reply(id):
    reply = RecipeReply.query.get_or_404(id)
    if reply.replier != current_user:
        abort(403)  # Forbidden access if not the author of the reply
    form = RecipeReplyForm()  
    if form.validate_on_submit():
        reply.content = form.content.data
        db.session.commit()
        flash('Your reply has been updated!', 'success')
        return redirect(url_for('recipe_requests'))  # Redirecting to the list of recipe requests or wherever appropriate
    elif request.method == 'GET':
        form.content.data = reply.content
    return render_template('update_reply.html', title='Update Reply', form=form)
@app.route('/delete-reply/<int:id>', methods=['POST'])
@login_required
def delete_reply(id):
    reply = RecipeReply.query.get_or_404(id)
    if reply.replier != current_user:
        abort(403)
    db.session.delete(reply)
    db.session.commit()
    flash('Your reply has been deleted!', 'success')
    return redirect(url_for('recipe_requests'))  # Redirecting to the list of recipe requests or wherever appropriate

########

@app.route('/search')
def search():
    search_query = request.args.get('ingredient', '')
    if search_query:
        search_terms = search_query.split(',')  # Split search query into individual ingredients
        matching_requests = RecipeRequest.query \
            .join(recipe_ingredients) \
            .join(Ingredient) \
            .filter(Ingredient.name.in_(search_terms)) \
            .group_by(RecipeRequest.id) \
            .order_by(db.func.count(Ingredient.id).desc())  # Order by the count of matching ingredients
        # Execute the query and fetch results
        results = matching_requests.all()
    else:
        results = []

    return render_template('index.html', requests=results, search_query=search_query)
