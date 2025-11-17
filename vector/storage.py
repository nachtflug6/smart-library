import numpy as np

class VectorStore:
    def __init__(self, dim):
        self.vectors = np.zeros((0, dim), dtype=np.float32)
        self.id_to_idx = {}
        self.idx_to_id = []
    
    def add(self, vid, vec):
        self.vectors = np.vstack([self.vectors, vec])
        self.id_to_idx[vid] = len(self.idx_to_id)
        self.idx_to_id.append(vid)

    def delete(self, vid):
        idx = self.id_to_idx.pop(vid)
        last_idx = len(self.idx_to_id) - 1
        
        # move last vector into deleted slot
        self.vectors[idx] = self.vectors[last_idx]
        last_vid = self.idx_to_id[last_idx]
        self.id_to_idx[last_vid] = idx
        
        # shrink
        self.vectors = self.vectors[:-1]
        self.idx_to_id.pop()

    def similarity(self, vec):
        # cosine similarity
        return (self.vectors @ vec) / (
            np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(vec)
        )