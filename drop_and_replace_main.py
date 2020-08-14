from scripts.drop_and_replace import create_view_node, add_dependant_view, drop_views, rebuild_structure, print_failed_views, \
    get_sql_code_from_file


def main():
    # Replace variables view_name and schema
    view_name = input('Name of the view to replace:')
    schema = input('Schema that holds the view:')
    # Replace the file content with the new definiton
    sql = get_sql_code_from_file('new_view_definition')

    root = create_view_node(view_name, schema, sql)  # The source view
    tree = add_dependant_view(root)  # All dependant views in a Tree structure
    print('Will attempt to drop and replace following structure:')
    tree.print_tree_from_node()
    inp = input('(y=continue)  (any other key = cancel)')

    if inp.lower() == 'y':
        drop_views(tree)  # Drop Cascade
        rebuild_structure(tree) # Attempts to rebuild all views
        open('output', 'w').close()
        print_failed_views(tree)
    else:
        print('cancelling')


if __name__ == '__main__':
    main()
