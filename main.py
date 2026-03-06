import json
import urllib.request
import io
import threading
import tkinter as tk
import customtkinter as ctk  # type: ignore
from PIL import Image  # type: ignore

try:
    import reportlab  # type: ignore
except ImportError:
    import subprocess
    import sys
    print("Installing reportlab for PDF generation...")
    if sys.version_info < (3, 9):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab<4.0"])
    else:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])

from reportlab.lib import colors  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph  # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # type: ignore
from reportlab.pdfbase import pdfmetrics  # type: ignore
from reportlab.pdfbase.ttfonts import TTFont  # type: ignore
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

pdfmetrics.registerFont(TTFont('msjh', 'C:\\Windows\\Fonts\\msjh.ttc', 'msjh'))

# Initialize customtkinter settings
ctk.set_appearance_mode("System")  # Uses system theme (light/dark)
ctk.set_default_color_theme("blue")

class CountryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("World Countries Viewer - 國家資訊查詢系統")
        self.geometry("900x750")
        self.minsize(700, 600)
        
        # Load and process data
        self.valid_countries = []
        self.current_index = 0
        self.load_data()
        
        # UI Setup
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ==================== Main Frame ====================
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1) # Allow flag to expand
        
        # Top Navigation Bar
        self.top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.top_frame.grid(row=0, column=0, sticky="ew", pady=(5, 5))
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=0, minsize=550)
        self.top_frame.grid_columnconfigure(2, weight=1)
        
        self.prev_button = ctk.CTkButton(self.top_frame, text="◀", command=self.prev_country, font=ctk.CTkFont(size=40, weight="bold"), width=80, height=60)
        self.prev_button.grid(row=0, column=0, sticky="e", padx=(0, 20))
        
        self.title_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.title_frame.grid(row=0, column=1)
        
        self.info_title = ctk.CTkLabel(self.title_frame, text="國家資訊", font=ctk.CTkFont(size=28, weight="bold"))
        self.info_title.pack()

        self.capital_label = ctk.CTkLabel(self.title_frame, text="首都: ", font=ctk.CTkFont(size=24), text_color="lightgray")
        self.capital_label.pack(pady=0)
        
        self.next_button = ctk.CTkButton(self.top_frame, text="▶", command=self.next_country, font=ctk.CTkFont(size=40, weight="bold"), width=80, height=60)
        self.next_button.grid(row=0, column=2, sticky="w", padx=(20, 0))
        
        # Frame for flag
        self.flag_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.flag_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        self.flag_frame.grid_columnconfigure(0, weight=1)
        self.flag_frame.grid_rowconfigure(0, weight=1)
        
        self.flag_label = ctk.CTkLabel(self.flag_frame, text="載入中...", font=ctk.CTkFont(size=16))
        self.flag_label.grid(row=0, column=0)
        
        # Frame for text details
        self.details_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.details_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 5))
        self.details_frame.grid_columnconfigure(0, weight=1)
        self.details_frame.grid_columnconfigure(1, weight=1)
        
        self.area_label = ctk.CTkLabel(self.details_frame, text="領土面積 : ", font=ctk.CTkFont(size=24, weight="bold"))
        self.area_label.grid(row=0, column=0, pady=5, sticky="e", padx=(0, 20))

        self.population_label = ctk.CTkLabel(self.details_frame, text="國家人口 : ", font=ctk.CTkFont(size=24, weight="bold"))
        self.population_label.grid(row=0, column=1, pady=5, sticky="w", padx=(20, 0))

        # Frame for range buttons
        self.range_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.range_frame.grid(row=3, column=0, pady=(5, 10))
        
        # Determine ranges
        total_countries = len(self.valid_countries)
        ranges = [(i, min(i+49, total_countries-1)) for i in range(0, total_countries, 50)]
        
        # Layout ranges horizontally
        for start, end in ranges:
            btn_text = f"排名 {start+1}-{end+1}"
            btn = ctk.CTkButton(self.range_frame, text=btn_text, font=ctk.CTkFont(size=16),
                                command=lambda s=start, e=end: self.show_range_window(s, e))
            btn.pack(side="left", padx=5)

        self.action_frame = ctk.CTkFrame(self.range_frame, fg_color="transparent")
        self.action_frame.pack(side="left", padx=15)

        self.export_button = ctk.CTkButton(self.action_frame, text="匯出 PDF", command=self.export_pdf_thread, font=ctk.CTkFont(size=14, weight="bold"), width=120, height=30)
        self.export_button.pack(side="top", pady=(0, 5))

        search_btn = ctk.CTkButton(self.action_frame, text="🔍 搜尋", font=ctk.CTkFont(size=16), width=120, height=30,
                                    command=self.show_search_window, fg_color="darkblue", hover_color="blue")
        search_btn.pack(side="top")

        # Key bindings for arrow keys
        self.bind("<Left>", lambda event: self.prev_country())
        self.bind("<Right>", lambda event: self.next_country())

        if self.valid_countries:
            self.show_country()
            
    def load_data(self):
        try:
            json_path = resource_path("countries.json")
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            data = []
            
        # process data
        for c in data:
            name_en = c.get('name', {}).get('common', 'Unknown')
            name_zh = c.get('translations', {}).get('zho', {}).get('common', name_en)
                
            area = c.get('area')
            if area is None:
                area = -1
            
            population = c.get('population', -1)
            
            flag_url = c.get('flags', {}).get('png', '')
            if flag_url:
                flag_url = flag_url.replace('/w320/', '/w1280/')
            
            capital_en = c.get('capital_en', 'N/A')
            capital_zh = c.get('capital_zh', '無')
            self.valid_countries.append({
                'en': name_en,
                'zh': name_zh,
                'area': area,
                'population': population,
                'flag_url': flag_url,
                'capital_en': capital_en,
                'capital_zh': capital_zh
            })
            
        # Sort by area descending
        self.valid_countries.sort(key=lambda x: x['area'], reverse=True)
        for i, c in enumerate(self.valid_countries):
            c['rank'] = i + 1

    def export_pdf_thread(self):
        # Update button to show loading state
        self.export_button.configure(text="匯出中...", state="disabled")
        threading.Thread(target=self.export_pdf, daemon=True).start()

    def export_pdf(self):
        try:
            pdf_filename = "World_Countries_Ranking.pdf"
            doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
            
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                name="CustomTitle",
                parent=styles["Title"],
                fontName="msjh",
                fontSize=24,
                spaceAfter=20
            )
            
            elements.append(Paragraph("世界各國領土排名對照表", title_style))
            
            # Setup cell styles for text wrapping
            cell_style = ParagraphStyle(
                name="TableCell",
                fontName="msjh",
                fontSize=16,
                alignment=1, # Center
                leading=20
            )
            
            header_style = ParagraphStyle(
                name="TableHeader",
                fontName="msjh",
                fontSize=18,
                alignment=1, # Center
                leading=22,
                textColor=colors.whitesmoke
            )
            
            # Table data setup
            table_data = [[
                Paragraph("排名<br/>(Rank)", header_style), 
                Paragraph("繁體中文<br/>(Traditional Chinese)", header_style), 
                Paragraph("英文名稱<br/>(English)", header_style),
                Paragraph("首都<br/>(Capital)", header_style)
            ]]
            
            for i, c in enumerate(self.valid_countries):
                table_data.append([
                    Paragraph(str(c['rank']), cell_style), 
                    Paragraph(c['zh'], cell_style), 
                    Paragraph(c['en'], cell_style),
                    Paragraph(f"{c['capital_zh']}<br/>({c['capital_en']})", cell_style)
                ])
                
            # Create Table
            table = Table(table_data, colWidths=[65, 160, 160, 150])
            
            # Add general table style
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'msjh'),
                ('FONTSIZE', (0, 0), (-1, 0), 18),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 16),
                ('TOPPADDING', (0, 0), (-1, 0), 16),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 16),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 12),
                ('TOPPADDING', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            # Add alternating row colors for the data rows
            for i in range(1, len(table_data)):
                bg_color = colors.lightgrey if i % 2 == 0 else colors.whitesmoke
                style.add('BACKGROUND', (0, i), (-1, i), bg_color)
                
            table.setStyle(style)
            elements.append(table)
            doc.build(elements)
            print(f"Successfully generated: {pdf_filename}")
            
            # Open the generated PDF (Windows)
            os.startfile(os.path.abspath(pdf_filename))  # type: ignore
        except Exception as e:
            print(f"Error generating PDF: {e}")
        finally:
            self.after(0, lambda: self.export_button.configure(text="匯出 PDF", state="normal"))

    def show_range_window(self, start_idx, end_idx):
        is_zoomed = self.state() == "zoomed"
        window = ctk.CTkToplevel(self)
        
        # Workaround for CustomTkinter Toplevel un-maximizing the main window on Windows
        if is_zoomed:
            self.after(200, lambda: self.state("zoomed"))
            window.after(250, lambda: window.attributes("-topmost", True))
            window.after(300, lambda: window.attributes("-topmost", False))
            window.after(300, window.focus_force)
            
        window.title(f"國家列表 (排名 {start_idx+1} - {end_idx+1})")
        
        # Center horizontally at the top of the screen
        win_w, win_h = 650, 700
        screen_w = self.winfo_screenwidth()
        x = (screen_w - win_w) // 2
        y = 20
        window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        window.focus()
        
        # Scrollable frame for list
        scroll_frame = ctk.CTkScrollableFrame(window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        for i in range(start_idx, end_idx + 1):
            if i < len(self.valid_countries):
                c = self.valid_countries[i]
                rank = c['rank']
                zh = c['zh']
                en = c['en']
                
                # Make it clickable to jump to that country
                btn_text = f"No.{rank} - {zh} ({en})"
                
                item_btn = ctk.CTkButton(
                    scroll_frame, text=btn_text, font=ctk.CTkFont(size=26), 
                    anchor="w", fg_color="transparent", 
                    text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"], 
                    hover_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                    height=50,
                    command=lambda idx=i, w=window: self.jump_to_country(idx, w)
                )
                item_btn.pack(fill="x", pady=2)

    def show_search_window(self):
        is_zoomed = self.state() == "zoomed"
        window = ctk.CTkToplevel(self)
        
        # Workaround for CustomTkinter Toplevel un-maximizing the main window on Windows
        if is_zoomed:
            self.after(200, lambda: self.state("zoomed"))
            window.after(250, lambda: window.attributes("-topmost", True))
            window.after(300, lambda: window.attributes("-topmost", False))
            window.after(300, window.focus_force)
            
        window.title("搜尋國家 (Search Country)")
        
        # Center horizontally at the top of the screen
        win_w, win_h = 650, 700
        screen_w = self.winfo_screenwidth()
        x = (screen_w - win_w) // 2
        y = 20
        window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        window.focus()
        
        # Search entry
        search_entry = ctk.CTkEntry(window, placeholder_text="輸入國家名稱 (中英文皆可)...", font=ctk.CTkFont(size=20), height=40)
        search_entry.pack(fill="x", padx=20, pady=(20, 10))
        
        # Scrollable frame for list
        scroll_frame = ctk.CTkScrollableFrame(window)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def update_search_results(*args):
            # Clear previous results
            for widget in scroll_frame.winfo_children():
                widget.destroy()
                
            query = search_entry.get().strip().lower()
            
            for i, c in enumerate(self.valid_countries):
                zh = c['zh'].lower()
                en = c['en'].lower()
                if query in zh or query in en:
                    btn_text = f"No.{c['rank']} - {c['zh']} ({c['en']})"
                    item_btn = ctk.CTkButton(
                        scroll_frame, text=btn_text, font=ctk.CTkFont(size=26), 
                        anchor="w", fg_color="transparent", 
                        text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"], 
                        hover_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                        height=50,
                        command=lambda idx=i, w=window: self.jump_to_country(idx, w)
                    )
                    item_btn.pack(fill="x", pady=2)
                    
        # Call directly once to show all
        update_search_results()
        
        # Bind the update function to key release events on the entry
        search_entry.bind("<KeyRelease>", update_search_results)
        search_entry.focus()

    def jump_to_country(self, index, window):
        self.current_index = index
        self.show_country()
        window.destroy()
        self.focus_set()

    def prev_country(self):
        if not self.valid_countries: return
        self.current_index = (self.current_index - 1) % len(self.valid_countries)
        self.show_country()

    def next_country(self):
        if not self.valid_countries: return
        self.current_index = (self.current_index + 1) % len(self.valid_countries)
        self.show_country()

    def show_country(self):
        if not self.valid_countries: return
        c_data = self.valid_countries[self.current_index]
            
        area_text = f"{c_data['area']:,.2f} km²" if c_data['area'] >= 0 else "無資料"
        self.area_label.configure(text=f"領土面積 : {area_text}")
        
        pop_text = f"{c_data.get('population', -1):,}" if c_data.get('population', -1) >= 0 else "無資料"
        self.population_label.configure(text=f"國家人口 : {pop_text}")
        
        # Title updated: Rank - Name
        title_text = f"No. {c_data['rank']} - {c_data['zh']} ({c_data['en']})"
        title_font_size = 28 if len(title_text) < 45 else 20 if len(title_text) < 65 else 16
        self.info_title.configure(text=title_text, font=ctk.CTkFont(size=title_font_size, weight="bold"))

        # Capital updated
        capital_text = f"首都: {c_data['capital_zh']} ({c_data['capital_en']})" if c_data['capital_en'] != 'N/A' else "首都: 無資料"
        cap_font_size = 24 if len(capital_text) < 45 else 18 if len(capital_text) < 65 else 14
        self.capital_label.configure(text=capital_text, font=ctk.CTkFont(size=cap_font_size))
        
        # Load flag image asynchronously
        self.flag_label.configure(image=None, text="載入國旗中... (Loading Flag...)")
        threading.Thread(target=self.load_image, args=(c_data['flag_url'],), daemon=True).start()

    def load_image(self, url):
        self.current_raw_img = None
        if not url:
            self.after(0, lambda: self.flag_label.configure(text="無國旗圖片 (No Flag Available)"))
            return
            
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_data = urllib.request.urlopen(req).read()
            img = Image.open(io.BytesIO(raw_data)).convert("RGBA")
            self.current_raw_img = img
            
            W, H = img.size
            new_W = min(600, W * 3)
            new_H = int(H * (new_W / W)) if W > 0 else 360
            
            # Create CTkImage
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_W, new_H))
            
            self.after(0, self.update_image_label, ctk_img)
        except Exception as e:
            print(f"Failed to load image: {e}")
            self.after(0, lambda: self.flag_label.configure(text="國旗載入失敗 (Failed to load flag)"))
            

            
    def update_image_label(self, img):
        self.flag_label.configure(image=img, text="")
        self.flag_label.image = img # Keep reference to avoid garbage collection

if __name__ == "__main__":
    app = CountryApp()
    app.mainloop()
