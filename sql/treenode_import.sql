SET session_replication_role = replica;
CREATE TEMPORARY TABLE indexed_table (
  rel regclass
);
INSERT INTO indexed_table (VALUES
('treenode_connector')
);


UPDATE pg_index
SET indisready=false
FROM indexed_table it
WHERE indrelid = it.rel;

BEGIN;
SET CONSTRAINTS ALL DEFERRED;

COPY treenode_connector(user_id, project_id, treenode_id, relation_id, connector_id, skeleton_id)
FROM '/data/data0/eric/fw_staging/connector_treenode.csv' WITH (FORMAT csv);

COMMIT;

UPDATE pg_index
SET indisready=true
FROM indexed_table it
WHERE indrelid = it.rel;