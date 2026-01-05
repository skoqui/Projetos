import tkinter as tk
from tkinter import messagebox
import random
import string


def gerar_senha():
    try:
        tamanho = int(entry_tamanho.get())
        if tamanho <= 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Erro", "Digite um número válido maior que 0.")
        return

    caracteres = ""
    if var_maiusculas.get():
        caracteres += string.ascii_uppercase
    if var_minusculas.get():
        caracteres += string.ascii_lowercase
    if var_numeros.get():
        caracteres += string.digits
    if var_especiais.get():
        caracteres += string.punctuation

    if not caracteres:
        messagebox.showerror("Erro", "Selecione pelo menos um tipo de caractere.")
        return

    senha = "".join(random.choice(caracteres) for _ in range(tamanho))
    entry_resultado.delete(0, tk.END)
    entry_resultado.insert(0, senha)


def copiar_para_area_transferencia():
    senha = entry_resultado.get()
    if senha:
        root.clipboard_clear()
        root.clipboard_append(senha)
        messagebox.showinfo("Copiado", "Senha copiada para a área de transferência.")


bg_color = "#1e1e1e"
fg_color = "#ffffff"
entry_bg = "#2d2d2d"
button_bg = "#3c3c3c"

root = tk.Tk()
root.title("Gerador de Senhas- Dark Mode")
root.geometry("400x320")
root.resizable(False, False)
root.configure(bg=bg_color)

label_tamanho = tk.Label(root, text="Tamanho da Senha:", bg=bg_color, fg=fg_color)
label_tamanho.pack(pady=5)

entry_tamanho = tk.Entry(
    root, justify="center", bg=entry_bg, fg=fg_color, insertbackground=fg_color
)
entry_tamanho.insert(0, "12")
entry_tamanho.pack()

frame_opcoes = tk.Frame(root, bg=bg_color)
frame_opcoes.pack(pady=10)

var_maiusculas = tk.BooleanVar(value=True)
var_minusculas = tk.BooleanVar(value=True)
var_numeros = tk.BooleanVar(value=True)
var_especiais = tk.BooleanVar(value=True)

tk.Checkbutton(
    frame_opcoes,
    text="Letras Maiúsculas",
    variable=var_maiusculas,
    bg=bg_color,
    fg=fg_color,
    selectcolor=bg_color,
).grid(row=0, column=0, sticky="w")
tk.Checkbutton(
    frame_opcoes,
    text="Letras Minúsculas",
    variable=var_minusculas,
    bg=bg_color,
    fg=fg_color,
    selectcolor=bg_color,
).grid(row=1, column=0, sticky="w")
tk.Checkbutton(
    frame_opcoes,
    text="Números",
    variable=var_numeros,
    bg=bg_color,
    fg=fg_color,
    selectcolor=bg_color,
).grid(row=0, column=1, sticky="w")
tk.Checkbutton(
    frame_opcoes,
    text="Especiais",
    variable=var_especiais,
    bg=bg_color,
    fg=fg_color,
    selectcolor=bg_color,
).grid(row=1, column=1, sticky="w")

btn_gerar = tk.Button(
    root,
    text="Gerar Senha",
    command=gerar_senha,
    bg=button_bg,
    fg=fg_color,
    activebackground="#555",
)
btn_gerar.pack(pady=10)

entry_resultado = tk.Entry(
    root,
    justify="center",
    font=("Courier", 12),
    bg=entry_bg,
    fg=fg_color,
    insertbackground=fg_color,
)
entry_resultado.pack(pady=5, fill=tk.X, padx=20)

btn_copiar = tk.Button(
    root,
    text="Copiar",
    command=copiar_para_area_transferencia,
    bg=button_bg,
    fg=fg_color,
    activebackground="#555",
)
btn_copiar.pack()

root.mainloop()
