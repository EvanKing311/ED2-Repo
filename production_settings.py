from .settings import *

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = 'efiy#i9cg+dw!i+b+$6&t7v2r5rjc=@h31t2e&w#r)9z2c*gp0'

# Add your domain/IP
ALLOWED_HOSTS = [
    'domain.com',
    'www.domain.com',
    'pc-ip-address',
    'localhost',
]

# STATIC FILES
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = '/static/'

#SET ALL TO TRUE IF WE END UP USING HTTPS
# SECURITY HEADERS
SECURE_SSL_REDIRECT = False  
SESSION_COOKIE_SECURE = False  
CSRF_COOKIE_SECURE = False  

# DATABASE - existing MySQL config
DATABASES = {
    'default': {
        'ENGINE': 'mysql.connector.django',
        'NAME': 'egnsitedb',
        'USER': 'root',
        'PASSWORD': 'Kings1305',  
        'HOST': 'localhost',
        'PORT': '3306',
    }
}