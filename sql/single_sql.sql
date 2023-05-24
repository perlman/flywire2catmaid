\set query_neuron 48071148

EXPLAIN ANALYZE
WITH import AS (
    SELECT
      3 AS user_id,
      1 AS project_id
), data AS (
  SELECT *
  FROM eric_connector_treenode_lookup WHERE skeleton_id = :query_neuron
),
closest_node AS (
  /* Get closest node in skeleton */
  SELECT data.*, closest.id AS closest_treenode_id
  FROM data
  JOIN LATERAL (
    SELECT treenode.id
    FROM treenode
    WHERE skeleton_id = data.skeleton_id
    --ORDER BY ST_MakePoint(location_x, location_y, location_z) <<->> ST_MakePoint(data.x, data.y, data.z)
    ORDER BY SQRT(POWER(location_x-data.x,2)+POWER(location_y-data.y,2)+POWER(location_z-data.z,2))
    LIMIT 1
  ) closest(id)
    ON TRUE
)
SELECT * FROM closest_node;
