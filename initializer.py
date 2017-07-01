#!/usr/bin/env python3

# Batteries
import json
import sys

# Local
import model


@model.pny.db_session
def add_user_to_team(team_id, user_id):
    T = model.Team.get(id=team_id)
    if T is None:
        T = model.Team(id=team_id)
    U = model.User.get(id=user_id, team=T)
    if U is None:
        U = model.User(id=user_id, team=T)
    T.users.add(U)


def interface(inpath):
    with open(inpath) as fd:
        teams = json.load(fd)

    for t in teams:
        for u in teams[t]:
            add_user_to_team(t, u)


if __name__ == '__main__':
    try:
        inpath  = sys.argv[1]
    except:
        print("usage: {}  <inpath>".format(
            sys.argv[0]))
        sys.exit(1)
    interface(inpath)
