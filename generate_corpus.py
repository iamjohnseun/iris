import json

from generate_utterances import generate_utterances

def generate_corpus(qa_pairs):
    corpus = []
    for pair in qa_pairs:
        utterances = generate_utterances(pair['question'])
        corpus.append({
            "intent": pair['intent'],
            "utterances": utterances,
            "answer": [pair['answer']]
        })
    return corpus
  
# USAGE

# qa_pairs = [{"question": "Can I get a refund?", "answer": "Yes, you can get a refund.", "intent": "faq.refund"}]
# corpus = generate_corpus(qa_pairs)

# with open('corpus.json', 'w') as f:
#     json.dump(corpus, f, indent=4)

# print(corpus)
