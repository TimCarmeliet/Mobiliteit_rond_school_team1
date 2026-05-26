import tkinter as tk

def get_default_theme():
    return {
        'chart_text': "#2c3e50",
        'chart_grid': "#e8eaed",
        'text_muted': "#5a6b7c",
        'border': "#5a6b7c"
    }

def teken_grafiek(canvas, data_dict, titel, theme=None):
    """Tekent een prachtige, uiterst leesbare vlakke staafgrafiek met dynamische kleurenthema contrasten."""
    canvas.update_idletasks()
    canvas.delete("all")
    if not data_dict: return
    
    if theme is None:
        theme = get_default_theme()
        
    c_width = canvas.winfo_width()
    c_height = canvas.winfo_height()
    
    if c_width <= 1: c_width = 580
    if c_height <= 1: c_height = 320
    
    margin_left, margin_bottom, margin_top, margin_right = 70, 60, 45, 30 
    graph_width = c_width - margin_left - margin_right
    graph_height = c_height - margin_top - margin_bottom
    
    # Grafiektitel in perfect leesbare themakleur
    canvas.create_text(c_width / 2, 20, text=titel, font=("Arial", 11, "bold"), fill=theme['chart_text'])
    
    max_val = max(data_dict.values()) if max(data_dict.values()) > 0 else 1
    num_items = len(data_dict)
    
    slot_width = graph_width / num_items
    bar_width = slot_width * 0.55
    spacing = slot_width * 0.45
    
    # Ticks en rasterlijnen (Grid lines)
    num_ticks = 4
    for t in range(num_ticks + 1):
        tick_val = (max_val / num_ticks) * t
        tick_y = c_height - margin_bottom - (t / num_ticks) * graph_height
        
        # Subtiele grid lijn
        canvas.create_line(margin_left - 4, tick_y, c_width - margin_right, tick_y, width=1, fill=theme['chart_grid'])
        
        # Label
        display_val = f"{int(tick_val)}" if tick_val.is_integer() else f"{tick_val:.1f}"
        canvas.create_text(margin_left - 10, tick_y, text=display_val, font=("Arial", 9), anchor="e", fill=theme['text_muted'])
    
    # Staven (Solid flat design met donkere omlijning)
    for i, (key, value) in enumerate(data_dict.items()):
        x_start = margin_left + (i * slot_width) + (spacing / 2)
        x_end = x_start + bar_width
        bar_h = (value / max_val) * graph_height
        y_start = c_height - margin_bottom - bar_h
        y_end = c_height - margin_bottom
        
        # Professional stalen blauwe of indigo kleur voor perfecte contrasten
        bar_color = theme.get('accent', '#4a90e2')
        outline_color = theme.get('border', '#5a6b7c')
        
        canvas.create_rectangle(x_start, y_start, x_end, y_end, fill=bar_color, outline=outline_color, width=1)
        
        # Waarde label bovenop de staaf
        display_val = round(value, 1)
        val_text = f"{int(display_val)}" if display_val.is_integer() else f"{display_val:.1f}"
        canvas.create_text((x_start + x_end) / 2, y_start - 10, text=val_text, font=("Arial", 9, "bold"), fill=theme['chart_text'])
        
        # Label onderaan de as
        y_offset = 16 if i % 2 == 0 else 32
        canvas.create_text((x_start + x_end) / 2, y_end + y_offset, text=str(key), font=("Arial", 9, "bold"), fill=theme['text_muted'], justify="center")

    # As-lijnen
    canvas.create_line(margin_left, c_height - margin_bottom, c_width - margin_right, c_height - margin_bottom, width=1.5, fill=theme['border']) 
    canvas.create_line(margin_left, margin_top, margin_left, c_height - margin_bottom, width=1.5, fill=theme['border']) 

def teken_cirkeldiagram(canvas, data_dict, titel, theme=None):
    """Tekent een klassiek, solide cirkeldiagram (pie chart) met een contrastrijke legenda."""
    canvas.update_idletasks()
    canvas.delete("all")
    
    totaal = sum(data_dict.values())
    if not data_dict or totaal == 0:
        return
        
    if theme is None:
        theme = get_default_theme()
        
    c_width = canvas.winfo_width()
    c_height = canvas.winfo_height()
    
    if c_width <= 1: c_width = 580
    if c_height <= 1: c_height = 320
    
    # Titel
    canvas.create_text(c_width / 2, 20, text=titel, font=("Arial", 11, "bold"), fill=theme['chart_text'])
    
    margin = 45
    box_size = min(c_width / 2.3, c_height - margin * 1.5)
    cx = c_width / 3.2
    cy = c_height / 2 + 10
    
    x0 = cx - box_size / 2
    y0 = cy - box_size / 2
    x1 = cx + box_size / 2
    y1 = cy + box_size / 2
    
    # Klassieke, heldere kleuren voor scherpe contrasten
    kleuren = ["#3498db", "#2ecc71", "#f1c40f", "#e74c3c", "#9b59b6", "#e67e22", "#1abc9c", "#34495e"]
    start_angle = 90  
    
    legend_x = cx + box_size / 2 + 35
    legend_y = y0 + 15
    
    outline_sep_color = theme.get('card_bg', '#ffffff')
    
    kleur_index = 0
    for key, value in data_dict.items():
        if value == 0: continue
            
        extent_angle = (value / totaal) * 360
        huidige_kleur = kleuren[kleur_index % len(kleuren)]
        
        # Teken taartpunt (Pie slice) met dunne witte/card scheidingen
        canvas.create_arc(x0, y0, x1, y1, start=start_angle, extent=-extent_angle, fill=huidige_kleur, outline=outline_sep_color, width=1.5)
        
        # Legenda indicator vierkant
        canvas.create_rectangle(legend_x, legend_y, legend_x + 14, legend_y + 14, fill=huidige_kleur, outline=theme['border'])
        
        # Legenda tekst (High contrast)
        pct = round((value / totaal) * 100, 1)
        lbl_text = f"{key}  •  {value} ({pct}%)"
        canvas.create_text(legend_x + 22, legend_y + 7, text=lbl_text, font=("Arial", 9, "bold"), anchor="w", fill=theme['chart_text'])
        
        start_angle -= extent_angle
        legend_y += 24
        kleur_index += 1
