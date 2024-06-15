from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
import openai
from factories import MuscleQuestionFactory, OpenAIMuscleQuestionStrategy
import time
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'Nathan123'
app.config['UPLOAD_FOLDER'] = '/home/NathanBatista/mysite/static/uploads'
app.config['DEBUG'] = True

openai.api_key = 'sk-proj-it3FMvQ0gxBMLYGDpwNqT3BlbkFJ8qFb72ID7COqqLulgokT'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    posts = db.relationship('Post', backref='user', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

    def __init__(self, name, password):
        self.name = name
        self.password = password

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ratings = db.relationship('Rating', backref='post', lazy=True, cascade="all, delete-orphan")

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

with app.app_context():
    db.create_all()

def calculate_average_rating(post_id):
    ratings = Rating.query.filter_by(post_id=post_id).all()
    if ratings:
        return sum(rating.score for rating in ratings) / len(ratings)
    return None

def perguntar(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente útil."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

#Decorator (Padrão de Projeto Estrutural)
def log_execution_time(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Function {f.__name__} executed in {execution_time:.4f} seconds")
        return result
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
@log_execution_time
def homePage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    posts = Post.query.all()
    posts_with_ratings = [
        {
            'post': post,
            'average_rating': calculate_average_rating(post.id)
        } for post in posts
    ]

    quiz_question = None
    quiz_options = None
    if 'quiz' in request.args:
        strategy = OpenAIMuscleQuestionStrategy()  # Pode ser alterado para qualquer outra estratégia
        factory = MuscleQuestionFactory(strategy)
        try:
            quiz_question, quiz_options, correct_answer = factory.create_question()
            session['correct_answer'] = correct_answer
            session['quiz_options'] = quiz_options  # Armazena as opções embaralhadas na sessão
        except ValueError as e:
            quiz_question = "Erro ao gerar a pergunta do quiz: " + str(e)

    if request.method == 'POST' and 'answer' in request.form:
        answer = request.form['answer']
        correct_answer = session.get('correct_answer')
        quiz_options = session.get('quiz_options')  # Recupera as opções embaralhadas da sessão
        if answer == correct_answer:
            return redirect(url_for('workout_plan'))

    return render_template('homePage.html', posts_with_ratings=posts_with_ratings, quiz_question=quiz_question, quiz_options=quiz_options, enumerate=enumerate)

@app.route('/upload', methods=['GET', 'POST'])
@log_execution_time
def upload():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            new_post = Post(image=filename, user_id=session['user_id'])
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('homePage'))
    return redirect(url_for('homePage'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@log_execution_time
def post(post_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        rating = int(request.form['rating'])
        new_rating = Rating(score=rating, user_id=session['user_id'], post_id=post_id)
        db.session.add(new_rating)
        db.session.commit()
        return redirect(url_for('homePage'))
    return render_template('homePage.html', posts=Post.query.all(), post=post)

@app.route('/delete/<int:id>', methods=['POST'])
@log_execution_time
def delete(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    post = Post.query.get(id)
    if not post:
        return redirect(url_for('homePage'))  # Post não encontrado

    if post.user_id != session['user_id']:
        return redirect(url_for('homePage'))  # Usuário não autorizado a excluir

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('homePage'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['usernameLogin']
        password = request.form['passwordLogin']

        user = User.query.filter_by(name=name, password=password).first()

        if user:
            session['user_id'] = user.id
            session['username'] = user.name
            session['password'] = user.password
            return redirect(url_for('homePage'))
        else:
            return render_template('auth.html', error='Invalid username or password', usuarios=User.query.all(), debug=app.config['DEBUG'])
    return render_template('auth.html', usuarios=User.query.all(), debug=app.config['DEBUG'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['usernameRegister']
        password = request.form['passwordRegister']

        # Verifica se o nome de usuário já existe
        existing_user = User.query.filter_by(name=name).first()
        if existing_user:
            return render_template('auth.html', error='Username already taken', usuarios=User.query.all(), debug=app.config['DEBUG'])

        if name and password:
            newUser = User(name=name, password=password)
            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for('login'))

        return render_template('auth.html', error='Invalid username or password', usuarios=User.query.all(), debug=app.config['DEBUG'])

    return render_template('auth.html', usuarios=User.query.all(), debug=app.config['DEBUG'])


@app.route('/logout')
@log_execution_time
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('homePage'))

@app.route('/quiz', methods=['GET'])
@log_execution_time
def quiz():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('homePage', quiz='true'))

@app.route('/workout_plan')
@log_execution_time
def workout_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    workout_plan = perguntar("Crie uma planilha de treino de musculação completa.")
    return render_template('workout_plan.html', workout_plan=workout_plan)

if __name__ == '__main__':
    app.run(debug=True)
