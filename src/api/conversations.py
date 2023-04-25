from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List

# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """

    # TODO: Remove the following two lines. This is just a placeholder to show
    # how you could implement persistent storage.
    char1 = db.characters.get(conversation.character_1_id)
    char2 = db.characters.get(conversation.character_2_id)
    if not char1 or not char2:
        raise HTTPException(status_code=404, detail="character not found.")
    if char1 == char2:
        raise HTTPException(status_code=400, 
            detail="conversation must contain unique characters.")
    for line in conversation.lines:
        if line.character_id != char1.id and line.character_id != char2.id:
            raise HTTPException(status_code=400, 
            detail="lines contain unknown character.")
    if(char1.movie_id != movie_id or 
       char2.movie_id != movie_id):
        raise HTTPException(status_code=400, detail="character not in movie.")

    db.logs.append({"conversation_id" : db.conv_id, 
                    "character1_id": conversation.character_1_id, 
                    "character2_id": conversation.character_2_id, 
                    "movie_id" : movie_id})
    db.upload_new_log()
    db.update_log()
    return db.conv_id
