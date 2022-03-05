"""
- 현재 DB 상에 존재하는 모든 책 정보를 가져옵니다.
- 현재 DB 상에 존재하는 남은 책의 수를 표기합니다.
- 책 이름을 클릭 시 책 소개 페이지로 이동합니다.
- 책의 평점은 현재 DB 상에 담겨있는 모든 평점의 평균입니다. 숫자 한자리수로 반올림하여 표기합니다.
"""

from flask import Blueprint, request, session, flash, redirect, url_for, render_template
from datetime import date
from flask_login import login_required, login_user, current_user, logout_user

from models import User,BookInfo,BookComment,BookRentInfo
from db_connect import db
from . import login_manager



from sqlalchemy import desc


bp=Blueprint('main',__name__,url_prefix='/main')

@bp.route('/home',methods=['GET','POST'])
def home():
    if not current_user.is_authenticated:
        flash('로그인 되지 않거나, 로그인 유효시간이 지났네요. 다시 로그인해 주세요')
        return redirect(url_for('auth.login'))
    page = request.args.get('page', 1, type=int)
    book_list=BookInfo.query.paginate(page,per_page=8,error_out=False)

    if request.method == 'POST':
        bookId = request.form.get('bookId')
        if not bookId:
            flash('book_id는 필수 파라미터 입니다.')
            return render_template('home.html', books=book_list)
        try:
            bookId = int(bookId)
        except ValueError:
            flash('book_id는 정수여야 합니다.')
            return render_template('home.html', books=book_list)

        book = BookInfo.query.filter_by(id=bookId).first()
        if book is None:
            flash('대출하려는 책을 찾을 수 없습니다.')
            return render_template('home.html', books=book_list)

#        rentInfo=BookRentInfo.query.filter_by(book_id=bookId).first()
#        if rentInfo.return_date is None:
#            flash(f'{book.book_name}을 이미 대여한 상태입니다.')

        if book.stock == 0:
            flash('모든 책이 대출중입니다')
        #bookId랑 내가 불러올 rentInfo의 book_id랑 같으면? 해당 책을 이미 빌렸다고 flash뿌림
        else:
            rent = BookRentInfo(book_id=bookId, user_id=current_user.id, rent_date=date.today())
            db.session.add(rent)
            book.stock -= 1
            db.session.commit()
            flash(f'{book.book_name}을 대여했습니다.')
        return redirect('/main/home')

    return render_template('home.html', books=book_list)


@bp.route('/books/<int:book_id>',methods=['GET','POST'])
def books(book_id):
    if not current_user.is_authenticated:
        flash('로그인 되지 않거나, 로그인 유효시간이 지났네요. 다시 로그인해 주세요')
        return redirect(url_for('auth.login'))
    book=BookInfo.query.filter_by(id=book_id).first()
    if book is None:
        flash('책을 찾을 수 없습니다.')
        return redirect('/main/home')
    if request.method == 'POST':
        content = request.form.get('content')
        if not content:
            flash('내용을 입력해주세요')
            return redirect(f'/main/books/{book_id}')
        rating = request.form.get('rating')
        if not rating:
            flash('평가를 입력해주세요')
            return redirect(f'/main/books/{book_id}')
        try:
            rating = int(rating)
        except ValueError:
            flash('평가 점수를 올바르게 입력해주세요.')
            return redirect(f'/books/{book_id}')
        book_comment = BookComment(bookInfo_id=book_id, user_id=current_user.id, comment=content,
                                   rating=rating + 1)
        db.session.add(book_comment)
        db.session.commit()
        comments = BookComment.query.filter_by(bookInfo_id=book.id).all()
        rating_sum = 0
        for comment in comments:
            rating_sum += comment.rating
            #여기에 breakpoint찍고 디버깅 돌려보기
        book_rating = round(rating_sum / len(comments))
        book.rating = book_rating

        db.session.add(book)
        db.session.commit()
    comments = BookComment.query.filter_by(bookInfo_id=book.id).order_by(desc(BookComment.id))

    return render_template('book_info.html',book=book,comments=comments)


@bp.route('/rent_history',methods=['GET','POST'])
def rent_history():
    if not current_user.is_authenticated:
        flash('로그인 되지 않거나, 로그인 유효시간이 지났네요. 다시 로그인해 주세요')
        return redirect(url_for('auth.login'))
    rents=BookRentInfo.query.filter_by(user_id=current_user.id)
    
    return render_template('rent_history.html',book_rents=rents)

@bp.route('/book_return',methods=['GET','POST'])
def book_return():
    if not current_user.is_authenticated:
        flash('로그인 되지 않거나, 로그인 유효시간이 지났네요. 다시 로그인해 주세요')
        return redirect(url_for('auth.login'))
    book_id=None
    if request.method == 'POST':
        rent_id=request.form.get('rent_id')
        user_bookRentInfo=BookRentInfo.query.filter_by(id=rent_id,user_id=current_user.id).first()
        user_bookRentInfo.return_date=date.today()
        book_id=user_bookRentInfo.book_id
        book=BookInfo.query.filter_by(id=book_id).first()
        book.stock+=1
        db.session.commit()
        flash(f'{book.book_name}을 반납했습니다.')
        return redirect('/main/book_return')
    rents=BookRentInfo.query.filter_by(user_id=current_user.id ,return_date=None)

    return render_template('book_return.html',book_rents=rents)