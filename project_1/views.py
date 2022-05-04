from turtle import title
from unicodedata import category
import mysql.connector
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from . import db, mail, bcrypt
from .models import Post, Tag, User, Comment, Rating, Downvote
from datetime import datetime, timedelta
from .forms import RequestResetForm, ResetPasswordForm
from flask_mail import Message

from flask_sqlalchemy import SQLAlchemy

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    posts = Post.query.all()
    tags = Tag.query.all()
    
    return render_template("home.html", user=current_user, posts=posts, tags=tags)

@views.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method =='POST':
        subject = request.form.get('subject')
        content = request.form.get('content')
        tagString = request.form.get('tag')
        tags = tagString.split(", ")
        print(subject)
        print(content)
        print(tagString)
        print(tags)
        print(current_user)

        posts = Post.query.all()
        date = datetime.now()
        t = timedelta(days=1)
        count = 0

        #Check for all posts that were created by the current user less than 1 day ago.
        for post in posts:
            if (post.author == current_user.username):
                if (date - post.date_created) < t:
                    count = count + 1

        
        if not subject:
            flash('Subject cannot be empty', category='error')
        elif not content:
            flash('Content cannot be left empty', category='error')
        elif count > 2:
            flash('Can not make more than 2 posts per day.', category='error')
        else:
            
            if not tagString:
                post = Post(subject=subject, content=content, author=current_user.username)
                db.session.add(post)
                db.session.commit()
                flash('Post created', category='success')
                return redirect(url_for('views.home'))
            else:
                post = Post(subject=subject, content=content, author=current_user.username)
                db.session.add(post)
                db.session.commit()
                tags = tagString.split(", ")

                for tag in tags:
                    new_tag = Tag(tag=tag, PostID=post.PostID)
                    db.session.add(new_tag)
                    db.session.commit() 
                flash('Post created', category='success')   
                return redirect(url_for("views.home"))

    return render_template("create_post.html", user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(PostID=id).first()

    if not post:
        flash("Post does not exist.", category='error')
        
    elif current_user.username != post.author:
        flash('You do not have permission to delete this post.', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category='success')

    return redirect(url_for('views.home'))

@views.route("/posts/<username>")
@login_required
def posts(username):
    
    user = User.query.filter_by(username=username).all()

    if not user:
        flash('User does not exist.', category='error')
        return redirect(url_for('views.home'))

    posts = Post.query.filter_by(author=username).all()
    tags = Tag.query.all()
    return render_template("posts.html", user=current_user, posts=posts, username=username, tags=tags)

@views.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('text')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(PostID=post_id)

        comments = Comment.query.filter_by(post_id=post_id)
        postCommentCount = 0
        for comment in comments:
            if current_user.username == comment.author:
                postCommentCount = postCommentCount + 1
        
        allComments = Comment.query.all()
        date = datetime.now()
        t = timedelta(days=1)
        totalCommentCount = 0

        #Check for all comments that were created by the current user less than 1 day ago.
        for comment in allComments:
            if (comment.author == current_user.username):
                if (date - comment.date_created) < t:
                    totalCommentCount = totalCommentCount + 1
        

        if postCommentCount > 0:
            flash('You cannot make more than 1 comment per post.', category='error')
        elif totalCommentCount > 2:
            flash('You can only make 3 comments per day.', category='error')
        elif post:
            comment = Comment(text=text, author=current_user.username, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')


    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist', category='error')
    elif current_user.username != comment.author and current_user.username != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.home'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('views.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.

    '''

@views.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info' )
        return redirect(url_for('views.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@views.route('reset_password/<token>', methods=['GET', 'Post'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    user = User.verify_reset_token(token)

    if user is None:
        flash('Token has expired', category='error')
        return redirect(url_for('views.reset_request'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has now been updated!', category='success')
        return redirect(url_for('views.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

@views.route("/like-post/<postid>", methods=['GET'])
@login_required
def like(postid):
    post = Post.query.filter_by(PostID=postid)
    rating = Rating.query.filter_by(author=current_user.username, post_id=postid,).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif rating:
        db.session.delete(rating)
        db.session.commit()
    else:
        rating = Rating(author=current_user.username, post_id=postid, vote='like')
        db.session.add(rating)
        db.session.commit()

    return redirect(url_for('views.home'))


@views.route("/dislike-post/<postid>", methods=['GET'])
@login_required
def dislike(postid):
    post = Post.query.filter_by(PostID=postid)
    rating = Downvote.query.filter_by(author=current_user.username, post_id=postid,).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif rating:
        db.session.delete(rating)
        db.session.commit()
    else:
        rating = Downvote(author=current_user.username, post_id=postid, vote='dislike')
        db.session.add(rating)
        db.session.commit()

    return redirect(url_for('views.home'))




# Replace this with downloading the confidential file
@views.route('/initialize-db', methods=['GET', 'POST'])
@login_required
def initDB():

    if request.method == 'POST':
        print("Testing passed")
        rejected = True
        response = ''

        try:
            
            mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="pass1234",
            database="users"
            )

            cursor = mydb.cursor()
           
            #sql will holde the sql statement
            sql = ''
            
            # waiting is if we are waiting to see a ';' to indicate the statement end.
            waiting = False
            for line in open('/Users/Luis Garcia/OneDrive/Desktop/cs491/project_1/sql/university.sql'):
                print("File was oppened")
                # Strip the line of the new line character, '\n'
                line = line.strip()

                # Is this just an empty line?
                if line == '':
                    # Yep, move on.
                    continue
                elif line[0] == '-' or line[0] == '/':
                    # We have a comment here, move on
                    continue
                elif line[len(line)-1] == ';' and waiting:
                    # We've been waiting for the end of statement character, ';'
                    # and now we've found it
                    waiting = False         # Set waiting to false
                    sql = sql + line        # Add the last line to the statement
                    print(sql)              # Output the statement to the terminal
                    cursor.execute(sql)     # Execute the statement
                    sql = ''                # Reset our sql variable
                    continue                # Move on with the for loop
                elif len(line) > 6:
                    # Is the length of the line > 6 (since we want to check up to index 5)?
                    if line[0] == 'C' and line[1] == 'R' and line[2] == 'E' and line[3] == 'A' and line[4] == 'T' and line[5] == 'E':
                        # Yep, did the first 5 char spell create? Yep!
                        # We're making a new table then
                        waiting = True      # Set waiting to true.
                        sql = sql + line    # Add the line to the sql variable
                        continue            # Move on with the for loop
                    elif waiting:
                        # The length is indeed longer, but we're not a create statement
                        # and we are waiting to be executed
                        sql = sql + line    # Add the line to the sql variable
                        continue            # Move on with the for loop
                    else:
                        # The length is indeed longer, but we're not waiting either
                        # Print and execute the command and continue on
                        print('Here')
                        print(line)
                        cursor.execute(line)
                        continue
                elif waiting:
                    # None of the above are true, but we're waiting
                    sql = sql + line        # Add the line to the sql variable
                    continue                # Move on with the for loop
                # Nothing above was true, and we're not waiting for an ';'
                # Print the command and execute it.
                print('Here')
                print(line)
                cursor.execute(line)
            # Create our response to the client and return it
            # message = {
            #     'status': 200,
            #     'message': 'Database successfully initialized!',
            # }
            # response = jsonify(message)
            # response.status_code = 200
            # return response
            flash('Database created', category='success')
        except Exception as e:
            # Was there some error in our code above?
            # Print it out to the terminal so we can try and debug it
            print(e)
        finally:
            if rejected == False:
                # If we've made it here, then we successfully executed out try
                # Now we can close our cursor and connection
                cursor.close()
                # conn.close()

    return render_template('initialize_db.html', user=current_user)








# FROM HERE DOWN IS NOT REQUIRED!!!!!!!!

@views.route('/queries', methods=['GET'])
@login_required
def queries():

    return render_template('queries.html', user=current_user)

@views.route("/query1", methods=['GET', 'POST'])
@login_required
def query1():
    x = request.form.get('tag_x')
    print(x)
    

    users = User.query.all()
    return render_template('query1.html', user=current_user, users=users, x=x)

@views.route("/query2", methods=['GET'])
@login_required
def query2():
    users = User.query.all()
    return render_template('query2.html', user=current_user, users=users)

@views.route("/query3", methods=['GET'])
@login_required
def query3():
    users = User.query.all()
    return render_template('query3.html', user=current_user, users=users)

@views.route("/query4", methods=['GET'])
@login_required
def query4():
    users = User.query.all()
    return render_template('query4.html', user=current_user, users=users)

@views.route("/query5", methods=['GET'])
@login_required
def query5():
    users = User.query.all()
    return render_template('query5.html', user=current_user, users=users)


@views.route("/query6", methods=['GET'])
@login_required
def query6():
    users = User.query.all()
    return render_template('query6.html', user=current_user, users=users)

@views.route("/query7", methods=['GET'])
@login_required
def query7():
    users = User.query.all()
    return render_template('query7.html', user=current_user, users=users)

@views.route("/query8", methods=['GET'])
@login_required
def query8():
    users = User.query.all()
    return render_template('query8.html', user=current_user, users=users)

@views.route("/query9", methods=['GET'])
@login_required
def query9():
    users = User.query.all()
    return render_template('query9.html', user=current_user, users=users)
