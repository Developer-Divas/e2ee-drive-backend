def match_doc(question: str, docs: dict):
    q = question.lower()

    scores = {}

    for key, content in docs.items():
        score = 0
        for word in q.split():
            if word in content.lower():
                score += 1
        scores[key] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return None

    return docs[best]
