#!/usr/bin/env python3

from decimal import Decimal
import pony.orm as pny


db = pny.Database()


class Team(db.Entity):
    id    = pny.PrimaryKey(pny.LongStr, lazy=False)
    users = pny.Set('User')


class Post(db.Entity):
    id = pny.PrimaryKey(pny.LongStr, lazy=False)
    user = pny.Required('User')
    location = pny.Optional('Location')
    images = pny.Set('Image')
    videos = pny.Set('Video')


class User(db.Entity):
    id = pny.PrimaryKey(pny.LongStr, lazy=False)
    posts = pny.Set(Post)
    team  = pny.Required(Team)


class Location(db.Entity):
    id   = pny.PrimaryKey(int, auto=True)
    post = pny.Required(Post)
    latitude  = pny.Required(Decimal)
    longitude = pny.Required(Decimal)


class Image(db.Entity):
    post = pny.Required(Post)
    id   = pny.PrimaryKey(pny.LongStr, lazy=False)


class Video(db.Entity):
    post = pny.Required(Post)
    id   = pny.PrimaryKey(pny.LongStr, lazy=False)


db.bind("sqlite", "database.sqlite",
        create_db=True)
db.generate_mapping(create_tables=True)
