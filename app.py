from flask import Flask, render_template, request, url_for, redirect, session
from sqlite3 import *
import pickle

app = Flask(__name__)
app.secret_key = "lender"
@app.route("/")
def home():
	return render_template("home.html")
@app.route("/login", methods = ["POST","GET"])
def login():
	if request.method == "POST":
		un = request.form["un"]
		pw = request.form["pw"]
		con = None
		try:
			con = connect("lender.db")
			cursor = con.cursor()
			sql = "select * from users where username = '%s' and password = '%s'"
			cursor.execute(sql%(un,pw))
			data = cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html",msg = "Invalid Login")
			else:
				session["username"] = un
				return redirect(url_for("predict"))
		except Exception as e:
			return render_template("login.html",msg = e)
		finally:
			if con is not None:
				con.close()
	return render_template("login.html")
@app.route("/signup", methods = ["POST","GET"])
def signup():
	if request.method == "POST":
		un = request.form["un"]
		pw1 = request.form["pw1"]
		pw2 = request.form["pw2"]
		if pw1 == pw2:
			con = None
			try:
				con = connect("lender.db")
				cursor = con.cursor()
				sql = "insert into users values('%s','%s')"
				cursor.execute(sql%(un,pw1))
				con.commit()
				return redirect(url_for("login"))
			except Exception as e:
				con.rollback()
				return render_template("signup.html",msg = "user already exists")
			finally:
				if con is not None:
					con.close
		else:
			return render_template("signup.html",msg = "password did not match")
	else:
		return render_template("signup.html")
	return render_template("signup.html")
@app.route("/find_eligibilty",methods = ['GET','POST'])
def predict():
	if request.method == "POST":
		gen = request.form.get("gender")
		if gen == "f":
			g = 0
		else:
			g = 1
		marr = request.form.get("ms")
		if marr == "um":
			m = 1
		else:
			m = 0
		d = int(request.form["dep"])
		edustat = request.form.get("edu")
		if edustat == "grad":
			e = 0
		else:
			e = 1
		selfemp = request.form.get("se")
		if selfemp == "y":
			se = 1
		else:
			se = 0
		i = float(request.form["inc"])
		ci = float(request.form["coinc"])
		l = float(request.form["la"])
		per = int(request.form["lat"])
		credit = request.form.get("ch")
		if credit == "p":
			cr = 1			
		elif credit == "up":
			cr = 0
		elif credit == "pp":
			cr = 0.842198582
		ar = request.form.get("ps")
		data = []
		if ar == "ru":
			data = [[g,m,d,e,se,i,ci,l,per,cr,0,0]]	
		elif ar == "su":
			data = [[g,m,d,e,se,i,ci,l,per,cr,1,0]]
		elif ar == "u":
			data = [[g,m,d,e,se,i,ci,l,per,cr,0,1]]
		with open("RF.model","rb") as f:
			model = pickle.load(f)
		t = model.predict(data)
		op = t[0]
		if op == 0:
			msg = "Unfortunately loan cannot be granted :("
		elif op == 1:
			msg = "Congrats! Applicant is eligible for loan" 
		return render_template('predict.html',msg = msg)
	else:
		return render_template("predict.html")
if __name__=="__main__":
	app.run(debug = True,use_reloader = True)