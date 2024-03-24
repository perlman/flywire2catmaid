#
# Python wrapper to run the psql nearest neighbor query in parallel
#

# usage:
# seq -w 0 1000 | parallel -j 32 python run_psql.py --workers 1000 --worker {}

import argparse
import tempfile
import os

def get_sql(first_id, last_id, query_table_name = "eric_connector_treenode_lookup"):

    LIMIT = ""
    # LIMIT = " LIMIT 5"

    stmt = f"""

WITH import AS (
    SELECT
     3 AS user_id,
      1 AS project_id
), data AS (
  SELECT *
  -- FROM {query_table_name} {LIMIT}
  FROM {query_table_name} WHERE id BETWEEN {first_id} AND {last_id} {LIMIT}
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
      LIMIT 50
    ) closest_node(id, edge)
    ON closest_node.id = treenode.id
    ORDER BY ST_StartPoint(edge) <<->> ST_MakePoint(data.x, data.y, data.z)
    LIMIT 1
  ) closest(id)
    ON TRUE
)
SELECT * FROM closest_node;
-- SELECT * INTO TEMPORARY connector_treenode_lookup_results FROM closest_node;
-- SELECT * INTO connector_treenode_lookup_results FROM closest_node;

"""

    return stmt


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--max_id", type=int, default=244358224+1)
    parser.add_argument("--workers", type=int, default=10000)
    parser.add_argument("--worker", type=int, required=True) # Which worker is this?
    parser.add_argument("--workdir", default="/data/data0/eric/flywire_783_synapses/connector_work/")

    args = parser.parse_args()

    ids_per_worker = args.max_id // args.workers
    first_id = ids_per_worker * args.worker
    last_id = ids_per_worker * (args.worker + 1) - 1

    sql = get_sql(first_id, last_id)

    outfilename = os.path.join(args.workdir, f'{args.worker:06}.csv')

    with tempfile.NamedTemporaryFile() as tfp:
        tfp.write(sql.encode())
        tfp.flush()
        psql_cmd = f"psql -p 5447 --dbname=catmaid_flywire_m783 -U catmaid_user -f {tfp.name} --csv -o {outfilename}"
        print (psql_cmd)
        os.system(psql_cmd)

if __name__ == "__main__":
    main()
