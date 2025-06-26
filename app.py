from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from docx import Document
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Colaborador(db.Model):
    __tablename__ = 'colaborador'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    base = db.Column(db.String)
    cargo = db.Column(db.String)
    patrimonio = db.Column(db.String)
    modelo = db.Column(db.String)
    imei = db.Column(db.String)
    numero = db.Column(db.String)

# Rota principal - Seleção do colaborador
@app.route('/')
def index():
    colaboradores = Colaborador.query.order_by(Colaborador.nome).all()
    return render_template('index.html', colaboradores=colaboradores)

# Rota do formulário completo
@app.route('/termo/<int:id>', methods=['GET', 'POST'])
def formulario_termo(id):
    colaborador = Colaborador.query.get_or_404(id)
    
    if request.method == 'POST':
        # Processar checklist
        # No seu método que processa o formulário, altere:
        respostas = {}
        for i in range(1, 25):
            respostas[f'sim{i}'] = '(X)' if request.form.get(f'sim{i}') else '( )'
            respostas[f'nao{i}'] = '(X)' if request.form.get(f'nao{i}') else '( )'
                
        # Gerar documento
        tipo_termo = request.form.get('tipo_termo')
        modelo = "Entrega.docx" if tipo_termo == "entrega" else "Devolução.docx"
        
        doc = Document(modelo)
        marcadores = {
            '{nome}': colaborador.nome,
            '{modelo}': colaborador.modelo,
            '{marca}': extrair_marca(colaborador.modelo),  # Extrai marca do modelo
            '{patrimonio}': colaborador.patrimonio,
            '{imei}': colaborador.imei,
            '{sim}': '(X)' if tem_linha_telefonica(colaborador.numero) else '( )',
            '{não}': '( )' if tem_linha_telefonica(colaborador.numero) else '(X)',
            '{cargo}': colaborador.cargo,
            '{local}': colaborador.base,
            '{info_adicionais}': request.form.get('info_adicionais', ''),
            '{data}': datetime.now().strftime('%d/%m/%Y')
        }
        marcadores.update(respostas)
        
        # Substitui no documento
        substituir_marcadores(doc, marcadores)
        
        nome_arquivo = f"Termo_{tipo_termo}_{colaborador.nome}.docx"
        doc.save(nome_arquivo)
        
        return send_file(nome_arquivo, as_attachment=True)
    
    return render_template('formulario_termo.html', colaborador=colaborador)

# Funções auxiliares
def tem_linha_telefonica(numero):
    return numero and numero.strip() not in ['', 'NÃO POSSUI', '-']

def extrair_marca(modelo):
    if 'galaxy' in modelo.lower(): return 'Samsung'
    if 'moto' in modelo.lower(): return 'Motorola'
    if 'iphone' in modelo.lower(): return 'Apple'
    return 'Outra'

def substituir_marcadores(doc, marcadores):
    for p in doc.paragraphs:
        for key, value in marcadores.items():
            if key in p.text:
                # Corrige a formatação dos checkboxes
                if key.startswith('sim') or key.startswith('nao'):
                    p.text = p.text.replace(f'{{{key}}}', value)
                else:
                    p.text = p.text.replace(key, str(value))
    
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in marcadores.items():
                    if key in cell.text:
                        # Corrige para checkboxes em tabelas
                        if key.startswith('sim') or key.startswith('nao'):
                            cell.text = cell.text.replace(f'{{{key}}}', value)
                        else:
                            cell.text = cell.text.replace(key, str(value))

if __name__ == '__main__':
    app.run(debug=True)