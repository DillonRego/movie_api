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
    * `in_context` : Shows the rest of the conversation with the line in question highlighted as html
    """
    line = db.lines.get(line_id)

    def filter_fn(l):
        return l.conv_id == line.conv_id

    movie = db.movies.get(line.movie_id)
    char = db.characters.get(line.c_id)
    in_context = "<html>"

    items = list(filter(filter_fn, db.lines.values()))    
    for item in items:
        c = db.characters.get(item.c_id)
        if item != line:
            in_context += c.name + ": " + item.line_text + "<br>"
        else:
            in_context += c.name + ": " +"<b>" + item.line_text + "</b><br>"
            

    if line:
        result = {
            "line_id": line.id,
            "title": movie.title,
            "said_by": char.name,
            "in_context": in_context
        }
        return result

    raise HTTPException(status_code=404, detail="line not found.")

# Add get parameters
@router.get("/lines/", tags=["lines"])
def list_lines(
    text: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
):
    """
    This endpoint returns a list of lines. For each line it returns:
    
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `movie_id`: the internal id of the movie the line appears in. can be used
    to querry the '/movies/{movie_id}' endpoint
    * `movie_title`: The title of the movie the line appears in.
    * `text : the lines text.
    * `conversation_id`: The internal id of the conversation.
    * `characters_involved`: a touple containing the characters involved in the conversation.

    You can filter for a line whose text contain a string by using the
    `text` query parameter.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if text:
        def filter_fn(l):
            return l.line_text and text.lower() in l.line_text
    else:
        def filter_fn(_):
            return True

    items = list(filter(filter_fn, db.lines.values()))
    items.sort(key=lambda l: l.id)

    json = (
        {
            "line_id": l.id,
            "movie_id" : l.movie_id,
            "movie_title": db.movies.get(l.movie_id).title,
            "text": l.line_text,
            "conversation_id": l.conv_id, 
            "characters_involved": (db.characters.get(db.conversations.get(l.conv_id).c1_id),
                                    db.characters.get(db.conversations.get(l.conv_id).c2_id))
        }
        for l in items[offset : offset + limit]

    )

    return json


# Add get parameters
@router.get("/lines/bycharacter/{character_id}", tags=["lines"])
def list_lines(
    character_id : int,
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
):
    """
    This endpoint returns a list of lines said by a specific character. For each line it returns:
    
    * `line_id`: the internal id of the line. Can be used to query the
      `/lines/{line_id}` endpoint.
    * `movie_id`: the internal id of the movie the line appears in
    * `character_id` : the internal id of the character the line belongs to
    * `text : the lines text.
    * `conversation_id`: The IMDB rating of the movie.
    """

    def filter_fn(l):
        return character_id == l.c_id

    items = list(filter(filter_fn, db.lines.values()))
    items.sort(key=lambda l: l.id)

    json = (
        {
            "line_id": l.id,
            "movie_id": l.movie_id,
            "character_id": l.c_id,
            "text": l.line_text,
            "conversation_id": l.conv_id,
        }
        for l in items[offset : offset + limit]
    )

    return json
