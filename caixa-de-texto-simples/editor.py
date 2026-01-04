import tkinter as tk

fixo_no_topo = False

def copiar():
    texto = caixa_texto.get("1.0", tk.END)
    janela.clipboard_clear()
    janela.clipboard_append(texto)

def colar():
    try:
        texto = janela.clipboard_get()
        caixa_texto.insert(tk.INSERT, texto)
    except tk.TclError:
        pass

def alternar_topo():
    global fixo_no_topo
    fixo_no_topo = not fixo_no_topo
    janela.attributes("-topmost", fixo_no_topo)
    if fixo_no_topo:
        btn_topo.config(text="Fixo no topo")
    else:
        btn_topo.config(text="Não fixo")

janela = tk.Tk()
janela.title("Editor do Skoqui")
janela.geometry("500x300")
janela.config(bg="#1e1e1e")

frame_botoes = tk.Frame(janela, bg="#1e1e1e")
frame_botoes.pack(side=tk.TOP, fill=tk.X, pady=5)

btn_copiar = tk.Button(frame_botoes, text="Copiar", command=copiar, bg="#333", fg="white", font=("Arial", 10), width=5)
btn_copiar.pack(side=tk.LEFT, padx=5)

btn_colar = tk.Button(frame_botoes, text="Colar", command=colar, bg="#333", fg="white", font=("Arial", 10), width=5)
btn_colar.pack(side=tk.LEFT, padx=5)

btn_topo = tk.Button(frame_botoes, text="Não fixo", command=alternar_topo, bg="#444", fg="white", font=("Arial", 10), width=8)
btn_topo.pack(side=tk.LEFT, padx=5)

caixa_texto = tk.Text(
    janela,
    bg="#1e1e1e", fg="white",
    insertbackground="white",
    font=("Consolas", 12),
    wrap=tk.WORD
)
caixa_texto.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

janela.mainloop()
