import re


class ViewNode(object):
    def __init__(self,
                 sql: str,
                 name: str,
                 schema: str,
                 parent=None):
        self.parent = parent # Single object
        self.name = name
        self.schema = schema
        self.children = []  # Array of objects
        self.sql_definition = sql
        self.auto_sql = sql
        self.failed_to_build = False
        self.exception = ''

    def __str__(self):
        return f'Name: {self.name} \nSchema: {self.schema} \nChildren: {len(self.children)} \nParent: {self.parent.name} \n SQL-Query: {self.sql_definition}'

    def add_children(self, child):
        child.parent = self
        self.children.append(child)

    def rebuild_sql_view(self, curs, mode='auto'):
        # Execute sql to rebuild the view on fail abort transaction and add to failed views
        if self.parent is not None and self.parent.failed_to_build:
            self.failed_to_build = True
            self.exception = f'Source view {self.parent.name} failed to build\n'
            return
        try:
            sql_string = f'''create or replace view {self.schema}."{self.name}" as {self.sql_definition}'''
            curs.execute(sql_string)
            curs.connection.commit()
        except Exception as e:
            curs.execute("ROLLBACK")
            self.exception = e.__str__()
            # Handle columns deleted from the original view
            if self.exception.startswith('column') and mode == 'auto':
                self.handle_missing_columns(curs)
            else:
                self.failed_to_build = True

    def delete_sql_view(self, curs):
        sql_string = f'''DROP VIEW {self.schema}."{self.name}" CASCADE'''
        curs.execute(sql_string)
        curs.connection.commit()

    def print_tree_from_node(self, offset=0):
        spaces = ' ' * offset
        offset += 2
        print(f'{spaces}{self.name}')
        for child in self.children:
            child.print_tree_from_node(offset)

    def get_name(self):
        return self.name

    def handle_missing_columns(self, curs):
        missing_col = self.exception.split()[1]
        self.auto_sql = re.sub(rf",\s*\b(?=\w){re.escape(missing_col)}\b(?!\w)", '', self.auto_sql)
        sql_string = f'''create or replace view {self.schema}."{self.name}" as {self.auto_sql}'''
        try:
            curs.execute(sql_string)
            curs.connection.commit()
            self.failed_to_build = False
        except Exception as e:
            self.exception = e.__str__()
            self.handle_missing_columns(curs)




