from flask import render_template, url_for, redirect, request
from SiteCozinha import app, database, bcrypt
from flask_login import login_required, login_user, logout_user, current_user
from SiteCozinha.forms import FormLogin, FormCriarConta
from SiteCozinha.models import Usuario, Foto
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime
from werkzeug.utils import secure_filename

@app.route("/", methods =["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("dashboard"))
    return render_template("homepage.html", form=form_login)

@app.route("/criarconta", methods =["GET", "POST"])
def criarconta():
    form_criarconta = FormCriarConta()
    if form_criarconta.validate_on_submit():
        senha = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, senha=senha, email=form_criarconta.email.data)

        database.session.add(usuario)
        database.session.commit()

        login_user(usuario, remember=True)
        return redirect(url_for("homepage"))

    return render_template("criarconta.html", form=form_criarconta)
"""
@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    return render_template("perfil.html", usuario = Usuario)
"""

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))



# Carregar os dados do CSV para o dashboard
df = pd.read_csv('pedidos_marmitas.csv')

# Função para filtrar os dados
def filtrar_dados(data_inicial, data_final, refeicao):
    df_filtrado = df.copy()
    df_filtrado['data'] = pd.to_datetime(df_filtrado['data'])
    df_filtrado['horario'] = pd.to_datetime(df_filtrado['horario'], format='%H:%M:%S').dt.time
    
    if data_inicial and data_final:
        df_filtrado = df_filtrado[(df_filtrado['data'] >= data_inicial) & (df_filtrado['data'] <= data_final)]
    
    if refeicao == 'almoço':
        df_filtrado = df_filtrado[df_filtrado['horario'] <= datetime.strptime('14:30:00', '%H:%M:%S').time()]
    elif refeicao == 'janta':
        df_filtrado = df_filtrado[df_filtrado['horario'] > datetime.strptime('14:30:00', '%H:%M:%S').time()]

    return df_filtrado

# Rota para o painel com filtros, protegida por login
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    data_inicial = request.form.get('data_inicial')
    data_final = request.form.get('data_final')
    refeicao = request.form.get('refeicao')
    
    if data_inicial and data_final:
        data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
        data_final = datetime.strptime(data_final, '%Y-%m-%d')

    df_filtrado = filtrar_dados(data_inicial, data_final, refeicao)
    
    # Gráfico 1: Quantidade de marmitas por horário
    pedidos_por_horario = df_filtrado.groupby(df_filtrado['horario'].apply(lambda x: x.hour)).size().reset_index(name='quantidade')
    pedidos_por_horario.columns = ['horario', 'quantidade']
    fig1 = px.bar(pedidos_por_horario, x='horario', y='quantidade', title='Quantidade de Marmitas por Horário')
    grafico_horario = pio.to_html(fig1, full_html=False)

    # Gráfico 2: Quantidade de marmitas por tipo
    pedidos_por_tipo = df_filtrado['tipo_pedido'].value_counts().reset_index()
    pedidos_por_tipo.columns = ['tipo_pedido', 'quantidade']
    fig2 = px.bar(pedidos_por_tipo, x='tipo_pedido', y='quantidade', title='Quantidade de Marmitas por Tipo')
    grafico_tipo = pio.to_html(fig2, full_html=False)

    # Gráfico 3: Quantidade de opções (doce e fruta)
    opcoes = ['opcao_doce', 'opcao_fruta']
    dados_opcoes = {opcao: df_filtrado[opcao].value_counts().get('Sim', 0) for opcao in opcoes}
    df_opcoes = pd.DataFrame(list(dados_opcoes.items()), columns=['opcao', 'quantidade'])
    fig3 = px.pie(df_opcoes, names='opcao', values='quantidade', title='Distribuição de Doce e Fruta')
    grafico_opcoes = pio.to_html(fig3, full_html=False)

    return render_template('dashboard.html', grafico_horario=grafico_horario,
                           grafico_tipo=grafico_tipo, grafico_opcoes=grafico_opcoes)