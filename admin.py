import cyclone.web
from twisted.python import log
from web_utils import *
from common import *
import json
from jwt_auth import jwtauth

@jwtauth
class AddAdminHandler(JsonHandler, DatabaseMixin):
    SUPPORTED_METHODS = ("POST", "GET", "DELETE", "PUT")

    @dbsafe
    @defer.inlineCallbacks
    def get(self):
        a_id = self.uid
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % a_id)
        result = []
        if len(r):
            role = r[0][6]
            if(role == 'admin'):
                rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE role = '%s'" % role)
                if len(rs):
                    for res in rs:
                        result.append({'id': res[0], 'name': res[1], 'mobile_number': res[2],
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
        resp = {"response": rcode, "message": msg, "data": result}
        self.write(resp)

    @dbsafe
    @defer.inlineCallbacks
    def delete(self):
        r = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % self.uid)
        if len(r):
            role = r[0][6]
            if(role == 'admin'):
                try:
                    a_id = self.request.arguments['id']
                    rcode = True
                except Exception, e:
                    log.msg("requested argument not given")
                    rcode = False
                    msg = "Argument missing"
                if(rcode == True):
                    res = yield self.dbpool.runQuery("SELECT * FROM users WHERE id='%s'" % a_id)
                    if len(res):
                        rs = yield self.dbpool.runQuery("DELETE FROM users WHERE id='%s'" % a_id)
                        rcode = True
                        msg = "admin deleted successfully"
                    else:
                        rcode = False
                        msg = "Admin is not present"
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
                    rt = yield self.dbpool.runQuery("SELECT * FROM users WHERE mobile_number = '%s'" % ph_num)
                    if len(rt):
                        rcode = False
                        msg = "Admin already exists"
                    else:
                        yield self.dbpool.runQuery(
                            "INSERT INTO users (name, mobile_number, address, email_id, password, role) VALUES"
                            " ('%s','%s', '%s','%s', '%s', '%s')" % (name, ph_num, addr, email, pwd, 'admin'));
                        rcode = True
                        msg = "Admin inserted successfully"
            else:
                rcode = False
                msg = "You are not an Admin"
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
            role = r[0][6]
            if(role == 'admin'):
                try:
                    a_id = self.request.arguments['id']
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
                    rs = yield self.dbpool.runQuery("SELECT * FROM users WHERE id = '%s'" % a_id)
                    if len(rs):
                        yield self.dbpool.runQuery(
                            "UPDATE users SET name = ?, mobile_number = ?, address = ?, email_id = ? where id = ?",
                            (name, ph_num, addr, email, a_id))
                        rcode = True
                        msg = "Admin updated successfully"
                    else:
                        rcode = False
                        msg = "Invalid admin Id"
            else:
                rcode = False
                msg = "You are not an Admin"
        else:
            rcode = False
            msg = "Invalid Admin Id"
        resp = {"response": rcode, "message": msg, "data": []}
        self.write(resp)

