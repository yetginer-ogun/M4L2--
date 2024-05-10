# İçe aktar
from flask import Flask, render_template,request, redirect, session, flash
# Veri tabanı kitaplığını bağlama
from flask_sqlalchemy import SQLAlchemy
from functools import wraps


app = Flask(__name__)
# SQLite'ı bağlama
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary_yeni.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Veri tabanı oluşturma
db = SQLAlchemy(app)
# Tablo oluşturma


app.secret_key = "DENEME"
#Kullanıcı Giriş Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfaya erişmek için giriş yapmalısınız")
            return redirect("/")
    return decorated_function


class Card(db.Model):
    # Sütun oluşturma
    # id
    id = db.Column(db.Integer, primary_key=True)
    # Başlık
    title = db.Column(db.String(100), nullable=False)
    # Tanım
    subtitle = db.Column(db.String(300), nullable=False)
    # Metin
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    # Nesnenin ve kimliğin çıktısı
    def __repr__(self):
        return f'<Card {self.id}>'
    

#Ödev #2. Kullanıcı tablosunu oluşturun
class User(db.Model):
	# Sütunlar oluşturuluyor
	#id
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	# Giriş
	email = db.Column(db.String(100), nullable=False)
	# Şifre
	password = db.Column(db.String(30), nullable=False)





# İçerik sayfasını çalıştırma
@app.route('/', methods=['GET','POST'])
def login():
        error = ''
        if request.method == 'POST':
            form_login = request.form['email']
            form_password = request.form['password']
            
            #Ödev #4. yetkilendirmeyi uygulamak
            users_db = User.query.all()
            for user in users_db:
                if form_login == user.email and form_password == user.password:
                    session["logged_in"] = True #session başlat
                    session["email"] = user.email
                    session["id"] = user.id
                    return redirect('/index')
            else:
                error = 'Hatalı giriş veya şifre'
                return render_template('login.html', error=error)


            
        else:
            return render_template('login.html')



@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        email= request.form['email']
        password = request.form['password']
        
        #Ödev #3 Kullanıcı verilerinin veri tabanına kaydedilmesini sağlayın
        kullanıcı = User(email=email, password=password)
        db.session.add(kullanıcı)
        db.session.commit()

        
        return redirect('/')
    
    else:    
        return render_template('registration.html')


# İçerik sayfasını çalıştırma
@app.route('/index')
@login_required
def index():
    # Veri tabanı girişlerini görüntüleme
    cards = Card.query.filter_by(user_id=session["id"]).order_by(Card.id).all()
    return render_template('index.html', cards=cards)


# Kayıt sayfasını çalıştırma
@app.route('/card/<int:id>')
@login_required
def card(id):
    card = Card.query.get(id)
    return render_template('card.html', card=card)


# Giriş oluşturma sayfasını çalıştırma
@app.route('/create')
@login_required
def create():
    print(session)
    print(session["id"])
    return render_template('create_card.html')


# Giriş formu
@app.route('/form_create', methods=['GET','POST'])
@login_required
def form_create():
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']
        user_id = session["id"]
        # Veri tabanına gönderilecek bir nesne oluşturma
        card = Card(title=title, subtitle=subtitle, text=text, user_id=user_id)
        
        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')


#Çıkış
@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Başarıyla çıkış yaptınız")
    return redirect("/")


#Kart silme 
@app.route("/card_delete/<int:id>")
def card_delete(id):
    card = Card.query.filter_by(id=id).first()
    db.session.delete(card)
    db.session.commit()
    flash("Kart başarıyla silindi")
    return redirect("/index")


if __name__ == "__main__":
    with app.app_context():
         db.create_all()
    app.run(debug=True)
