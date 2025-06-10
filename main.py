import sqlite3
import csv
import json
from datetime import datetime

conn = sqlite3.connect('vida_mais.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS medicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    crm TEXT,
    especialidade TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cpf TEXT,
    data_nascimento TEXT,
    telefone TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id INTEGER,
    medico_id INTEGER,
    data TEXT,
    observacoes TEXT,
    FOREIGN KEY(paciente_id) REFERENCES pacientes(id),
    FOREIGN KEY(medico_id) REFERENCES medicos(id)
)''')
conn.commit()


def importar_medicos_csv():
    with open('medicos.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cursor.execute('''
                INSERT INTO medicos (nome, crm, especialidade)
                VALUES (?, ?, ?)
            ''', (row['nome'], row['crm'], row['especialidade']))
    conn.commit()

def importar_pacientes_json():
    with open('pacientes.json', 'r', encoding='utf-8') as jsonfile:
        pacientes = json.load(jsonfile)
        for p in pacientes:
            cursor.execute('''
                INSERT INTO pacientes (nome, cpf, data_nascimento, telefone)
                VALUES (?, ?, ?, ?)
            ''', (p['nome'], p['cpf'], p['data_nascimento'], p['telefone']))
    conn.commit()

def cadastrar_medico():
    nome = input("Nome do médico: ")
    crm = input("CRM: ")
    esp = input("Especialidade: ")
    cursor.execute("INSERT INTO medicos (nome, crm, especialidade) VALUES (?, ?, ?)", (nome, crm, esp))
    conn.commit()
    print("Médico cadastrado com sucesso.")

def cadastrar_paciente():
    nome = input("Nome do paciente: ")
    cpf = input("CPF: ")
    nascimento = input("Data de nascimento (DD/MM/YYYY): ")
    telefone = input("Telefone: ")
    cursor.execute("INSERT INTO pacientes (nome, cpf, data_nascimento, telefone) VALUES (?, ?, ?, ?)",
                   (nome, cpf, nascimento, telefone))
    conn.commit()
    print("Paciente cadastrado com sucesso.")

def agendar_consulta():
    paciente_id = input("ID do paciente: ")
    medico_id = input("ID do médico: ")
    data = input("Data da consulta (DD/MM/YYYY): ")
    try:

        data_formatada = datetime.strptime(data, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        print("Data inválida. Use o formato DD/MM/YYYY.")
        return
    obs = input("Observações: ")
    cursor.execute("INSERT INTO consultas (paciente_id, medico_id, data, observacoes) VALUES (?, ?, ?, ?)",
                   (paciente_id, medico_id, data_formatada, obs))
    conn.commit()
    print("Consulta agendada.")

def listar_consultas_paciente():
    paciente_id = input("ID do paciente: ")
    cursor.execute('''
        SELECT c.id, c.data, m.nome, c.observacoes
        FROM consultas c
        JOIN medicos m ON c.medico_id = m.id
        WHERE c.paciente_id = ?
    ''', (paciente_id,))
    resultados = cursor.fetchall()

    if resultados:
        for r in resultados:
            try:
                data_formatada = datetime.strptime(r[1], "%Y-%m-%d").strftime("%d/%m/%Y")
            except ValueError:
                data_formatada = r[1]  # Exibe como está se a conversão falhar
            print(f"ID: {r[0]}, Data: {data_formatada}, Médico: {r[2]}, Obs: {r[3]}")
    else:
        print("Nenhuma consulta encontrada.")

def relatorio_consultas():
    cursor.execute('''
        SELECT m.nome, COUNT(c.id) as total
        FROM consultas c
        JOIN medicos m ON c.medico_id = m.id
        GROUP BY m.id
    ''')
    resultados = cursor.fetchall()
    for r in resultados:
        print(f"Médico: {r[0]} | Total de consultas: {r[1]}")

def exportar_csv():
    cursor.execute('''
        SELECT m.nome, COUNT(c.id) as total
        FROM consultas c
        JOIN medicos m ON c.medico_id = m.id
        GROUP BY m.id
    ''')
    resultados = cursor.fetchall()
    with open('relatorio_consultas.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Médico', 'Total de Consultas'])
        writer.writerows(resultados)
    print("Relatório exportado para 'relatorio_consultas.csv'.")

def menu():
    while True:
        print("\n=== Clínica Popular Vida+ ===")
        print("1. Importar médicos do CSV")
        print("2. Importar pacientes do JSON")
        print("3. Cadastrar médico")
        print("4. Cadastrar paciente")
        print("5. Agendar consulta")
        print("6. Listar consultas de paciente")
        print("7. Relatório: consultas por médico")
        print("8. Exportar relatório CSV")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            importar_medicos_csv()
        elif opcao == '2':
            importar_pacientes_json()
        elif opcao == '3':
            cadastrar_medico()
        elif opcao == '4':
            cadastrar_paciente()
        elif opcao == '5':
            agendar_consulta()
        elif opcao == '6':
            listar_consultas_paciente()
        elif opcao == '7':
            relatorio_consultas()
        elif opcao == '8':
            exportar_csv()
        elif opcao == '0':
            break
        else:
            print("Opção inválida.")

menu()
conn.close()
