from cogindo import api
from cogindo import db
from cogindo.users import User

from flask import current_app
from flask.ext.security import login_required, current_user
from flask.ext.restful import Resource, abort, reqparse
from mongoengine.errors import ValidationError


def mongo_jsonify(query):
    """
    Formats mongoengine queryset as appropriate JSON response.
    """
    return current_app.response_class(query.to_json(),
                                      mimetype='application/json')


class Team(db.Document):
    name = db.StringField(max_length=80)
    description = db.StringField(max_length=255)


class TeamResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str)
        self.args = self.parser.parse_args()

    @login_required
    def get(self):
        if current_user.team is not None:
            return mongo_jsonify(current_user.team)
        else:
            abort(404, message="User has not joined a team.")

    @login_required
    def put(self):
        try:
            # Create a new team.
            team = Team(**self.args)
            team.save()

            # Put the current user on this team.
            current_user.team = team
            current_user.save()
            return mongo_jsonify(team), 201
        except ValidationError, e:
            abort(400, message=repr(e))

api.add_resource(TeamResource, '/api/team')


class TeamMembersResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str)
        self.args = self.parser.parse_args()

    @login_required
    def get(self):
        if current_user.team is not None:
            return mongo_jsonify(
                User.objects(team=current_user.team)
                .only("id", "name"))
        else:
            abort(404, message="User has not joined a team.")

    @login_required
    def put(self):
        try:
            new_user = User.objects.with_id(self.args['id'])
            if (new_user is not None
                    and new_user.team_request == current_user.team):
                new_user.team = current_user.team
                new_user.team_request = None
                new_user.save()
                return mongo_jsonify(
                    User.objects(team=current_user.team)
                    .only("id", "name")), 200
            else:
                abort(400, message="User did not request to join your team.")
        except ValidationError:
            abort(400, message="User ID was not valid.")

api.add_resource(TeamMembersResource, '/api/team/members')


class TeamRequestResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=str)
        self.args = self.parser.parse_args()

    @login_required
    def get(self):
        if current_user.team is not None:
            return mongo_jsonify(
                User.objects(team_request=current_user.team)
                .only("id", "name"))
        else:
            abort(404, message="User has not joined a team.")

    @login_required
    def put(self):
        try:
            team = Team.objects.with_id(self.args['id'])
            if team is not None:
                current_user.team_request = team
                current_user.save()
            return {"request": str(team.id)}, 201
        except ValidationError:
            abort(400, message="Team ID was not valid.")

api.add_resource(TeamRequestResource, '/api/team/requests')
