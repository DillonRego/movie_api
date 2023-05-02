from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter
from fastapi.params import Query
from src import database as db
import sqlalchemy

router = APIRouter()

@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
#     conn = engine.connect()

#     stmt = (
#         sqlalchemy.select()
#         .limit(limit)
#         .offset(offset)
#         .order_by(order_by, db.movies.c.movie_id)
#     )
#     raise HTTPException(status_code=404, detail="character not found.")


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    conn = db.engine.connect()

    if sort is character_sort_options.character:
        order_by = db.characters.c.name
    elif sort is character_sort_options.movie:
        order_by = db.characters.c.movie_id
    elif sort is character_sort_options.number_of_lines:
        order_by = sqlalchemy.desc(db.characters.c.imdb_rating)
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.character,
            db.movies.filter(db.characters.c.movie_id == db.movies.c.movie_id).title,
            db.lines.fiter(db.characters.c.character_id == db.lines.c.character_id)
        )
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.movies.c.movie_id)
    )

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.movies.c.title.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "movie_id": row.movie_id,
                    "movie_title": row.title,
                    "year": row.year,
                    "imdb_rating": row.imdb_rating,
                    "imdb_votes": row.imdb_votes,
                }
            )

    return json
    


    # items = list(filter(filter_fn, db.characters.values()))

    # def none_last(x, reverse=False):
    #     return (x is None) ^ reverse, x

    # # if sort == character_sort_options.character:
    # #     items.sort(key=lambda c: none_last(c.name))
    # # elif sort == character_sort_options.movie:
    # #     items.sort(key=lambda c: none_last(db.movies[c.movie_id].title))
    # # elif sort == character_sort_options.number_of_lines:
    # #     items.sort(key=lambda c: none_last(c.num_lines, True), reverse=True)

    # json = (
    #     {
    #         "character_id": c.id,
    #         "character": c.name,
    #         "movie": db.movies[c.movie_id].title,
    #         "number_of_lines": c.num_lines,
    #     }
    #     for c in items[offset : offset + limit]
    # )
    # return json
