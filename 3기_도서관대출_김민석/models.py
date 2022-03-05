from datetime import datetime

from db_connect import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    pw = db.Column(db.String(256), nullable=False)
    username = db.Column(db.String(20), nullable=False)

    is_authenticated = True
    is_active = True

    def get_id(self):
        return self.user_email

    userbookcomment = db.relationship("BookComment", backref="user")
    userbookrentinfo = db.relationship("BookRentInfo", backref="user")

    def __init__(self, user_email, pw, username):
        self.user_email = user_email
        self.pw = pw
        self.username = username


class BookInfo(db.Model):
    __tablename__ = "bookInfo"

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    book_name = db.Column(db.String(100), nullable=False, unique=True)
    publisher = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    publication_date = db.Column(db.Date)
    pages = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.BigInteger, nullable=False)
    descrip = db.Column(db.TEXT, nullable=False)
    link = db.Column(db.String(500), nullable=False)
    img_path = db.Column(db.String(500), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    bookinfobookcomment = db.relationship("BookComment", backref="bookInfo")
    bookinfobookrentinfo = db.relationship("BookRentInfo", backref="bookInfo")

    def __init__(
        self,
        id,
        book_name,
        publisher,
        author,
        publication_date,
        pages,
        isbn,
        descrip,
        link,
        img_path,
        stock,
        rating,
    ):
        self.id = id
        self.book_name = book_name
        self.publisher = publisher
        self.author = author
        self.publication_date = publication_date
        self.pages = pages
        self.isbn = isbn
        self.descrip = descrip
        self.link = link
        self.img_path = img_path
        self.stock = stock
        self.rating = rating


class BookComment(db.Model):
    __tablename__ = "bookComment"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    comment = db.Column(db.String(500), primary_key=True, nullable=False)
    rating = db.Column(db.Integer(), primary_key=True, nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    bookInfo_id = db.Column(db.Integer(), db.ForeignKey("bookInfo.id"))

    def __init__(self, comment, rating, user_id, bookInfo_id):
        self.comment = comment
        self.rating = rating
        self.user_id = user_id
        self.bookInfo_id = bookInfo_id


class BookRentInfo(db.Model):
    __tablename__ = "bookRentInfo"
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True, nullable=False)
    book_id = db.Column(db.Integer(), db.ForeignKey("bookInfo.id"))
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    rent_date = db.Column(db.Date(), nullable=False)
    return_date = db.Column(db.Date())

    book = db.relationship("BookInfo", foreign_keys="BookRentInfo.book_id")

    def __init__(self, book_id, user_id, rent_date):
        self.book_id = book_id
        self.user_id = user_id
        self.rent_date = rent_date
