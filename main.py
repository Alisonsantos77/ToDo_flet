import sqlite3

import flet as ft


class ToDo:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.bgcolor = ft.colors.WHITE
        self.page.window_width = 400
        self.page.window_height = 450
        self.page.window_resizable = False
        self.page.window_always_on_top = True
        self.page.title = "ToDo App"
        self.task = ''
        self.view = 'all'
        
        # Inicia o banco de dados e Recupera tarefas
        self.db_execute('CREATE TABLE IF NOT EXISTS tasks(name, status)')
        self.results = self.db_execute('SELECT * FROM tasks')
        
        # Configuração da pagina inicial
        self.main_page()
        

    def db_execute(self, query, params=[]):
        with sqlite3.connect('database.db') as con:
            cursor = con.cursor()
            cursor.execute(query, params)
            con.commit()
            return cursor.fetchall()

    def checked(self, e):
        is_checked = e.control.value
        label = e.control.label
        
        if is_checked:
            self.db_execute('UPDATE tasks SET status = "complete" WHERE name = ?', params=[label])
        else:
            self.db_execute('UPDATE tasks SET status = "incomplete" WHERE name = ?', params=[label])
            
        if self.view == 'all':
            self.results = self.db_execute('SELECT * FROM tasks')
        else:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status =?', params=[self.view])
            
        self.update_task_list()
        
    def task_container(self):
        return ft.Container(
            height=self.page.height * 0.8,
            content=ft.Column(
                controls=[
                    ft.Checkbox(
                        adaptive=True,
                        active_color=ft.colors.BLUE_700,
                        label=res[0],
                        value=True if res[1] == 'complete' else False,
                        on_change=self.checked,
                    ) for res in self.results if res],
                scroll=ft.ScrollMode.ALWAYS
            )
        )
        
    def set_value(self, e):
        self.task = e.control.value
        

    def add(self, e, input_task):
        name = self.task
        status = 'incomplete'
        
        if name:
            self.db_execute(query='INSERT INTO tasks VALUES (?, ?)', params=[name,status])
            input_task.value = ''
            self.results = self.db_execute('SELECT * FROM tasks')
            self.update_task_list()
    
    def update_task_list(self):
        tasks = self.task_container()
        self.page.controls.pop()
        self.page.add(tasks)
        self.page.update()
        
    def tabs_changed(self,e):
        if e.control.selected_index == 0:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=['incomplete'])
            self.view = 'incomplete'
        elif e.control.selected_index == 1:
            self.results = self.db_execute('SELECT * FROM tasks WHERE status = ?', params=['complete'])
            self.view = 'complete'
        elif e.control.selected_index == 2:
            self.results = self.db_execute('SELECT * FROM tasks')
            self.view = 'all'
            
        self.update_task_list()
    def main_page(self):
        input_task = ft.TextField(hint_text="Digite aqui uma tarefa",
                                  color=ft.colors.BLACK,
                                  expand=True,
                                  on_change=self.set_value)

        input_bar = ft.Row(
            controls=[
                input_task,
                ft.FloatingActionButton(
                    on_click=lambda e: self.add(e, input_task),
                    icon=ft.icons.ADD)
                
            ]
        )

        tabs = ft.Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            label_color=ft.colors.BLUE_900,
            indicator_color=ft.colors.BLUE_700,
            tabs=[
                ft.Tab(text="Em Andamento"),
                ft.Tab(text="Finalizados"),
                ft.Tab(text="Todos"),
            ]
        )

        tasks = self.task_container()
        self.page.add(input_bar, tabs, tasks)


ft.app(target=ToDo)
