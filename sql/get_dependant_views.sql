select distinct dependent_ns.nspname dependent_schema
        , dependent_view.relname as dependent_view
from pg_depend
    join pg_rewrite ON pg_depend.objid = pg_rewrite.oid
    join pg_class as dependent_view ON pg_rewrite.ev_class = dependent_view.oid
    join pg_class as source_table ON pg_depend.refobjid = source_table.oid
    join pg_attribute ON pg_depend.refobjid = pg_attribute.attrelid AND pg_depend.refobjsubid = pg_attribute.attnum
    join pg_namespace dependent_ns ON dependent_ns.oid = dependent_view.relnamespace
    join pg_namespace source_ns ON source_ns.oid = source_table.relnamespace
where source_table.relname = '{0}'
and source_ns.nspname = '{1}'
