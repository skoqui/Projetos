import re
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tkinter as tk
from tkinter import filedialog
import os
import platform


def configurar_caminhos():
    if platform.system() == "Windows":
        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        caminho_poppler = r".\poppler\bin"
    else:
        caminho_poppler = None

    return caminho_poppler


def formatar_chave(chave_numerica):
    return " ".join(chave_numerica[i : i + 4] for i in range(0, len(chave_numerica), 4))


def processar_texto(texto):
    apenas_numeros = re.sub(r"\D", "", texto)
    return re.findall(r"35\d{42}", apenas_numeros)


def extrair_dados():
    caminho_poppler = configurar_caminhos()

    root = tk.Tk()
    root.withdraw()
    caminho = filedialog.askopenfilename(
        title="Selecionar Nota Fiscal",
        filetypes=[("Imagens e PDF", "*.png *.jpg *.jpeg *.pdf")],
    )
    root.destroy()

    if not caminho:
        print("Nenhum ficheiro selecionado.")
        return

    extensao = os.path.splitext(caminho)[1].lower()
    chaves_finais = []

    if extensao == ".pdf":
        paginas = convert_from_path(caminho, poppler_path=caminho_poppler)
        for i, pagina in enumerate(paginas):
            texto = pytesseract.image_to_string(pagina, lang="por")
            chaves = processar_texto(texto)
            for c in chaves:
                chaves_finais.append(
                    {"origem": f"Pág {i+1}", "chave": formatar_chave(c)}
                )
    else:
        imagem = Image.open(caminho)
        texto = pytesseract.image_to_string(imagem, lang="por")
        chaves = processar_texto(texto)
        for c in chaves:
            chaves_finais.append({"origem": "Imagem", "chave": formatar_chave(c)})

    if chaves_finais:
        print(f"\nResultados para: {os.path.basename(caminho)}")
        for item in chaves_finais:
            print(f"{item['origem']:<10} | {item['chave']}")
    else:
        print("Nenhuma chave válida encontrada.")


if __name__ == "__main__":
    extrair_dados()
