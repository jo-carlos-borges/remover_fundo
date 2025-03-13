import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from rembg import remove
from PIL import Image
import os
import threading

class BackgroundRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Removedor de Fundo de Imagens")
        self.root.geometry("600x450")
        
        # Variáveis de controle
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.resize_var = tk.BooleanVar(value=True)
        self.width_var = tk.StringVar(value="500")
        self.height_var = tk.StringVar(value="500")
        self.processing = False

        # Configurar layout
        self.create_widgets()

    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Seção de entrada
        ttk.Label(main_frame, text="Pasta de Origem:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.input_dir, width=40).grid(row=0, column=1, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar", command=self.browse_input).grid(row=0, column=2, padx=5)

        # Seção de saída
        ttk.Label(main_frame, text="Pasta de Destino:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=40).grid(row=1, column=1, sticky=tk.EW)
        ttk.Button(main_frame, text="Procurar", command=self.browse_output).grid(row=1, column=2, padx=5)

        # Seção de redimensionamento
        ttk.Checkbutton(main_frame, text="Redimensionar imagens para:", 
                       variable=self.resize_var).grid(row=2, column=0, sticky=tk.W, pady=10)
        
        ttk.Label(main_frame, text="Largura:").grid(row=2, column=1, sticky=tk.W)
        ttk.Entry(main_frame, textvariable=self.width_var, width=8).grid(row=2, column=1, sticky=tk.W, padx=60)
        
        ttk.Label(main_frame, text="Altura:").grid(row=2, column=1, sticky=tk.E)
        ttk.Entry(main_frame, textvariable=self.height_var, width=8).grid(row=2, column=1, sticky=tk.E, padx=5)

        # Botão de processamento
        self.process_btn = ttk.Button(main_frame, text="Processar Imagens", command=self.start_processing)
        self.process_btn.grid(row=3, column=1, pady=20)

        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress.grid(row=4, column=0, columnspan=3, sticky=tk.EW)

        # Log de status
        self.status_text = tk.Text(main_frame, height=8, state=tk.DISABLED)
        self.status_text.grid(row=5, column=0, columnspan=3, sticky=tk.EW)

        # Configurar pesos das colunas
        main_frame.columnconfigure(1, weight=1)

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_dir.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)
        else:
            folder = filedialog.askdirectory(mustexist=False)
            if folder:
                os.makedirs(folder, exist_ok=True)
                self.output_dir.set(folder)

    def log_message(self, message, color="black"):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n", color)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)

    def start_processing(self):
        if self.processing:
            return

        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Erro", "Selecione ambas as pastas!")
            return

        self.processing = True
        self.process_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.process_images, daemon=True).start()

    def process_images(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()
        resize = self.resize_var.get()

        try:
            # Validar tamanhos
            try:
                new_width = int(self.width_var.get())
                new_height = int(self.height_var.get())
                new_size = (new_width, new_height)
            except ValueError:
                messagebox.showerror("Erro", "Valores de tamanho inválidos! Use números inteiros.")
                return

            os.makedirs(output_dir, exist_ok=True)
            image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            total_images = len(image_files)
            error_files = []

            self.progress["maximum"] = total_images
            self.progress["value"] = 0

            if total_images == 0:
                self.log_message("Nenhuma imagem encontrada na pasta de origem!", "red")
                return

            for index, filename in enumerate(image_files, 1):
                if not self.processing:
                    break

                input_path = os.path.join(input_dir, filename)
                output_path = os.path.join(output_dir, os.path.splitext(filename)[0] + ".png")

                try:
                    with Image.open(input_path) as img:
                        output_img = remove(img)

                        if resize:
                            output_img = output_img.resize(new_size)

                        output_img.save(output_path, 'PNG')
                        self.log_message(f"Processado: {filename}", "green")
                except Exception as e:
                    error_files.append(filename)
                    self.log_message(f"Erro em {filename}: {str(e)}", "red")

                self.progress["value"] = index
                self.root.update_idletasks()

            # Resultado final
            self.log_message("\nProcessamento concluído!", "blue")
            if error_files:
                self.log_message(f"Arquivos com erro ({len(error_files)}):", "red")
                for file in error_files:
                    self.log_message(f" - {file}", "red")
            else:
                self.log_message("Todas as imagens foram processadas com sucesso!", "green")

            os.startfile(output_dir)

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")
        finally:
            self.processing = False
            self.process_btn.config(state=tk.NORMAL)
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = BackgroundRemoverApp(root)
    root.mainloop()