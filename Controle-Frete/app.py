from flask import (
    Flask,
    render_template,
    request,
    redirect,
    send_from_directory,
    url_for,
    flash,
)
import sqlite3, os, uuid, datetime, shutil

app = Flask(__name__)
app.secret_key = "fretes-seguro"  # necessário para flash

DB = "banco.db"
UPLOAD = "uploads/fretes"
os.makedirs(UPLOAD, exist_ok=True)


def conectar():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def limpar_valor_brl(valor_raw):
    """
    Recebe valor no formato BR (1.234,56)
    Retorna float seguro (1234.56)
    """
    if not valor_raw:
        raise ValueError("Valor vazio")

    valor = valor_raw.replace(".", "").replace(",", ".").strip()

    return float(valor)


@app.route("/", methods=["GET", "POST"])
def enviar():
    if request.method == "POST":
        frete_id = str(uuid.uuid4())

        servico = request.form.get("servico", "").strip()
        empresa = request.form.get("empresa")
        pagador = request.form.get("pagador")

        enviado_por = "Carla"
        data_hora = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        # 🔐 VALIDAÇÃO DO VALOR DO FRETE
        try:
            valor_frete = limpar_valor_brl(request.form.get("valor"))
        except ValueError:
            flash("Valor do frete inválido. Use apenas números.", "danger")
            return redirect(url_for("enviar"))

        agrupar_cte = int(request.form.get("agrupar_cte", 0))
        manifestar = int(request.form.get("manifestar", 0))

        base = f"{UPLOAD}/{frete_id}/entrada"
        os.makedirs(base, exist_ok=True)

        conn = conectar()
        c = conn.cursor()

        c.execute(
            """
            INSERT INTO fretes (
                id,
                empresa,
                servico,
                enviado_por,
                pagador,
                valor,
                visto,
                concluido,
                data_hora,
                agrupar_cte,
                manifestar
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                frete_id,
                empresa,
                servico,
                enviado_por,
                pagador,
                valor_frete,  # 👈 agora é FLOAT seguro
                0,
                0,
                data_hora,
                agrupar_cte,
                manifestar,
            ),
        )

        for f in request.files.getlist("documentos"):
            if f.filename:
                novo_nome = f"{servico}_{f.filename}"
                f.save(os.path.join(base, novo_nome))

                c.execute(
                    """
                    INSERT INTO arquivos (
                        frete_id,
                        tipo,
                        nome_original,
                        nome_salvo
                    )
                    VALUES (?, 'entrada', ?, ?)
                    """,
                    (frete_id, f.filename, novo_nome),
                )

        conn.commit()
        conn.close()

        return redirect(url_for("listar"))

    return render_template("enviar.html")


@app.route("/listar")
def listar():
    conn = conectar()
    fretes = conn.execute("SELECT * FROM fretes ORDER BY data_hora DESC").fetchall()
    conn.close()

    hoje_str = datetime.datetime.now().strftime("%d/%m/%Y")

    return render_template("listar.html", fretes=fretes, hoje_str=hoje_str)


@app.route("/frete/<id>")
def frete(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("UPDATE fretes SET visto = 1 WHERE id = ?", (id,))
    frete = c.execute("SELECT * FROM fretes WHERE id = ?", (id,)).fetchone()

    arquivos = c.execute("SELECT * FROM arquivos WHERE frete_id = ?", (id,)).fetchall()

    conn.commit()
    conn.close()

    return render_template("frete.html", frete=frete, arquivos=arquivos)


@app.route("/concluir/<id>")
def concluir(id):
    conn = conectar()
    conn.execute("UPDATE fretes SET concluido = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("frete", id=id))


@app.route("/download/<frete_id>/<path:nome>")
def download(frete_id, nome):
    pasta = f"{UPLOAD}/{frete_id}/entrada"
    return send_from_directory(pasta, nome, as_attachment=True)


@app.route("/remover/<id>", methods=["POST"])
def remover(id):
    conn = conectar()
    c = conn.cursor()

    c.execute("DELETE FROM arquivos WHERE frete_id = ?", (id,))
    c.execute("DELETE FROM fretes WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    pasta = f"{UPLOAD}/{id}"
    if os.path.exists(pasta):
        shutil.rmtree(pasta)

    return redirect(url_for("listar"))


if __name__ == "__main__":
    app.run(debug=True)
