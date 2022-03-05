import csv
from datetime import date, datetime
  
#init의 db를 가져와서 init이 실행될때, db를 import한 파일들이 먼저 실행되면서 아래 코드를 한번 숙 훑고 간다. 
import os
import csv
import dotenv

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

dotenv.load_dotenv('.env')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] =os.environ.get('DATABASE_URI')

# db 초기화
db = SQLAlchemy()
db.init_app(app)
# from __init__ import *
# from db_connect import db
# app_context 생성 - 참고 https://flask-docs-kr.readthedocs.io/ko/latest/appcontext.html
app.app_context().push()

# db를 초기화 한뒤에 models를 import
# models 는 'db' 객체에 의존하기 때문
from models import *

# 테이블이 존재하지 않다면 생성
db.create_all()
 
with open('info_books.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        published_at = row['publication_date']
        image_path = f"/static/book_photo/{row['id']}"
        try:
            open(f'{image_path}.png')
            #위에 설정해둔 image_path를 여는 코든데, 우린 같은 디렉토리에 있으니까 app을 지워도됨.
            #해당 파일이 .png로 열리면 png 아니면 jpg로.
            image_path += '.png'
        except:
            image_path += '.jpg'

        published_at = datetime.strptime(published_at, '%Y-%m-%d').date()
        book = BookInfo(
            id=int(row['id']), book_name=row['book_name'], publisher=row['publisher'],
            author=row['author'], publication_date=published_at, pages=int(row['pages']),
            isbn=row['isbn'], descrip=row['description'], link=row['link'], img_path=image_path,
            stock=5, rating=0
        )
        db.session.add(book)
    db.session.commit()