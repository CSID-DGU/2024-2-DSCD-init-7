from sentence_transformers import SentenceTransformer
import torch

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def get_similarities(n_okr, objectives):
    n_okr_embedding = model.encode(n_okr, convert_to_tensor=True)
    return [
        torch.nn.functional.cosine_similarity(
            n_okr_embedding, model.encode(objective, convert_to_tensor=True), dim=-1
        ).item()
        for objective in objectives
    ]

def calculate_weighted_scores(n_okr, member_okr):
    grouped_df = member_okr.groupby('Member')
    weighted_sums = []

    for member, group in grouped_df:
        objectives = group['Objective'].tolist()
        objective_scores = group['Objective Score'].tolist()
        similarities = get_similarities(n_okr, objectives)
        total_weighted_score = sum(sim * score for sim, score in zip(similarities, objective_scores))
        weighted_sums.append((member, total_weighted_score / len(objectives) if objectives else 0))
    
    return weighted_sums
