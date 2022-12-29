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


@app.route('/fotomodele', methods=['GET', 'POST'])
def fotomodele():
    if request.method == "GET":
        connection = mysql.connector.connect(host='127.0.0.1',
                                             database='modellingagency',
                                             user='root',
                                             password='petrut123#')
        cursor = connection.cursor()
        cursor.execute("SELECT nume, prenume, cnp, sex, denumire FROM fotomodel f, eveniment e, fotomodel_eveniment fe \
            WHERE e.id_eveniment = fe.id_eveniment AND f.id_fotomodel = fe.id_fotomodel \
                GROUP BY nume ORDER BY data DESC;")
        results = cursor.fetchall()

        cursor.execute(
            "SELECT f.nume, f.prenume, m.nume, m.prenume FROM fotomodel f, manager_personal m WHERE f.id_fotomodel = m.id_fotomodel;")
        results2 = cursor.fetchall()

        return render_template("fotomodele.html",  vector=results, vector3=results2)
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
                            query = f"INSERT INTO fotomodel (nume, prenume, cnp, sex, strada, numar, oras, judet) \
                                VALUES('{nume}', '{prenume}', '{cnp}', '{sex}', '{strada}', {numar}, '{oras}', '{judet}')"

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
        cursor = mysql1.connection.cursor()
        queryy = f"select denumire, cost, data, locatia, name from eveniment join event_category on id_ev_category = id_categ_eveniment"

        cursor.execute(queryy)
        results = cursor.fetchall()
        return render_template("elimina.html", vector2=results)
    else:

        cursor = mysql1.connection.cursor()
        eveniment = request.form['eveniment']

        query = f"SELECT cnp AS cnpp FROM fotomodel f, eveniment e, fotomodel_eveniment fe WHERE f.id_fotomodel = fe.id_fotomodel AND e.id_eveniment = fe.id_eveniment AND e.denumire = '{eveniment}'"
        cursor.execute(query)
        res = cursor.fetchone()

        if res:
            query2 = f"delete FROM fotomodel WHERE cnp IN \
                (SELECT cnpp FROM \
                    (SELECT cnp AS cnpp FROM fotomodel f, eveniment e, fotomodel_eveniment fe \
                        WHERE f.id_fotomodel = fe.id_fotomodel AND e.id_eveniment = fe.id_eveniment \
                            AND e.denumire = '{eveniment}') AS C);"
            cursor.execute(query2)
            mysql1.connection.commit()

            flash("The model was successfully removed!", category="success")
            return redirect(url_for("fotomodele"))
        else:
            flash(
                "The CNP could not be found in the database, please try again!", category="error")
            return render_template("elimina.html")


@app.route('/afisare', methods=['GET', 'POST'])
def afisare():
    if request.method == 'GET':
        cursor = mysql1.connection.cursor()
        query = f"select e.denumire, count(id_fotomodel) as nrFotomodele from eveniment e, fotomodel_eveniment fe where e.id_eveniment = fe.id_eveniment group by e.denumire order by count(id_fotomodel) desc, denumire;"

        cursor.execute(query)
        results = cursor.fetchall()
        return render_template("afisare.html", vector2=results)
    else:
        oras = request.form['oras']
        cursor = mysql1.connection.cursor()

        query = f"select f.nume, f.prenume, f.cnp, f.sex \
            from fotomodel f, manager_personal m \
                where f.id_fotomodel = m.id_fotomodel and m.oras = '{oras}';"

        cursor.execute(query)
        results = cursor.fetchall()

        query2 = f"select e.denumire, count(id_fotomodel) as nrFotomodele from eveniment e, fotomodel_eveniment fe where e.id_eveniment = fe.id_eveniment group by e.denumire order by count(id_fotomodel) desc, denumire;"

        cursor.execute(query2)
        results2 = cursor.fetchall()

        return render_template("afisare.html", vector=results, vector2=results2)


@app.route('/form1-handler', methods=['POST', 'GET'])
def form1_handler():
    an = request.form['an']
    an = int(an)
    cursor = mysql1.connection.cursor()
    query = f"SELECT nume, prenume, YEAR(data_angajare) AS an \
                FROM fotomodel f, contract c \
                WHERE f.id_fotomodel = c.id_fotomodel AND YEAR(data_angajare) > {an} \
                GROUP BY nume, prenume \
                ORDER BY YEAR(data_angajare) DESC"
    cursor.execute(query)
    results = cursor.fetchall()

    query3 = f"SELECT I.nume, I.prenume, I.salariu FROM \
        (SELECT f.nume, f.prenume, c.salariu FROM \
            fotomodel f, contract c WHERE f.id_fotomodel = c.id_fotomodel) AS I ORDER BY salariu DESC LIMIT 5;"
    cursor.execute(query3)
    results1 = cursor.fetchall()

    query2 = f"select year(data_angajare) as an, count(id_fotomodel) nrFot \
            from contract \
                group by year(data_angajare) \
                having count(id_fotomodel)=(select max(s.nrang) \
                from (select (count(id_fotomodel)) as nrang from contract group by year(data_angajare)) as s);"
    cursor.execute(query2)
    results3 = cursor.fetchall()

    return render_template("afisare2.html", vectan=results, vector=results1, vector3=results3)


@app.route('/form2-handler', methods=['POST'])
def form2_handler():
    salariu = request.form['salariu']
    salariu = int(salariu)
    cursor = mysql1.connection.cursor()

    query = f"SELECT f.id_fotomodel, f.nume, f.prenume \
            FROM fotomodel f WHERE EXISTS (SELECT id_fotomodel \
                FROM contract c WHERE c.salariu < {salariu} and c.id_fotomodel = f.id_fotomodel)"
    cursor.execute(query)
    results = cursor.fetchall()

    query3 = f"SELECT I.nume, I.prenume, I.salariu FROM \
        (SELECT f.nume, f.prenume, c.salariu FROM \
            fotomodel f, contract c WHERE f.id_fotomodel = c.id_fotomodel) AS I ORDER BY salariu DESC LIMIT 5;"
    cursor.execute(query3)
    results1 = cursor.fetchall()

    query2 = f"select year(data_angajare) as an, count(id_fotomodel) nrFot \
            from contract \
                group by year(data_angajare) \
                having count(id_fotomodel)=(select max(s.nrang) \
                from (select (count(id_fotomodel)) as nrang from contract group by year(data_angajare)) as s);"
    cursor.execute(query2)
    results3 = cursor.fetchall()

    return render_template("afisare2.html", vector4=results, vector=results1, vector3=results3)


@app.route('/statistici', methods=['GET', 'POST'])
def statistici():
    if request.method == 'GET':
        cursor = mysql1.connection.cursor()
        query = f"SELECT I.nume, I.prenume, I.salariu FROM \
            (SELECT f.nume, f.prenume, c.salariu FROM \
                fotomodel f, contract c WHERE f.id_fotomodel = c.id_fotomodel) AS I ORDER BY salariu DESC LIMIT 5;"
        cursor.execute(query)
        results1 = cursor.fetchall()

        query3 = f"select year(data_angajare) as an, count(id_fotomodel) nrFot \
            from contract \
                group by year(data_angajare) \
                having count(id_fotomodel)=(select max(s.nrang) \
                from (select (count(id_fotomodel)) as nrang from contract group by year(data_angajare)) as s);"
        cursor.execute(query3)
        results3 = cursor.fetchall()
        return render_template("afisare2.html", vector=results1, vector3=results3)


if __name__ == '__main__':
    app.secret_key = "i//g]naxtedsvcubzebogsks"
    app.run(debug=True)