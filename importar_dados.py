import gspread
from google.oauth2.service_account import Credentials
from app import app, db, Colaborador

# Configuração do Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(CREDS)

# Abre a planilha
sheet = client.open_by_key("1tcQ6Vp5mT7VugQHYyvk3fwSvleeAk_7VarNQU4uM_HM").sheet1

# Pega todos os dados
dados = sheet.get_all_records()

with app.app_context():
    for linha in dados:
        # Filtra apenas as colunas que precisamos
        colaborador = Colaborador(
            nome=linha["NOMES"],
            base=linha["BASES"],
            cargo=linha["DEPARTAMENTO"],
            patrimonio=linha["PATRIMONIO CELULAR"],
            modelo=linha["MODELO CELULAR"],
            imei=linha["IMEI"],
            numero=linha["NÚMERO CELULAR (CHIP)"]
        )
        db.session.add(colaborador)
    
    db.session.commit()
    print(f"Dados importados com sucesso! Total: {len(dados)} registros.")