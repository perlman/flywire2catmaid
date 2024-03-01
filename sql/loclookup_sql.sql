WITH import AS (
    SELECT
     3 AS user_id,
      1 AS project_id
), data AS (
  SELECT *
  FROM connector_treenode_lookup --LIMIT 5000
  -- data(id, relation_id, skeleton_id, x, y, z)
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
)
-- SELECT * INTO TEMPORARY connector_treenode_lookup_results FROM closest_node;
SELECT * INTO connector_treenode_lookup_results FROM closest_node;
