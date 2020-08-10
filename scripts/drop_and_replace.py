from scripts.viewnode import ViewNode
import sqlalchemy
import os

USER = os.environ.get('USER', None)
PASSWORD = os.environ.get('PASSWORD', None)
HOST = os.environ.get('HOST', None)
DATABASE = os.environ.get('DATABASE', None)

HOST_ENGINE = sqlalchemy.create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}/{DATABASE}')
DB_CONNECTION = HOST_ENGINE.raw_connection()


def create_view_node(view_name: str, view_schema: str, sql: str) -> ViewNode:
    root = ViewNode(sql, view_name, view_schema)
    return root


def add_dependant_view(root_node: ViewNode) -> ViewNode:
    dependant_views = retrieve_dependant_views(root_node.name, root_node.schema)
    if not dependant_views:
        return root_node
    for view in dependant_views:
        # view[1]=name view[0]=schema
        sql = retrieve_sql_definition(view[1], view[0])
        dependant_view = create_view_node(view[1], view[0], sql[0])
        add_dependant_view(dependant_view)
        root_node.add_children(dependant_view)
    return root_node


def retrieve_dependant_views(src_view: str, schema: str) -> list:
    curs = DB_CONNECTION.cursor()
    sql = get_sql_code_from_file('get_dependant_views', src_view, schema)
    curs.execute(sql)
    result = curs.fetchall()
    return result


def retrieve_sql_definition(src_name: str, src_schema: str):
    curs = DB_CONNECTION.cursor()
    sql = get_sql_code_from_file('get_sql_definition', src_schema, src_name)
    curs.execute(sql)
    result = curs.fetchall()
    return result[0]


def drop_views(src_view: ViewNode):
    curs = DB_CONNECTION.cursor()
    src_view.delete_sql_view(curs)


def rebuild_structure(tree: ViewNode):
    curs = DB_CONNECTION.cursor()
    print(f'Building {tree.name}')
    tree.rebuild_sql_view(curs)
    for child in tree.children:
        rebuild_structure(child)


def print_failed_views(view: ViewNode):
    # This will print views that failed
    failed_views = get_failed_views(view, dict())
    open('output', 'w').close()

    for x, y in failed_views.items():
        if y.failed_to_build:
            print(f'''\n ---Failed to build view {y.schema}.{y.name}---\nException: {y.exception}\nSQL: {y.sql}\n''')
            out = open('output', 'a')
            out.write(f'''\n ---Failed to build view {y.schema}.{y.name}---\nException: {y.exception}\nSQL: {y.sql}\n''')
            out.close()


def get_failed_views(view: ViewNode, view_status: dict) -> dict:
    if view.name in view_status:
        if not view.failed_to_build:
            view_status[view.name] = view
    else:
        view_status[view.name] = view

    for dependant_view in view.children:
        get_failed_views(dependant_view, view_status)
    return view_status


def get_sql_code_from_file(filename: str, *parameters) -> str:
    fd = open(f'drop_and_replace/sql/{filename}.sql')
    sql = fd.read()
    sql = sql.format(*parameters)
    fd.close()
    return sql
