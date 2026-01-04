import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import socket
import threading

stop_scan = False  

def scan_port(ip, port, result_box, params, verbose_level):
    if stop_scan:
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if verbose_level >= 1:
                result_box.insert(tk.END, f"[INFO] Tentando porta {port}...\n")
                result_box.see(tk.END)
            if result == 0:
                banner = ""
                if "-sV" in params or "-A" in params:
                    try:
                        s.sendall(b"\r\n")
                        banner = s.recv(1024).decode(errors="ignore").strip()
                    except:
                        pass
                result_box.insert(
                    tk.END,
                    f"[+] Porta aberta: {port} {'| ' + banner if banner else ''}\n",
                )
                result_box.see(tk.END)
            else:
                if verbose_level >= 2:
                    result_box.insert(
                        tk.END, f"[-] Porta {port} fechada ou inacessível.\n"
                    )
                    result_box.see(tk.END)
    except Exception as e:
        if verbose_level >= 2:
            result_box.insert(tk.END, f"[ERRO] Porta {port}: {e}\n")
            result_box.see(tk.END)


def start_scan():
    global stop_scan
    stop_scan = False
    target = entry_target.get()
    try:
        start_port = int(entry_start.get())
        end_port = int(entry_end.get())
        thread_count = int(entry_threads.get())
    except ValueError:
        messagebox.showerror("Erro", "Portas e threads devem ser números.")
        return

    raw_params = entry_params.get().strip()
    params = raw_params.split() if raw_params else []

    verbose_level = 0
    if "-vv" in params:
        verbose_level = 2
    elif "-v" in params:
        verbose_level = 1

    result_box.delete("1.0", tk.END)
    thread_list = []

    def scan_range():
        for port in range(start_port, end_port + 1):
            if stop_scan:
                break
            label_status.config(text=f"Escaneando: {port}/{end_port}")
            t = threading.Thread(
                target=scan_port, args=(target, port, result_box, params, verbose_level)
            )
            t.start()
            thread_list.append(t)
            if len(thread_list) >= thread_count:
                for thread in thread_list:
                    thread.join()
                thread_list.clear()
        label_status.config(
            text="Scan finalizado!" if not stop_scan else "Scan interrompido!"
        )

    threading.Thread(target=scan_range).start()


def parar_scan():
    global stop_scan
    stop_scan = True


def limpar_resultado():
    result_box.delete("1.0", tk.END)
    label_status.config(text="Aguardando...")


def salvar_resultado():
    resultado = result_box.get("1.0", tk.END)
    if resultado.strip():
        file = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Texto", "*.txt")]
        )
        if file:
            with open(file, "w") as f:
                f.write(resultado)
            messagebox.showinfo("Salvo", "Resultado salvo com sucesso!")
    else:
        messagebox.showwarning("Aviso", "Nenhum resultado para salvar.")


root = tk.Tk()
root.title("Port Scanner Simples")
root.geometry("600x550")
root.resizable(False, False)

tk.Label(root, text="Host/IP:").pack()
entry_target = tk.Entry(root, width=50)
entry_target.pack(pady=2)

frame_ports = tk.Frame(root)
frame_ports.pack(pady=5)

tk.Label(frame_ports, text="Porta Inicial:").grid(row=0, column=0)
entry_start = tk.Entry(frame_ports, width=10)
entry_start.grid(row=0, column=1)
entry_start.insert(0, "1")

tk.Label(frame_ports, text="Porta Final:").grid(row=0, column=2)
entry_end = tk.Entry(frame_ports, width=10)
entry_end.grid(row=0, column=3)
entry_end.insert(0, "1024")

tk.Label(frame_ports, text="Threads:").grid(row=0, column=4)
entry_threads = tk.Entry(frame_ports, width=5)
entry_threads.grid(row=0, column=5)
entry_threads.insert(0, "10")

frame_params = tk.Frame(root)
frame_params.pack(pady=5)

tk.Label(frame_params, text="Parâmetros (ex: -sV -A -v):").pack(side="left")
entry_params = tk.Entry(frame_params, width=30)
entry_params.pack(side="left", padx=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(
    button_frame, text="Iniciar Scan", command=start_scan, bg="#4CAF50", fg="white"
).grid(row=0, column=0, padx=5)
tk.Button(
    button_frame, text="Parar", command=parar_scan, bg="#f44336", fg="white"
).grid(row=0, column=1, padx=5)
tk.Button(
    button_frame, text="Limpar", command=limpar_resultado, bg="#9E9E9E", fg="white"
).grid(row=0, column=2, padx=5)
tk.Button(
    button_frame, text="Salvar", command=salvar_resultado, bg="#2196F3", fg="white"
).grid(row=0, column=3, padx=5)

label_status = tk.Label(root, text="Aguardando...", fg="blue")
label_status.pack()

result_box = scrolledtext.ScrolledText(root, height=20, width=70)
result_box.pack(pady=5)

root.mainloop()
