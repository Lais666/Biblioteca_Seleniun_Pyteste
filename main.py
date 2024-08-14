from flask import Flask, render_template, request, redirect, url_for, flash
import fdb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Configurações da conexão
host = 'localhost'  # ou o IP do servidor onde o Firebird está rodando
database = r'C:\Users\SN1089702\Downloads\bancofire\livro.FDB'  # caminho para o arquivo .fdb
user = 'sysdba'
password = 'sysdba'

# Conexão com o banco de dados
con = fdb.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

# Classe Livro
class Livro:
    def __init__(self, id_livro, titulo, autor, ano_publicacao):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.ano_publicacao = ano_publicacao

# Rota para exibir a lista de livros em um layout HTML
@app.route('/')
def index():
    cursor = con.cursor()
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM livros order by 1")
    livros = [Livro(*row) for row in cursor.fetchall()]
    cursor.close()
    return render_template('livros.html', livros=livros)

@app.route('/novo')
def novo():
        return render_template('novo.html', titulo='Novo Livro')

@app.route('/atualizar')
def atualizar():
        return render_template('editar.html', titulo='Editar Livro')


@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    cursor = con.cursor()

    # Verificar se o livro já existe
    cursor.execute("SELECT COUNT(*) FROM livros WHERE TITULO = ?", (titulo,))
    livro_existente = cursor.fetchone()[0]

    if livro_existente > 0:
        cursor.close()
        # Retornar uma mensagem de erro ou redirecionar para uma página de erro
        flash("Erro: Livro já cadastrado.", "error")
        return redirect(url_for('novo'))
    if titulo == '':
        flash("Erro: O campo título não pode ser vazio.", "error")
        return redirect(url_for('novo'))
    if autor == '':
        flash("Erro: O campo autor não pode ser vazio.", "error")
        return redirect(url_for('novo'))
    if ano_publicacao == '':
        flash("Erro: O ano de publicação não pode ser vazio.", "error")
        return redirect(url_for('novo'))

    # Inserir o novo livro
    cursor.execute("INSERT INTO livros (TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?) RETURNING ID_LIVRO",
                   (titulo, autor, ano_publicacao))
    livro_id = cursor.fetchone()[0]
    con.commit()
    cursor.close()
    flash("Livro cadastrado com sucesso!", "success")
    return redirect(url_for('index'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    cursor = con.cursor()

    # Buscar o livro específico para edição
    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM livros WHERE ID_LIVRO = ?", (id,))
    livro = cursor.fetchone()

    if not livro:
        cursor.close()
        flash("Livro não encontrado!", "error")

    livro = Livro(*livro)

    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        ano_publicacao = request.form['ano_publicacao']

        # Atualizar o livro no banco de dados
        cursor.execute("UPDATE livros SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?",
                       (titulo, autor, ano_publicacao, id))
        con.commit()
        cursor.close()
        flash("Livro atualizado com sucesso!", "success")
        return redirect(url_for('index'))

    cursor.close()
    return render_template('editar.html', livro=livro, titulo='Editar Livro')

@app.route('/deletar/<int:id>', methods=('POST',))
def deletar(id):
    if request.method == 'POST':
        cursor = con.cursor()
        cursor.execute('DELETE FROM livros WHERE id_livro = ?', (id,))
        con.commit()
        cursor.close()
        flash('Livro excluído com sucesso!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)