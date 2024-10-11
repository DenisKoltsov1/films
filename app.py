from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from films import Movie, Base 
from films import fetch_movies_from_filmru
# Настройка базы данных
DATABASE_URL = "sqlite:///./movies.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = Flask(__name__)

@app.route('/')
def index():
    # Получаем данные из базы данных
    with SessionLocal() as session:
        movies = session.query(Movie).all()

    # Передаем данные в шаблон
    return render_template('index.html', movies=movies)

@app.route('/fetch_movies', methods=['POST'])
def fetch_movies():
    # Вызов функции для парсинга
    fetch_movies_from_filmru()  
    
    # Перенаправляем обратно на главную страницу
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)