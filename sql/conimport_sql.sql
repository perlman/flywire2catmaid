WITH import AS (
    SELECT
     21 AS user_id,
      1 AS project_id
), data AS (
  SELECT *
  FROM (VALUES
    (6, 'pre', 10, 108400, 57760, 40),
    (6, 'post', 10541812, 108400, 57760, 40)
  ) data(id, type, skeleton_id, x, y, z)
),
relation_info AS (
    SELECT
      pre.id AS presynaptic_to_rel_id,
      post.id AS postsynaptic_to_rel_id
    FROM import
    JOIN LATERAL
      (SELECT id FROM relation WHERE project_id = import.project_id AND relation_name = 'presynaptic_to') pre
      ON TRUE
    JOIN LATERAL
      (SELECT id FROM relation WHERE project_id = import.project_id AND relation_name = 'postsynaptic_to') post
      ON TRUE
),
max_ids AS MATERIALIZED (
   SELECT a.id AS location_id, b.id AS data_id FROM
      (SELECT MAX(id) FROM location) a(id),
      (SELECT MAX(id) FROM data) b(id)
),
id_setup AS (
  /* In order to make a mapping from original IDs to CATMAID IDs for connector
   * nodes easier, we will record the current maximum and claim the next N ids
   * for the import.
   */
   SELECT SETVAL('location_id_seq', (SELECT location_id + data_id FROM max_ids))
),
connector_locations AS (
  /* Compute connector location as average between all reference points.
  */
  SELECT data.id, AVG(x) AS x, AVG(y) AS y, AVG(Z) AS z
  FROM data
  GROUP BY id
),
referenced_connectors AS (
  /* Create new connector nodes with ID initial max ID + FLyWire ID */
  INSERT INTO connector (id, user_id, editor_id, project_id, location_x, location_y, location_z)
  SELECT max_ids.location_id + cl.id, import.user_id, import.user_id, import.project_id, x, y, z
  FROM connector_locations cl, max_ids, import
  ON CONFLICT DO NOTHING
  RETURNING connector.id
),
closest_node AS (
  /* Get closest node in skeleton */
  SELECT data.*, closest.id AS closest_treenode_id
  FROM data
  JOIN LATERAL (
    SELECT treenode.id
    FROM treenode
    JOIN (
      WITH skeleton_edge AS MATERIALIZED (
        SELECT te.id, te.edge
        FROM treenode_edge te
        JOIN (
            SELECT id
            FROM treenode t
            WHERE skeleton_id = data.skeleton_id
        ) skeleton_node(id)
        ON skeleton_node.id = te.id
        WHERE project_id = 1
      )
      SELECT id, edge
      FROM skeleton_edge
      ORDER BY edge <<->> ST_MakePoint(data.x, data.y, data.z)
      LIMIT 100
    ) closest_node(id, edge)
    ON closest_node.id = treenode.id
    ORDER BY ST_StartPoint(edge) <<->> ST_MakePoint(data.x, data.y, data.z)
    LIMIT 1
  ) closest(id)
    ON TRUE
),
linked_pre_nodes AS (
  INSERT INTO treenode_connector (user_id, project_id, relation_id, treenode_id, connector_id, skeleton_id)
  SELECT import.user_id, import.project_id, relation_info.presynaptic_to_rel_id, closest_node.closest_treenode_id,
    max_ids.location_id + closest_node.id, closest_node.skeleton_id
  FROM closest_node, max_ids, import, relation_info
  WHERE type = 'pre'
  RETURNING connector_id
),
linked_post_nodes AS (
  INSERT INTO treenode_connector (user_id, project_id, relation_id, treenode_id, connector_id, skeleton_id)
  SELECT import.user_id, import.project_id, relation_info.postsynaptic_to_rel_id, closest_node.closest_treenode_id,
    max_ids.location_id + closest_node.id, closest_node.skeleton_id
  FROM closest_node, max_ids, import, relation_info
  WHERE type = 'post'
  RETURNING connector_id
)
SELECT
  imported_connector.id - max_ids.location_id AS flywire_synapse_id,
  imported_connector.id AS catmaid_connector_id
FROM max_ids, (
  SELECT connector_id AS id
  FROM (
    SELECT * FROM linked_pre_nodes
    UNION ALL
    SELECT * FROM linked_post_nodes
  ) linked_nodes
  GROUP BY connector_id
) imported_connector;
