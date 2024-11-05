from banSiteCozinhadejaoSite import database, app 
from SiteCozinha.models import Usuario,Foto

with app.app_context():
    database.create_all()