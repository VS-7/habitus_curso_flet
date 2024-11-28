import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    # Configurações básicas da página
    page.bgcolor = ft.colors.BLACK
    page.padding = ft.padding.all(30)
    page.title = 'Habitus'

    # Banco de dados
    conn = sqlite3.connect('habitus.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habitus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
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
    def load_habits():
        cursor.execute('SELECT id, titulo, feito FROM habitus')
        return [{'id': row[0], 'titulo': row[1], 'feito': bool(row[2])} for row in cursor.fetchall()]

    def delete_habit(e, habit_title):
        cursor.execute('DELETE FROM habitus WHERE titulo = ?', (habit_title,))
        conn.commit()
        
        habits_list = load_habits()
        habits.content.controls = [create_habit_row(hl) for hl in habits_list]
        habits.update()
        update_progress()

    def create_habit_row(habit):
        return ft.Row(
            controls=[
                ft.Checkbox(
                    label=habit['titulo'],
                    value=habit['feito'],
                    on_change=change_habit,
                    expand=True
                ),
                ft.IconButton(
                    icon=ft.icons.DELETE_OUTLINE,
                    icon_color=ft.colors.RED_400,
                    tooltip="Remover habito",
                    on_click=lambda e: delete_habit(e, habit['titulo'])  
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def update_progress():
        cursor.execute('SELECT COUNT(*) FROM habitus WHERE feito = 1')
        done_count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM habitus')
        total_count = cursor.fetchone()[0]
        
        if total_count > 0:
            total = done_count / total_count
            progress_bar.value = total
            progress_text.value = f'{total:.0%}'
        else:
            progress_bar.value = 0
            progress_text.value = '0%'
        
        page.update()

    def change_habit(e):
        cursor.execute('UPDATE habitus SET feito = ? WHERE titulo = ?', 
                      (e.control.value, e.control.label))
        conn.commit()
        update_progress()

    def add_habit(e):
        if not e.control.value:
            return
            
        cursor.execute('INSERT INTO habitus (titulo, feito) VALUES (?, ?)', 
                      (e.control.value, False))
        conn.commit()
        
        habits_list = load_habits()
        habits.content.controls = [create_habit_row(hl) for hl in habits_list]
        
        e.control.value = ''
        habits.update()
        e.control.update()
        update_progress()

    # Componentes da interface
    habits = ft.Container(
        expand=True,
        padding=ft.padding.all(30),
        bgcolor=ft.colors.GREY_900,
        border_radius=ft.border_radius.all(20),
        margin=ft.margin.symmetric(vertical=20),
        content=ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[create_habit_row(hl) for hl in load_habits()]
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
            habits,
            ft.Text(value='Adicionar novo hábito', size=20, color=ft.colors.WHITE),
            ft.TextField(
                hint_text='Escreva um hábito...',
                border=ft.InputBorder.UNDERLINE,
                on_submit=add_habit,
                color=ft.colors.WHITE,
            )
        ]
    )

    # Inicialização e limpeza
    page.add(layout)
    update_progress()
    page.on_close = lambda: conn.close()

if __name__ == '__main__':
    ft.app(target=main)
