import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # Configurações básicas da página
    page.bgcolor = ft.colors.BLACK
    page.padding = ft.padding.all(30)
    page.window_width = 450
    page.window_height = 900
    page.title = 'Habitus'

    # Banco de dados
    conn = sqlite3.connect('habitus.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habitus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habito TEXT NOT NULL,
            feito BOOLEAN DEFAULT 0,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

    # Componentes de progresso
    progress_bar = ft.ProgressBar(
        width=400,
        value=0, 
        color=ft.colors.WHITE, 
        bgcolor=ft.colors.INDIGO_100,
        border_radius=ft.border_radius.all(10),
        height=20,
    )
    
    progress_text = ft.Text(
        value='0%', 
        size=50, 
        color=ft.colors.WHITE,
        weight=ft.FontWeight.BOLD
        
    )

    # Funções de gerenciamento de hábitos
    def carregar_habitos():
        cursor.execute('SELECT id, habito, feito FROM habitus')
        return [{'id': row[0], 'habito': row[1], 'feito': bool(row[2])} for row in cursor.fetchall()]

    def deletar_habito(e, titulo_habito):
        cursor.execute('DELETE FROM habitus WHERE habito = ?', (titulo_habito,))
        conn.commit()
        
        lista_habitos = carregar_habitos()
        habitos.content.controls = [criar_linha_habito(h) for h in lista_habitos]
        habitos.update()
        atualizar_progresso()

    def criar_linha_habito(habito):
        return ft.Row(
            controls=[
                ft.Checkbox(
                    label=habito['habito'],
                    value=habito['feito'],
                    on_change=mudar_habito,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.RED_400,
                    tooltip="Remover habito",
                    on_click=lambda e: deletar_habito(e, habito['habito'])  
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def atualizar_progresso():
        cursor.execute('SELECT COUNT(*) FROM habitus WHERE feito = 1')
        quantidade_feitos = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM habitus')
        quantidade_total = cursor.fetchone()[0]
        
        if quantidade_total > 0:
            total = quantidade_feitos / quantidade_total
            progress_bar.value = total
            progress_text.value = f'{total:.0%}'
        else:
            progress_bar.value = 0
            progress_text.value = '0%'
        
        page.update()

    def mudar_habito(e):
        cursor.execute('UPDATE habitus SET feito = ? WHERE habito = ?', 
                      (e.control.value, e.control.label))
        conn.commit()
        atualizar_progresso()

    def adicionar_habito(e):
        if not e.control.value:
            return
            
        cursor.execute('INSERT INTO habitus (habito, feito) VALUES (?, ?)', 
                      (e.control.value, False))
        conn.commit()
        
        lista_habitos = carregar_habitos()
        habitos.content.controls = [criar_linha_habito(h) for h in lista_habitos]
        
        e.control.value = ''
        habitos.update()
        e.control.update()
        atualizar_progresso()

    # Componentes da interface
    habitos = ft.Container(
        expand=True,
        padding=ft.padding.all(30),
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.all(20),
        margin=ft.margin.symmetric(vertical=20),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[criar_linha_habito(h) for h in carregar_habitos()]
        ),
    )

    progress_container = ft.Container(
        padding=ft.padding.all(30),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.colors.INDIGO_500, ft.colors.BLUE_400],
        ),
        border_radius=ft.border_radius.all(20),
        margin=ft.margin.symmetric(vertical=30),
        content=ft.Column(
            controls=[
                ft.Text(value='Sua evolução hoje', size=20, color=ft.colors.WHITE),
                progress_text,
                progress_bar,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    layout = ft.Column(
        expand=True,
        controls=[
            ft.Text(value='Que bom ter você aqui', size=30, color=ft.colors.WHITE),
            ft.Text(value='Como estão seus hábitos hoje?', size=20, color=ft.colors.GREY),
            progress_container,
            ft.Text(value='Hábitos de hoje', size=20, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ft.Text(
                value='Marcar suas tarefas como concluído te motiva a continuar focado.', 
                size=16, 
                color=ft.colors.WHITE
            ),
            habitos,
            ft.Text(value='Adicionar novo hábito', size=20, color=ft.colors.WHITE),
            ft.TextField(
                hint_text='Escreva um hábito...',
                border=ft.InputBorder.UNDERLINE,
                on_submit=adicionar_habito,
                color=ft.colors.WHITE,
            )
        ]
    )

    # Inicialização e limpeza
    page.add(layout)
    atualizar_progresso()
    page.on_close = lambda: conn.close()

if __name__ == '__main__':
    ft.app(target=main)
