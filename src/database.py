import sqlalchemy
import os
import dotenv

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())

# Use reflection to derive table schema. You can also code this in manually.
metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)

lines = sqlalchemy.Table("lines", metadata_obj, autoload_with=engine)

characters = sqlalchemy.Table("characters", metadata_obj, autoload_with=engine)

conversations = sqlalchemy.Table("conversations", metadata_obj, autoload_with=engine)