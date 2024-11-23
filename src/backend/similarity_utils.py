import torch
from sentence_transformers import SentenceTransformer

def get_similarities(model, n_okr, objectives):
    """OKR와 각 Objective 간의 유사도를 계산합니다."""
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    similarities = [
        torch.nn.functional.cosine_similarity(
            n_okr_embedding, 
            model.encode(obj, convert_to_tensor=True), 
            dim=-1
        ).item()
        for obj in objectives
    ]
    return similarities

def calculate_weighted_scores(member_okr_df, model, n_okr):
    """가중 점수를 계산합니다."""
    grouped = member_okr_df.groupby('Member')
    scores = []

    for member, group in grouped:
        objectives = group['Objective'].tolist()
        objective_scores = group['Objective Score'].tolist()
        similarities = get_similarities(model, n_okr, objectives)

        total_score = sum(sim * score for sim, score in zip(similarities, objective_scores))
        scores.append((member, total_score / len(similarities) if similarities else 0))

    return scores
