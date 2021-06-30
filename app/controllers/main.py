from functools import wraps
from app import app
from flask import render_template, flash, redirect, request, url_for, session
from app.forms.forms import LoginForm, CadastroForm, RecuperaSenhaForm, PostForm
from passlib.hash import sha256_crypt
from app import auth, db, storage
from werkzeug.utils import secure_filename

#bloqueando rota para usuário não logado
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('logged_in') == True:
            return f(*args, **kwargs)
        else:
            flash("Login necessário!", 'danger')
            #print(session)
            return redirect(url_for('login'))
    return wrap

@app.route("/home")
def index():
    return(render_template('index.html'))

@app.route("/cadastro", methods=['GET', 'POST'])
def cadastro():
    form = CadastroForm()
    if form.validate_on_submit():
        email = form.email.data
        nome = form.nome.data
        senha = sha256_crypt.encrypt(form.password.data)
        usuario = auth.create_user_with_email_and_password(email, form.password.data)
        auth.send_email_verification(usuario['idToken'])
        registro = {
            "nome": nome,
            "email": email,
            "senha": senha 
        }
        db.child("usuarios").push(registro)
        return redirect(url_for('login'))
    return(render_template('cadastro.html', form=form))


@app.route("/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        senha = form.password.data
        try:
            user = auth.sign_in_with_email_and_password(email, senha)
            user_info = auth.get_account_info(user['idToken'])
            if user_info['users'][0]['emailVerified'] == False:
                auth.send_email_verification(user['idToken'])
                flash("Confirmação do email necessária!", "danger")
                return render_template("login.html", form=form)
            else:
                session['useremail'] = email
                session['idToken'] = user['idToken']
                session['logged_in'] = True
                return redirect(url_for('publicar'))
        except:
            flash('Combinação usuario-senha incorreta!', 'danger')
            return(render_template('login.html', form=form))
    return(render_template('login.html', form=form))

@app.route("/recupera", methods=['GET', 'POST'])
def recuperasenha():
    form = RecuperaSenhaForm()
    if form.validate_on_submit():
        try:
            auth.send_password_reset_email(form.email.data)
            flash("Foi enviado um email para o processo de recuperação no endereço informado!", "success")
            return redirect("login")
        except:
            flash("O endereço de email fornecido não se encontra cadastrado em nosso sistema!", "danger")
            return render_template('esqueci-senha.html', form=form)
    return render_template('esqueci-senha.html', form=form)

@app.route("/publicar", methods=['GET', 'POST'])
@login_required
def publicar():
    form = PostForm()
    if form.validate_on_submit():
        titulo = form.titulo.data
        corpo = form.corpo.data
        imagem = form.foto.data
        img_nome = secure_filename(imagem.filename)
        storage.child(img_nome).put(imagem, session['idToken'])
        registro = {
            "titulo": titulo,
            "corpo": corpo,
            "imagem": storage.child(img_nome).get_url(session['idToken'])
        }
        db.child('postagem').push(registro, session['idToken'])
        flash('Postagem realizada com Sucesso!', 'success')
        return redirect(url_for('index'))
    return(render_template('publicar.html', form=form))


@app.route("/publicacoes")
def publicacoes():
    postagens = db.child("postagem").get(session['idToken']).val()
    lista = []
    for i in postagens:
        dicio = {}
        dicio = { 
            "titulo": postagens[i]['titulo'],
            "corpo": postagens[i]['corpo'],
            "imagem": postagens[i]['imagem']
        }
        lista.append(dicio)
    #print(lista)
    return(render_template('publicacoes.html', posts = lista))

@app.route("/logout")
def logout():
    session.clear()
    return(redirect(url_for('login')))