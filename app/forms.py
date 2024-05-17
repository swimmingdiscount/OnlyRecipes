from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length, Optional
from flask_login import current_user
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already in use. Please choose a different one or login.')

class RecipeRequestForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    meal_type = SelectField('Meal Type', choices=[
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('other', 'Other')
    ], default='other', validators=[DataRequired()])
    submit = SubmitField('Submit')

class RecipeReplyForm(FlaskForm):
    content = TextAreaField('Content', validators=[DataRequired()])
    add_as_recipe = BooleanField('Add this as a recipe')
    recipe_title = StringField('Recipe Title')
    recipe_ingredients = TextAreaField('Ingredients')
    recipe_instructions = TextAreaField('Instructions')
    submit = SubmitField('Post Reply')

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if self.add_as_recipe.data:
            if not self.recipe_title.data:
                self.recipe_title.errors.append('This field is required.')
                return False
            if not self.recipe_ingredients.data:
                self.recipe_ingredients.errors.append('This field is required.')
                return False
            if not self.recipe_instructions.data:
                self.recipe_instructions.errors.append('This field is required.')
                return False

        return True

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=6, max=25)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')

    def validate_current_password(self, current_password):
        user = User.query.filter_by(id=current_user.id).first()
        if user and not user.check_password(current_password.data):
            raise ValidationError('Current password is incorrect.')

class RecipeForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    ingredients = TextAreaField('Ingredients', validators=[DataRequired()])
    instructions = TextAreaField('Instructions', validators=[DataRequired()])