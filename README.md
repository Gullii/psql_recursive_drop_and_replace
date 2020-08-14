# psql_recursive_drop_and_replace
Drop and replace a view with dependant view

# This repo is Work in Progress

With this script it's possible to replace the SQL Definition of any view in a Postgres Database even if other views are dependant on it.

## Usage
1.Add the following Environment Variables to the Project
```
USER = Username to login to the database
PASSWORD = Password to login to the database 
HOST = Host address
DATABASE = Databasename
```

2. Replace the SQL in `new_view_definition.sql` with the new definiton of your view.

3. Run `drop_and_replace_main.py` and follow command line output

4. Any views that failed will be printed into an output file with the Exception and old SQL-Definiton to make it easier to create the view manually

## TODO
-Move all needed input to command line  
-Fix exceptions for droped columns  
-Optimize performance  


