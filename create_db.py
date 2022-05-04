import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="pass1234",
    database="cs424"
    )

my_cursor = mydb.cursor()

# q1 = "CREATE TABLE Like (id int PRIMARY KEY AUTO_INCREMENT, date_created DATETIME, author VARCHAR(255), post_id int, FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post (PostID))"
# q1 = "ALTER TABLE Rating ADD vote VARCHAR(255);"
q1 = "CREATE TABLE Downvotes (id int PRIMARY KEY AUTO_INCREMENT, date_created DATETIME NOT NULL, author VARCHAR(150) NOT NULL, post_id INT NOT NULL, vote VARCHAR(255), FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post(PostID));"
print(q1)

q1 = "CREATE DATABASE cs491"
q2 = "Create Table user(username VARCHAR(255) PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, password VARCHAR(255) NOT NULL, first_name VARCHAR(255) NOT NULL, last_name VARCHAR(255) NOT NULL, login_count INT NOT NULL, last_login_date DATETIME NOT NULL)"

q3 = "CREATE TABLE Post(PostID INT PRIMARY KEY AUTO_INCREMENT, subject VARCHAR(255) NOT NULL, content VARCHAR(255) NOT NULL, author VARCHAR(255) NOT NULL, date_created DATETIME NOT NULL, FOREIGN KEY (author) REFERENCES User(username))"
q4 = "CREATE TABLE Tag (TagID INT PRIMARY KEY AUTO_INCREMENT, tag VARCHAR(255), PostID INT NOT NULL, FOREIGN KEY (PostID) REFERENCES Post(PostID))"

q5 = "CREATE TABLE Comment(id INT PRIMARY KEY AUTO_INCREMENT, text VARCHAR(255) NOT NULL, date_created DATETIME NOT NULL, author VARCHAR(255) NOT NULL, post_id INT NOT NULL, FOREIGN KEY (author) REFERENCES User(username), FOREIGN KEY (post_id) REFERENCES Post(PostID))"

print(q2)

my_cursor.execute(q5)
