class User:
    def __init__ (self):
        self.username = 'barista'
        self.password = '123456'
        self.user_id = 1
        self.authenticated = False
        self.active = True
        self.anonymous = False

    def is_authenticated():
        return self.authenticated
    
    def is_active():
        return self.active

    def is_anonymous():
        return self.anonymous

    def authenticate(username, password):
        if username == self.username and password == self.password:
            self.authenticated = True
