import cyclone.web
from twisted.python import log
from web_utils import *
from common import *
import jwt
from jwt_auth import jwtauth, get_token
import json
import datetime
SECRET = 'my_secret_key'

class LoginHandler(JsonHandler, DatabaseMixin):
    SUPPORTED_METHODS = ("GET", "POST", "DELETE","PUT")
    @dbsafe
    @defer.inlineCallbacks
    def post(self):
        ph_num = self.request.arguments['mobile_number']
        password = self.request.arguments['password']
        auth = yield self.dbpool.runQuery("SELECT * FROM users WHERE mobile_number = '%s' and password = '%s'" %
                (ph_num, password))
        data = []
        if len(auth):
            if(auth[0][6] == 'admin'):
                uid = auth[0][0]
                #Getting the token using uid
                self.token = get_token(uid)
                rcode = True
                msg = ""
                data.append(self.token)
            else:
                rcode = False
                msg = "You are not an Admin"
        else:
            rcode = False
            msg = "Invalid mobile number and password"
        resp = {"response": rcode, "message": msg, "data": data}
        self.write(resp)


