# OnlyRecipes

OnlyRecipes is a web application that serves as a recipe request forum. Users can create accounts, post and respond to recipe requests, search for recipes, and interact with other food enthusiasts.

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- User authentication (registration, login, logout)
- Create and manage recipe requests
- Post replies to recipe requests
- Convert replies to full recipes
- Search for recipes and requests by ingredients and meal type
- Responsive design for mobile and desktop use
- User account management (update details, view own recipes and requests)
- Flash messages for user feedback
- Secure password handling

## Technologies Used

- **Frontend:**
  - HTML
  - CSS (Bootstrap for styling)
  - JavaScript (jQuery)
  
- **Backend:**
  - Python (Flask framework)
  - SQLite (SQLAlchemy for ORM)

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- `pip` (Python package installer)

### Installation Steps

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/onlyrecipes.git
    cd onlyrecipes
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**

    ```bash
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

5. **Run the application:**

    ```bash
    flask run
    ```

6. **Access the application:**
   Open your web browser and navigate to `http://127.0.0.1:5000`.

## Usage

1. **Register an account:** Create a new user account to access the full features of the application.
2. **Create a recipe request:** Post a new recipe request for other users to respond to.
3. **Reply to a request:** Post a reply to a recipe request. Optionally, mark your reply as a full recipe.
4. **Search for recipes:** Use the search bar to find recipes based on ingredients and meal types.
5. **Manage your account:** Update your account information, view your posted recipes and requests, and manage your replies.

## Project Structure
onlyrecipes/
│
├── app/
│ ├── static/
│ │ ├── css/
│ │ ├── images/
│ │ └── js/
│ ├── templates/
│ │ ├── partials/
│ │ ├── account.html
│ │ ├── add_recipe.html
│ │ ├── base.html
│ │ ├── create_reply.html
│ │ ├── index.html
│ │ ├── login.html
│ │ ├── register.html
│ │ ├── search_results.html
│ │ ├── update_recipe.html
│ │ ├── update_reply.html
│ │ ├── view_recipe.html
│ │ ├── view_reply.html
│ │ └── view_recipe_request.html
│ ├── init.py
│ ├── forms.py
│ ├── models.py
│ ├── routes.py
│ └── extensions.py
├── venv/
├── .gitignore
├── README.md
├── requirements.txt
└── run.py

## Contributing

We welcome contributions to enhance OnlyRecipes. To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Enjoy using OnlyRecipes! If you have any questions or feedback, please contact us or open an issue on GitHub.
