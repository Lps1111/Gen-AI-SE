from typing import List, Dict, Any

def merge_context(graph_chunks: List[Dict[str, Any]], vector_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Returns unified list of chunks with fields:
    {chunk_id, source, text, origin, score}
    """
    merged = {}

    # Graph chunks get a default score
    for c in graph_chunks or []:
        cid = c["chunk_id"]
        merged[cid] = {
            "chunk_id": cid,
            "source": c.get("source", "unknown"),
            "text": c.get("text", ""),
            "origin": "graph",
            "score": 0.55,  # baseline
        }

    for c in vector_chunks or []:
        cid = c["chunk_id"]
        if cid in merged:
            # fuse scores and mark hybrid
            merged[cid]["origin"] = "hybrid"
            merged[cid]["score"] = max(merged[cid]["score"], c.get("score", 0.0))
            # prefer longer text if one is empty
            if not merged[cid]["text"] and c.get("text"):
                merged[cid]["text"] = c["text"]
        else:
            merged[cid] = {
                "chunk_id": cid,
                "source": c.get("source", "unknown"),
                "text": c.get("text", ""),
                "origin": "vector",
                "score": float(c.get("score", 0.0)),
            }

    # sort by score
    out = list(merged.values())
    out.sort(key=lambda x: x["score"], reverse=True)
    return out
