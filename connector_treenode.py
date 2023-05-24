# 
# Script to look up information on each connector on a *per skeleton* basis.
# This lets us (attempt) to take advantage of quick skeleton lookup in CATMAID
#

#
# Single usage:
#   python connector_treenode.py  --rootmap /data/data0/eric/fw_staging/test_rootmap_000.csv 
# Bulk usage:
#   python connector_treenode.py  --rootmap /data/data0/eric/fw_staging/test_rootmap_000.csv  --out out --worker 0 --workers 2
#

import os
import time
import argparse
import psycopg2


def get_connector_treenoes(conn, skel_id):
    start = time.time()

    query = f"""
WITH data AS (
  SELECT *
  FROM eric_connector_treenode_lookup WHERE skeleton_id = {skel_id}
),
closest_node AS (
  SELECT data.*, closest.id AS closest_treenode_id
  FROM data
  JOIN LATERAL (
    SELECT treenode.id
    FROM treenode
    WHERE skeleton_id = data.skeleton_id
    ORDER BY SQRT(POWER(location_x-data.x,2)+POWER(location_y-data.y,2)+POWER(location_z-data.z,2))
    LIMIT 1
  ) closest(id)
    ON TRUE
)
SELECT 3 as user_id, 1 as project_id, closest_treenode_id as treenode_id,
    relation as relation_id, id as connector_id, skeleton_id as skeleton_id
FROM closest_node ;
    """

    # print(query)
    cursor = conn.cursor()
    cursor.execute(query)

    results = cursor.fetchall()

    end = time.time()
    print("%s took %ss." %  (skel_id, end - start))
    return results

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--rootmap", help="TSV file mapping root_id to skeleton_id", required=True)
    parser.add_argument("--verbose", '-v', action="store_true", default=False)
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--worker", type=int, default=1, help="Which worker is this")
    parser.add_argument("--prime", type=int, default=3, help="Divisor of skeleton IDs before mode... set to 3 due to current nubering of n..n+3...n+6")
    parser.add_argument("--single", default=False, action="store_true", help="Process one skeleton only [for testing]")
    parser.add_argument("--out", required=True, type=str, help="Output directory path")
    parser.add_argument("--user_id", default=3, type=int)
    parser.add_argument("--project_id", default=1, type=int)
    args = parser.parse_args()

    try:
        conn = psycopg2.connect("port=5446 dbname='catmaid_flywire_m630' user='catmaid_user' host='localhost' password='IcthamhorAs'")
        print(conn)
    except:
        raise

    outfilename = os.path.join(args.out, f"connector_treenode_{args.worker:03d}.csv")
    outfd = open(outfilename, "w")


    skel_ids = []
    # rootmap = {}
    if args.rootmap:
        for line in open(args.rootmap, "r"):
            line = line.strip().split(',')
            # rootmap[int(line[0])] = int(line[1])
            skel_ids.append(int(line[1]))


    for skel_id in skel_ids:
        if (skel_id // args.prime) % args.workers == args.worker:
            print(skel_id)
            results = data = get_connector_treenoes(conn, skel_id)
            # [(3, 1, 160050486, 20, 635827193, 48000027), ...]
            for result in results:
                outfd.write(','.join(map(str, result)) + '\n')

            outfd.flush()
        else:
            continue

        if args.single:
            break


    outfd.close()

if __name__ == "__main__":
    main()
