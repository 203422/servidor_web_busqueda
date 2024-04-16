class DevelopmentConfig():
    DEBUG = True
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '0123456'
    MYSQL_DB = 'busqueda'

config = {
    'development': DevelopmentConfig
}