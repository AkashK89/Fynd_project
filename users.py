import cyclone.web
from twisted.python import log
from web_utils import *
from common import *
from jwt_auth import jwtauth

@jwtauth
class AddUserHandler(JsonHandler, DatabaseMixin):
    SUPPORTED_METHODS = ("GET", "POST", "DELETE","PUT")

    @dbsafe
    @defer.inlineCallbacks
    def get(self):
        a_id = self.uid
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % a_id)
        result = []
        if len(r):
            if(r[0][6] == 'admin'):
                rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE role = '%s'" % 'user')
                if len(rs):
                    for res in rs:
                        result.append({'id': res[0], 'username': res[1], 'mobile_number': res[2],
                            'address': res[3], 'email_id': res[4]})
                    rcode = True
                    msg = ""
                else:
                    rcode = False
                    msg = "No data available"
            else:
                rcode = False
                msg = "You are not an admin"
        else:
            rcode = False
            msg = "Invalid Admin Id"
        resp = {"respnse": rcode, "message": msg, "data": result}
        self.write(resp)

    @dbsafe
    @defer.inlineCallbacks
    def post(self):
        a_id = self.uid
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % a_id)
        if len(r):
            if(r[0][6] == 'admin'):
                try:
                    pwd = self.request.arguments['password']
                    name = self.request.arguments['name']
                    ph_num = self.request.arguments['mobile_number']
                    addr = self.request.arguments['address']
                    email = self.request.arguments['email_id']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE mobile_number = '%s'" % ph_num)
                    if len(rs):
                        rcode = False
                        msg = "User already exists"
                    else:
                        yield self.dbpool.runQuery(
                            "INSERT INTO users (name, mobile_number, address, email_id, password, role) VALUES"
      	                    " ('%s', '%s' , '%s' , '%s', '%s', '%s') " % (name, ph_num, addr, email, pwd, 'user'))
                    rcode = True
                    msg = "User inserted successfully"
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
    def delete(self):
        a_id = self.uid
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % a_id)
        if len(r):
            if(r[0][6] == 'admin'):
                try:
                    u_id = self.request.arguments['id']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s' and role = '%s'" % (u_id, 'user'))
                    if len(rs):
                        yield self.dbpool.runQuery("DELETE from users WHERE id = '%s'" % u_id)
                        rcode = True
                        msg = "User deleted successfully"
                    else:
                        rcode = False
                        msg = "User does not exist"
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
    def put(self):
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % self.uid)
        if len(r):
            if(r[0][6] == 'admin'):
                try:
                    u_id = self.request.arguments['id']
                    name = self.request.arguments['name']
                    ph_num = self.request.arguments['mobile_number']
                    addr = self.request.arguments['address']
                    email = self.request.arguments['email_id']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s' and role = '%s'" % (u_id, 'user'))
                    if len(rs):
                        yield self.dbpool.runQuery(
                            "UPDATE users SET name = ?, mobile_number = ?, address = ?, email_id = ? WHERE id = ? and role = ?",
                            (name, ph_num, addr, email, u_id, 'user'))
                        rcode = True
                        msg = "User updated successfully"
                    else:
                        rcode = False
                        msg = "Invalid user Id"
            else:
                rcode = False
                msg = "You are not an admin"
        else:
            rcode = False
            msg = "Invalid Admin Id"
        resp = {"response": rcode, "message": msg, "data": []}
        self.write(resp)


