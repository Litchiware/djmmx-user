import sae  
from djmmx_user import app  
  
application = sae.create_wsgi_app(app)
