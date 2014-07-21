from cogindo import db
from cogindo import api
from cogindo import app
from cogindo.teams import Team

from flask import jsonify, request, send_from_directory
from flask.ext.security import login_required, current_user
from flask.ext.restful import Resource, abort

import datetime
import threading
import os


def get_subclasses(c):
    """
    Recursive generator of all subclasses of a given class.
    """
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        yield d
        for e in get_subclasses(d):
            yield e


class PuzzleState(db.DynamicDocument):
    team = db.ReferenceField(Team, required=True)
    name = db.StringField(max_length=80, required=True)
    display_name = db.StringField(max_length=255, required=True)
    version = db.IntField(required=True)
    found_time = db.DateTimeField(required=True)
    visible = db.BooleanField(default=False, required=True)
    enabled = db.BooleanField(default=False, required=True)
    completion = db.FloatField(default=0.0, required=True)


class Puzzle(object):
    PUZZLE_INSTANCES = {}
    PUZZLE_LOCK = threading.Lock()

    @property
    def display_name(self):
        return self.__class__.name

    @property
    def version(self):
        return 0

    def get(self, state, args):
        """
        Return the current state of this puzzle as a dict.
        """
        return {}

    def put(self, state, args):
        """
        Update the current state of this puzzle.
        """
        return {}

    def post(self, state, args):
        """
        Reset the puzzle to its initial state.
        """
        return {}

    @staticmethod
    def reveal(puzzle_name, args):
        """
        Reveal another puzzle to a team.  The args passed into this
        function are forwarded to the POST function on the other puzzle.
        """
        team = current_user.team
        if team is None:
            return

        puzzle = Puzzle.lookup(puzzle_name)
        if puzzle is None:
            return

        # Allow the puzzle to mess with its own settings.
        state = PuzzleState(team=team, name=puzzle)
        puzzle.post(state, args)

        # Set default fixed values and save to database.
        state.team = team
        state.name = puzzle.__class__.name
        state.display_name = puzzle.display_name
        state.version = int(puzzle.version)
        state.found_time = datetime.datetime.now()
        state.save()
        return state

    @staticmethod
    def lookup(puzzle_name):
        with Puzzle.PUZZLE_LOCK:

            # Return the puzzle instance if it exists.
            puzzle = Puzzle.PUZZLE_INSTANCES[puzzle_name]
            if puzzle:
                return puzzle

            # If no instance exists, try to create a new one.
            for c in get_subclasses(Puzzle):
                if puzzle_name == c.name:
                    puzzle = c()
                    Puzzle.PUZZLE_INSTANCES[puzzle_name] = puzzle
                    return puzzle


@app.route('/puzzles/<puzzle_name>/<path:filename>')
def puzzle_file(puzzle_name, filename):
    """
    File downloader that only allows teams to see content for puzzles
    that they have unlocked.
    """
    team = current_user.team
    if team is None:
        abort(404, message="User is not on a team.")

    state = PuzzleState.objects(team=team, name=puzzle_name).first()
    if state is None:
        abort(404, message="Puzzle not found.")

    return send_from_directory(
        os.path.join(app.root_path, 'puzzles', puzzle_name),
        filename)


class PuzzleResource(Resource):
    @login_required
    def get(self, puzzle_name):
        team = current_user.team
        if team is None:
            abort(404, message="User is not on a team.")

        state = PuzzleState.objects(team=team, name=puzzle_name).first()
        if state is None:
            abort(404, message="Puzzle not found.")

        puzzle = Puzzle.lookup(puzzle_name)
        if puzzle is None:
            abort(404, message="Puzzle not found.")

        if puzzle.version != state.version:
            state.delete()
            state = Puzzle.reveal(puzzle_name, request.args)

        result = jsonify(puzzle.get(state, request.args))
        state.save()
        return result

    @login_required
    def put(self, puzzle_name):
        team = current_user.team
        if team is None:
            abort(404, message="User is not on a team.")

        state = PuzzleState.objects(team=team, name=puzzle_name).first()
        if state is None:
            abort(404, message="Puzzle status not found.")

        puzzle = Puzzle.lookup(puzzle_name)
        if puzzle is None:
            abort(404, message="Puzzle not found.")

        if puzzle.version != state.version:
            state.delete()
            state = Puzzle.reveal(puzzle_name, request.args)

        result = jsonify(puzzle.put(state, request.args))
        state.save()
        return result, 200

    @login_required
    def post(self, puzzle_name):
        abort(403, message="Only administrators can reset puzzles.")

api.add_resource(PuzzleResource, '/api/puzzles/<puzzle_name>')
