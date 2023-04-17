from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from fastapi.params import Query

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_lines(line_id: int):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * `line_id`: the internal id of the line.
    * `title`: the title of the movie the line appears in.
    * `text`: The line itself.
    * `said by` : What character said the line.
    * `said to` : Who the character said it to
    * `in_context` : Shows the rest of the conversation with the line in question highlighted as html
    
    """

  

    line = db.lines.get(line_id)

    def filter_fn(l):
        return l.conversation_id == line.conversation_id

    movie = db.movies.get(line.movie_id)
    char_1 = db.characters.get(line.character1_id)
    char_2 = db.characters.get(line.character2_id)
    in_context = "<html>"

    items = list(filter(filter_fn, db.lines.values()))    


    if line:
        result = {
            "line_id": line.line_id,
            "title": movie.title,
            "said_by": char_1.name,
            "said_to": char_2.name,
            "in_context":
        }
        return result

    raise HTTPException(status_code=404, detail="line not found.")


class line_sort_options(str, Enum): #TODO fix this
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/lines/", tags=["lines"])
def list_lines(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: line_sort_options = line_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if name:
        def filter_fn(m):
            return m.title and name.lower() in m.title

    else:

        def filter_fn(_):
            return True

    items = list(filter(filter_fn, db.movies.values()))
    if sort == movie_sort_options.movie_title:
        items.sort(key=lambda m: m.title)
    elif sort == movie_sort_options.year:
        items.sort(key=lambda m: m.year)
    elif sort == movie_sort_options.rating:
        items.sort(key=lambda m: m.imdb_rating, reverse=True)

    json = (
        {
            "movie_id": m.id,
            "movie_title": m.title,
            "year": m.year,
            "imdb_rating": m.imdb_rating,
            "imdb_votes": m.imdb_votes,
        }
        for m in items[offset : offset + limit]
    )

    return json
