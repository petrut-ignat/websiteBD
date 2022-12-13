from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_mysqldb import MySQL, MySQLdb
from pymysql import cursors
import bcrypt
import sqlite3
import mysql.connector


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'petrut123#'
app.config['MYSQL_DB'] = 'modellingagency'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql1 = MySQL(app)
# mysql1.init_app(app)


@app.route('/', methods=['POST', 'GET'])
def home():

    connection = mysql.connector.connect(host='127.0.0.1',
                                         database='modellingagency',
                                         user='root',
                                         password='petrut123#')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM fotomodel")
    results = cursor.fetchall()

    return render_template('home.html', vector=results)


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template("sign_up.html")
    else:
        name = request.form['FirstName']
        if len(name) < 3:
            flash("Name must not be less than 3 characters!", category="error")
            return render_template("sign_up.html")
        email = request.form['email']

        cur = mysql1.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email, ))
        user = cur.fetchone()
        cur.close()

# daca nu se gaseste in baza de date niciun utilizator cu email-ul introdus, putem realiza "inscrierea"
        if not user:
            password1 = request.form['password1'].encode('utf-8')
            password2 = request.form['password2'].encode('utf-8')
            if password1 != password2:
                flash("Passwords don't match!", category="error")
                return render_template("sign_up.html")
            else:
                hash_password = bcrypt.hashpw(password1, bcrypt.gensalt())

                cur = mysql1.connection.cursor()
                cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                            (name, email, hash_password))
                mysql1.connection.commit()
                session['name'] = name
                session['email'] = email
                flash("Signed up!", category="success")
                return redirect(url_for("home"))
        else:
            flash(
                "This email already exists in our database, please login!", category="error")
            return render_template("sign_up.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql1.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM users WHERE email = %s", (email, ))
        user = cur.fetchone()
        cur.close()

        if user:
            if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                flash('You\'re succesfully logged in!', category='success')
                return redirect(url_for("home"))
            else:
                flash('Incorrect password, try again!', category='error')
                return render_template("login.html")
        else:
            flash('Email not found, please sign up!', category='error')
            return render_template("login.html")

    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))
    # return render_template("home.html")


@app.route('/fotomodele', methods=['GET', 'POST', 'POST'])
def fotomodele():
    if request.method == "GET":
        connection = mysql.connector.connect(host='127.0.0.1',
                                             database='modellingagency',
                                             user='root',
                                             password='petrut123#')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM fotomodel;")
        results = cursor.fetchall()
        return render_template("fotomodele.html",  vector=results)
    else:
        connection = mysql.connector.connect(host='127.0.0.1',
                                             database='modellingagency',
                                             user='root',
                                             password='petrut123#')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM fotomodel;")
        results = cursor.fetchall()

        nume = request.form['nume']
        prenume = request.form['prenume']
        cnp = request.form['cnp']
        sex = request.form['sex']
        strada = request.form['strada']
        numar = request.form['numar']
        oras = request.form['oras']
        judet = request.form['judet']
        if not numar:
            flash("Invalid street number!", category="error")
            return render_template("fotomodele.html",  vector=results)
        else:
            numar = int(float(numar))
            print("sex: ", sex, "-> ", type(sex), len(sex), "->", sex == "M")
            if sex == "M" or sex == "F":
                if len(nume) < 3 or len(prenume) < 3:
                    flash(
                        "First and last name must not be less than 3 characters!", category="error")
                    return render_template("fotomodele.html",  vector=results)
                else:
                    if len(cnp) < 13 or len(cnp) > 13:
                        flash("CNP invalid!", category="error")
                        return render_template("fotomodele.html",  vector=results)
                    else:
                        if len(strada) < 3 or len(oras) < 3 or len(judet) < 3 or numar < 0:
                            flash("Invalid address!", category="error")
                            return render_template("fotomodele.html",  vector=results)
                        else:
                            query = f"INSERT INTO fotomodel (nume, prenume, cnp, sex, strada, numar, oras, judet) VALUES('{nume}', '{prenume}', '{cnp}', '{sex}', '{strada}', {numar}, '{oras}', '{judet}')"

                            cur = mysql1.connection.cursor()
                            cur.execute(query)
                            mysql1.connection.commit()

                            flash("Fotomodel adaugat cu succes!",
                                  category="success")
                            # return redirect(url_for("fotomodele"))
                            return render_template("fotomodele.html",  vector=results)
            else:
                flash("You must select the gender!", category="error")
                return render_template("fotomodele.html",  vector=results)


@app.route('/elimina', methods=['GET', 'POST'])
def elimina():
    if request.method == "GET":
        return render_template("elimina.html")
    else:
        cursor = mysql1.connection.cursor()
        cnp = request.form['cnp']

        query2 = f"SELECT * FROM fotomodel WHERE cnp = '{cnp}'"
        cursor.execute(query2)
        res = cursor.fetchone()
        if res:
            if len(cnp) == 13:
                query = f"DELETE FROM fotomodel WHERE cnp = '{cnp}'"
                cursor.execute(query)
                mysql1.connection.commit()
                
                flash("The model was successfully removed!", category="success")
                return redirect(url_for("fotomodele"))
            else:
                flash("CNP must be 13 characters long!", category="error")
                return render_template("elimina.html")
        else:
            flash("The CNP could not be found in the database, please try again!", category="error")
            return render_template("elimina.html")


if __name__ == '__main__':
    app.secret_key = "i//g]naxtedsvcubzebogsks"
    app.run(debug=True)
