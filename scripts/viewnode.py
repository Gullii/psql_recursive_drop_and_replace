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
        self.sql = sql
        self.failed_to_build = False
        self.exception = ''

    def __str__(self):
        return f'Name: {self.name} \nSchema: {self.sql} \nChildren: {len(self.children)} \nParent: {self.parent.name} \n SQL-Query: {self.sql}'

    def add_children(self, child):
        child.parent = self
        self.children.append(child)

    def rebuild_sql_view(self, curs):
        # Execute sql to rebuild the view on fail abort transaction and add to failed views
        if self.parent is not None and self.parent.failed_to_build:
            self.failed_to_build = True
            self.exception = f'Source view {self.parent.name} failed to build\n'
            return
        try:
            sql_string = f'''create or replace view {self.schema}."{self.name}" as {self.sql}'''
            curs.execute(sql_string)
            curs.connection.commit()
        except Exception as e:
            curs.execute("ROLLBACK")
            self.exception = e.__str__()
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


