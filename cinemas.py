import re
from operator import itemgetter

import requests
from bs4 import BeautifulSoup


def fetch_afisha_page():
    return requests.get('http://www.afisha.ru/msk/schedule_cinema/').content


def parse_afisha_list(raw_html):
    soup = BeautifulSoup(raw_html, features="html.parser")
    names_tags = soup.findAll('h3', class_='card__title')
    return list(
        map(
            lambda tag: tag.string.strip().strip('«»'),
            names_tags
        )
    )


def fetch_movie_info(movie_title):
    kinopoisk_html = requests.get(
        'https://www.kinopoisk.ru/index.php',
        {
            'kp_query': movie_title
        }
    ).content
    soup = BeautifulSoup(kinopoisk_html, features="html.parser")
    rating_tag = soup.select_one('div.element.most_wanted div.rating')
    none_int = 0
    if (rating_tag is None):
        rating_tag = soup.select_one('span.rating_ball')
        count_tag = soup.select_one('span.ratingCount')
        rating = float(rating_tag.string) if rating_tag else none_int
        votes_cnt = int(count_tag.string) if count_tag else none_int
        return rating, votes_cnt

    rating, votes_cnt = rating_tag['title'].split(' ')
    rating = float(rating)
    votes_cnt = int(re.sub(r'[()\u00a0]', '', votes_cnt))
    return rating, votes_cnt


def output_movies_to_console(movies):
    movies = sorted(movies, key=itemgetter('rating'), reverse=True)[:10]
    for movie in movies:
        print('{title:<30} | {rating} ({votes_cnt})'.format(
            title=movie['title'],
            rating=movie['rating'],
            votes_cnt=movie['votes_cnt']
        ))


if __name__ == '__main__':
    raw_html = fetch_afisha_page()

    titles = parse_afisha_list(raw_html)

    movies = []
    for title in titles:
        rating, votes_cnt = fetch_movie_info(title)
        movies.append({
            'title': title,
            'rating': rating,
            'votes_cnt': votes_cnt
        })

    output_movies_to_console(movies)
