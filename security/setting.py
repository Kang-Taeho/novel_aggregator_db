class DB :
    __host = '**************'
    __port = 0
    __user = '******'
    __passwd = '*************'
    __db = '***********'

    @classmethod
    def get_host(cls) : return cls.__host
    @classmethod
    def get_port(cls) : return cls.__port
    @classmethod
    def get_user(cls) : return cls.__user
    @classmethod
    def get_passwd(cls) : return cls.__passwd
    @classmethod
    def get_db(cls) : return cls.__db
