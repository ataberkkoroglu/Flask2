from flask import Flask,render_template,flash,redirect,url_for,request,session
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

#Kullanıcı Giriş Decoratoru
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
           return f(*args, **kwargs)
        else:
            flash("Bu Sayfayı Görüntülemek İçin Lütfen Giriş Yapınız...","danger")
            return redirect(url_for("login"))
    return decorated_function
#Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name=StringField("İsim Soyisim",validators=[validators.Length(min=3,max=25)])
    username=StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)])
    e_mail=StringField("E-Mail Adresi",validators=
    [validators.Email(message="Lütfen E-Mail Adresinizi Giriniz.")])
    password=PasswordField("Şifreniz",validators= 
    [validators.DataRequired(message="Lütfen Şifrenizi Belirleyiniz."),validators.Length(min=6),validators.equal_to(fieldname="confirm",message="Mesajınız Uyuşmuyor...")])
    confirm=PasswordField("Parolayı Doğrula")
#Kullanıcı Giriş Formu
class Login(Form):
    Username=StringField("Kullanıcı Adınız",validators=
    [validators.Length(min=5,max=25),validators.equal_to(fieldname="username",message="Kullanıcı Adınız Yanlış")])
    Password=PasswordField("Şifreniz",validators=
    [validators.DataRequired(message="Lütfen Şifrenizi Giriniz."),validators.equal_to(fieldname="password",message="Kullanıcı  Şifreniz Yanlış...")])
#makale formu
class ArticleForm(Form):
   Title=StringField("Makalenin Adı",validators=[validators.Length(min=5,max=100)])
   Content=TextAreaField("Makalenin İçeriği",validators=[validators.Length(min=10,)])

app=Flask(__name__)
app.secret_key="ybblog"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_PASSWORD"]=""
app.config["MYSQL_DB"]="YB BLOG"
app.config["MYSQL_CURSORCLASS"]="DictCursor"

mysql=MySQL(app)
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def update(id):
   if request.method=="GET":
    Cursor=mysql.connection.cursor()
    sorgu=("Select * From articles Where Author=%s and Id=%s")
    Result=Cursor.execute(sorgu,(session["username"],id))
    if Result==0:
       flash("Böyle bir Makale Yok Veya Yetkiniz Yok.","danger")
       return redirect(url_for("home"))
    else: 
       Article=Cursor.fetchone()
       form=ArticleForm()
       form.Title.data=Article["Title"]
       form.Content.data=Article["Content"]
       return render_template("update.html",form=form)
   else:
      #Post Request
      form=ArticleForm(request.form)
      new_title=form.Title.data
      new_Content=form.Content.data
      Sorgu2=("Update articles set Title=%s,Content=%s Where Id=%s")
      Cursor=mysql.connection.cursor()
      Cursor.execute(Sorgu2,(new_title,new_Content,id))
      mysql.connection.commit()
      flash("Makale Başarıyla Güncellendi...","success")
      return redirect(url_for("dashboard"))
#Makale Silme

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    Cursor=mysql.connection.cursor()
    sorgu=("Select * From articles Where Author=%s and Id=%s")
    Result=Cursor.execute(sorgu,(session["username"],id))
    if Result>0:
        sorgu2=("Delete From articles Where Id=%s")
        Cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    else: 
       flash("Böyle Bir Makale Yok Veya Bu İşleme Yetkiniz Yok","danger")
       return redirect(url_for("home"))
@app.route("/")

#Ana Sayfa

def home():
    return render_template("index.html")
@app.route("/about")

#Hakkımızda Sayfası

def about():
    return render_template("about.html")

#Makaleler Sayfası

@app.route("/articles")
def article():
    cursor=mysql.connection.cursor()
    sorgu=("Select * From articles")
    result=cursor.execute(sorgu,)
    if result!=0:
        articles=cursor.fetchall()
        return render_template("article.html",articles=articles)
    elif result==0:
      return render_template("article.html")
#Kayıt Olma Sayfası
@app.route("/register",methods=["GET","POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST"and form.validate():
        name=form.name.data
        username=form.username.data
        mail=form.e_mail.data
        password=sha256_crypt.encrypt(form.password.data)
        cursor=mysql.connection.cursor()
        mysql.connection.commit()
        sorgu=("Insert into users(name,mail,Username,Password) VALUES(%s,%s,%s,%s)")
        cursor.execute(sorgu,(name,mail,username,password))
        mysql.connection.commit()
        sorgu2=("Select * From users where Username=%s")
        result=cursor.execute(sorgu2,(username,))
        if result !=0:
         flash("Başarıyla Kayıt Oldunuz...",category="success") 
         return redirect(url_for("login"))
        else:
            flash(message="Kayıt Gerçekleştirilemedi...Lütfen Tekrar Deneyiniz.",category="danger")
            return redirect(url_for("register"))
        
    else:
        return render_template("register.html",form=form)

#Giriş Yapma Sayfası

@app.route("/login",methods=["GET","POST"])
def login():
    form=Login(request.form)
    if request.method=="POST":
        Username=form.Username.data
        Password2=form.Password.data
        cursor=mysql.connection.cursor()
        sorgu=("Select * From users where Username=%s")
        result=cursor.execute(sorgu,(Username,))
        if result !=0:
            data=cursor.fetchone()
            real_password=data["Password"]
            if sha256_crypt.verify(Password2,real_password):
                flash("Başarıyla Giriş Yaptınız...",category="success")
                session["logged_in"]=True
                session["username"]=Username
                return redirect(url_for("home"))
            else:
                flash("Lütfen Bilgilerinizi Kontrol Ediniz...",category="danger")
                return redirect(url_for("login"))
        elif result==0:
            flash("Kullanıcı Bulunamadı.",category="danger")
            return redirect(url_for("login"))
    else:
        return render_template("login.html",form=form)
#Detaylar Sayfası
@app.route("/articles/<string:id>")
def detail(id):
    cursor=mysql.connection.cursor()
    sorgu=("Select * From articles where Id=%s")
    result=cursor.execute(sorgu,(id,))
    if result>0:
       article=cursor.fetchone()
       return render_template("articles.html",article=article)
    else:
      return render_template("article.html")

#Çıkış Yapma Sayfası

@app.route("/logout")
def logout():
    session.clear()
    flash("Çıkış Yaptınız...","success")
    return render_template("index.html")

#Kontrol Paneli Sayfası

@app.route("/dashboard")
@login_required
def dashboard():
    cursor=mysql.connection.cursor()
    sorgu=("Select * From articles where Author=%s")
    result=cursor.execute(sorgu,(session["username"],))
    if(result>0):
        articles=cursor.fetchall()
        return render_template("dashboard.html",articles=articles)
    else:
       return render_template("dashboard.html")

#Makale Ekleme

@app.route("/addArticle",methods=["GET","POST"])
def AddArticle():
    form=ArticleForm(request.form)
    if request.method=="POST" and form.validate():
        title=form.Title.data
        content=form.Content.data
        cursor=mysql.connection.cursor()
        sorgu=("Insert into articles(Title,Author,Content) Values(%s,%s,%s)")
        cursor.execute(sorgu,(title,session["username"],content))
        mysql.connection.commit()
        cursor.close()
        flash("Makale Başarıyla Eklendi.","success")
        return redirect(url_for("dashboard"))
    else:
     return render_template("AddArticle.html",form=form)
#Arama
@app.route("/search", methods=["GET","POST"])
def Search():
    if request.method=="POST":
        keyword=request.form.get("keyword")
        Cursor=mysql.connection.cursor()
        sorgu=("Select * From articles where Title like '%" + keyword +"%' ")
        Result=Cursor.execute(sorgu,)
        if Result==0:
            flash("Makale Bulunmuyor.","warning")
            return redirect(url_for("articles"))
        else:
          articles=Cursor.fetchall()
          return render_template("article.html",articles=articles)
    else:
        return redirect(url_for("home"))
if __name__=="__main__":
 app.run(debug=True)