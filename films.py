import requests
from bs4 import BeautifulSoup
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Настройка базы данных
DATABASE_URL = "sqlite:///./movies.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Модель базы данных для фильма
class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    title_eng = Column(String)
    year = Column(Integer)
    genre_country = Column(String)
    rating_filmru = Column(Float)
    rating_viewers = Column(Float)
    rating_imdb = Column(Float)

# Создание таблицы
Base.metadata.create_all(bind=engine)

# Функция для парсинга фильмов с film.ru
def fetch_movies_from_filmru():
    url = "https://www.film.ru/a-z/movies"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print('Подключение успешно')
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Извлекаем блоки с фильмами
        movies_list = soup.find_all("div", class_="redesign_afisha_movie_main")
        
        with SessionLocal() as session:
            for movie in movies_list:
                title = movie.find("a", class_="redesign_afisha_movie_main_title").find("strong").get_text(strip=True)
                
                # Проверяем, есть ли уже фильм в базе данных
                if session.query(Movie).filter_by(title=title).first():
                    print(f"{title} уже существует в базе данных.")
                    continue

                title_eng = movie.find("div", class_="redesign_afisha_movie_main_subtitle").find("span").get_text(strip=True)
               # print(title)
                #print(title_eng)
                
                # Год выпуска и жанр/страна
                year_and_genre = movie.find("div", class_="redesign_afisha_movie_main_subtitle").get_text(strip=True).split(" ")
                year = int(year_and_genre[0]) if year_and_genre[0].isdigit() else None
                genre_country = movie.find("div", class_="redesign_afisha_movie_main_info").get_text(strip=True)
                
                # Рейтинги
                ratings = movie.find("div", class_="redesign_afisha_movie_main_rating").find_all("span")
                rating_filmru = float(ratings[0].get_text(strip=True)) if ratings[0].get_text(strip=True).replace(".", "", 1).isdigit() else None
                rating_viewers = float(ratings[1].get_text(strip=True)) if ratings[1].get_text(strip=True).replace(".", "", 1).isdigit() else None
                rating_imdb = float(ratings[2].get_text(strip=True)) if ratings[2].get_text(strip=True).replace(".", "", 1).isdigit() else None

                # Сохраняем фильм в базе данных
                new_movie = Movie(
                    title=title,
                    title_eng=title_eng,
                    year=year,
                    genre_country=genre_country,
                    rating_filmru=rating_filmru,
                    rating_viewers=rating_viewers,
                    rating_imdb=rating_imdb
                )
                session.add(new_movie)
            session.commit()  # Сохраняем все добавленные фильмы
    else:
        print("Не удалось подключиться к сайту:", response.status_code)


with SessionLocal() as session:
    movies = session.query(Movie).all()
    for movie in movies:
        print(movie.title, movie.year, movie.rating_imdb)
  



# Вызов функции для парсинга
fetch_movies_from_filmru()