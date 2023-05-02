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
    This endpoint returns a single character by its identifier. For each 
    character
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
    * `number_of_lines_together`: The number of lines the character has 
    with the
      originally queried character.
    """
    top_convos = """SELECT json_build_object(
    'character_id', c2.character_id,
    'character', c2.name,
    'gender', c2.gender,
    'number_of_lines_together', top_conversations.number_of_lines_together
    ) AS top_conversations
    FROM (
    SELECT l2.character_id, COUNT(*) AS number_of_lines_together
    FROM characters c1
    JOIN lines l1 ON l1.character_id = c1.character_id
    JOIN lines l2 ON l2.movie_id = l1.movie_id AND l2.character_id != 
    c1.character_id
    WHERE c1.character_id = {}
    GROUP BY l2.character_id
    ORDER BY number_of_lines_together DESC
    LIMIT 10
    ) AS top_conversations
    JOIN characters c2 ON c2.character_id = top_conversations.character_id;
    """.format(id)

    sql = """SELECT characters.character_id, name, title, gender
    FROM characters
    JOIN movies on movies.movie_id = characters.movie_id
    WHERE characters.character_id = {}
    """.format(id)

    with db.engine.connect() as conn:
        top = conn.execute(sqlalchemy.text(top_convos))
        result = conn.execute(sqlalchemy.text(sql))
        json = []
        top_conversations = []
        for row in top:
            top_conversations.append(
                row.top_conversations
            )
        for row in result:
            json.append(
                {
                    "character": row.name,
                    "character_id": row.character_id,
                    "movie": row.title,
                    "gender": row.gender,
                    "top_conversations": top_conversations
                }
            )
        return json
                              
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

    if sort == character_sort_options.character:
        s_val = "name"
    elif sort == character_sort_options.movie:
        s_val = "movie_id"
    elif sort == character_sort_options.number_of_lines:
        s_val = "COUNT(lines.line_id) DESC"
    else:
        s_val = "characters.character_id ASC"

    sql = """
    SELECT characters.character_id, characters.name, characters.movie_id, count(lines.line_id)
    FROM characters
    JOIN lines ON lines.character_id = characters.character_id
    WHERE name iLIKE '%{}%'
    group by characters.character_id
    ORDER BY {}
    liMIT :b OFFSET :c
    """.format(name, s_val)

    with db.engine.connect() as conn:
        result = conn.execute(sqlalchemy.text(sql),  [{"b": limit, "c": offset}])
        json = []
        for row in result:
            json.append(
                {
                    "character": row.name,
                    "character_id": row.character_id,
                    "movie_id": row.movie_id,
                    "num_lines": row.count
                }
            )
    return json
