import cyclone.web
from twisted.python import log
from web_utils import *
from common import *
import json
from jwt_auth import jwtauth

@jwtauth
class AddMovieHandler(JsonHandler, DatabaseMixin):
    SUPPORTED_METHODS = ("POST", "DELETE", "PUT")

    @dbsafe
    @defer.inlineCallbacks
    def delete(self):
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id='%s'" % self.uid)
        if len(r):
            if(r[0][6] == 'admin'):
                try:
                    m_id = self.request.arguments['id']
                    rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE id = '%s'" % m_id)
                    if len(rs):
                        yield self.dbpool.runQuery("DELETE FROM movie_records WHERE id='%s'" % m_id)
                        rcode = True
                        msg = "Movie deleted successfully"
                    else:
                        rcode = False
                        msg = "Invalid movie Id"
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
            else:
                rcode = False
                msg = "You are not an admin"
        else:
            rcode = False
            msg = "Invalid Admin Id"
        resp = {"response": rcode, "message": msg, "data": []}
        self.write(resp)

    @dbsafe
    @defer.inlineCallbacks
    def post(self):
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % self.uid)
        if len(r):
            role = r[0][6]
            if(role == 'admin'):
                try:
                    popularity = self.request.arguments['popularity']
                    name = self.request.arguments['movie_name']
                    director = self.request.arguments['director']
                    genre = self.request.arguments['genre']
                    score = self.request.arguments['imdb_score']
                    date = self.request.arguments['released']
                    reg = self.request.arguments['region']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE movie_name = '%s'" % name)
                    if len(rs):
                        rcode = False
                        msg = "Movie already recorded"
                    else:
                        gen = []
                        for x in genre:
                            gen.append(x)
                        gen = json.dumps(gen)
                        yield self.dbpool.runQuery(
                            "INSERT INTO movie_records (popularity, movie_name, director, genre, imdb_score, released_date, region) VALUES"
                            " ('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (popularity, name, director, gen, score, date, reg));
                        rcode = True
                        msg = "Movie inserted successfully"
            else:
                rcode = False
                msg = "You are not an admin"
        else:
            rcode = False
            msg = "Invalid admin Id"
        resp = {"response": rcode, "message": msg, "data": []}
        self.write(resp)

    @dbsafe
    @defer.inlineCallbacks
    def put(self):
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % self.uid)
        if len(r):
            role = r[0][6]
            if(role == 'admin'):
                try:
                    m_id = self.request.arguments['id']
                    popularity = self.request.arguments['popularity']
                    name = self.request.arguments['movie_name']
                    director = self.request.arguments['director']
                    genre = self.request.arguments['genre']
                    score = self.request.arguments['imdb_score']
                    date = self.request.arguments['released']
                    reg = self.request.arguments['region']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    res = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE id = '%s'" % m_id)
                    if len(res):
                        gen = []
                        for x in genre:
                            gen.append(x)
                        gen = json.dumps(gen)
                        rs = yield self.dbpool.runQuery(
                            "UPDATE movie_records SET popularity = ?, movie_name = ?, director = ?, genre = ?, imdb_score = ?, released_date = ?, region = ? WHERE id = ?", (popularity, name, director, gen, score, date, reg, m_id))
                        rcode = True
                        msg = "Movie updated successfully"
                        data = []
                    else:
                        rcode = False
                        msg = "No such movie present"
            else:
                rcode = False
                msg = "You are not an admin"
        else:
            rcode = False
            msg = "Invalid admin Id"
        resp = {"response": rcode, "message": msg, "data": data}
        self.write(resp)

def get_range_value(score):
    x = str(score - int(score))[2:3]
    if(x == '0'):
        tmp = score + 0.9
    else:
        tmp = score + 1
    return tmp

class MovieListHandler(JsonHandler, DatabaseMixin):
    SUPPORTED_METHODS = ('GET')

    @dbsafe
    @defer.inlineCallbacks
    def get(self):
        result = []
        try:
            if len(self.get_arguments('rating')):
                score = float(self.get_arguments('rating')[0])
                tmp = get_range_value(score)
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE imdb_score >= '%s' AND imdb_score <= '%s'" %
                        (score, tmp))
            elif len(self.get_arguments('movie')):
                mov = self.get_arguments('movie')[0]
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE movie_name = '%s'" % mov)
            elif len(self.get_arguments('released')):
                yr = self.get_arguments('released')[0]
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE released_date = '%s'" % yr)
            elif len(self.get_arguments('region')):
                reg = self.get_arguments('region')[0]
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE region = '%s'" % reg)
            elif len(self.get_arguments('director')):
                dtr = self.get_arguments('director')[0]
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records WHERE director = '%s'" % dtr)
            else:
                rs = yield self.dbpool.runQuery("SELECT * FROM movie_records")
            if len(rs):
                for res in rs:
                    result.append({'id': res[0], 'popularity': res[1], 'movie_name': res[2], 'director': res[3],
                        'genre': json.loads(res[4]), 'imdb_score': res[5], "released_on": res[6], "region": res[7]})
                rcode = True
                msg = ""
            else:
                rcode = False
                msg = "No data available"
        except Exception, e:
            log.msg("Invalid argument")
            rcode = False
            msg = "Invalid argument"
        resp = {"response": rcode, "message": msg, "data": result}
        self.write(resp)


