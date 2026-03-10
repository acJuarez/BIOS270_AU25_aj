import argparse
import sqlite3
import numpy as np
import h5py


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--database_path", type=str, required=True)
    p.add_argument("--H5_path", type=str, required=True)
    p.add_argument("--record_id", type=str, required=True)
    p.add_argument("--metric", type=str, required=True, choices=["mean_embeddings", "mean_mid_embeddings"])
    p.add_argument("--output_path", type=str, required=True)
    p.add_argument("--h5_ids_key", type=str, default="protein_ids")
    return p.parse_args()


class BacteriaDatabase:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)

    def get_protein_ids_from_record_id(self, record_id: str):
        q = """
        SELECT DISTINCT protein_id
        FROM gff
        WHERE record_id = ?
          AND protein_id IS NOT NULL
        """
        cur = self.conn.execute(q, (record_id,))
        return [row[0] for row in cur.fetchall()]

    def close(self):
        self.conn.close()


def _to_str_list(arr):
    out = []
    for x in arr:
        if isinstance(x, (bytes, np.bytes_)):
            out.append(x.decode("utf-8"))
        else:
            out.append(str(x))
    return out


def main():
    args = parse_args()

    db = BacteriaDatabase(args.database_path)
    protein_ids = db.get_protein_ids_from_record_id(args.record_id)
    db.close()

    if not protein_ids:
        raise SystemExit(f"No protein_ids found for record_id={args.record_id!r}")

    with h5py.File(args.H5_path, "r") as h5:
        if args.h5_ids_key not in h5:
            raise KeyError(f"Missing {args.h5_ids_key!r} in H5. Keys: {list(h5.keys())}")

        ids = _to_str_list(h5[args.h5_ids_key][...])
        id_to_idx = {pid: i for i, pid in enumerate(ids)}

        if args.metric not in h5:
            raise KeyError(f"Missing {args.metric!r} in H5. Keys: {list(h5.keys())}")

        emb = h5[args.metric]

        missing = [pid for pid in protein_ids if pid not in id_to_idx]
        if missing:
            raise SystemExit(f"{len(missing)} proteins not in H5 ids. Example: {missing[:10]}")

        idxs = np.array([id_to_idx[pid] for pid in protein_ids], dtype=np.int64)


        # unique sorted indices for h5py (strictly increasing)
        uniq_idxs, inv = np.unique(idxs, return_inverse=True)
        # read each unique row once
        uniq_mat = np.asarray(emb[uniq_idxs, :])

        # expand back to original order (and duplicates if they exist)
        mat = uniq_mat[inv, :]

    if mat.ndim != 2 or mat.shape[1] != 164:
        raise SystemExit(f"Unexpected shape {mat.shape}, expected (N, 164)")

    np.save(args.output_path, mat)
    print(f"Saved {mat.shape} -> {args.output_path}")


if __name__ == "__main__":
    main()