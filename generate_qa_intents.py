from transformers import pipeline

# Load pre-trained models
question_generator = pipeline('e2e-qg')
intent_classifier = pipeline('text-classification', model='JoanaLiu/bert_base_faq')

def generate_questions_and_intents(sentences):
    qa_pairs = []
    for sentence in sentences:
        questions = question_generator(sentence)
        intent = intent_classifier(sentence)[0]['label']
        for q in questions:
            qa_pairs.append({
                "question": q['question'],
                "answer": sentence,
                "intent": f"faq.{intent.lower().replace(' ', '_')}"
            })
    return qa_pairs

# USAGE

# sentences = ["Your extracted sentences here..."]
# qa_pairs = generate_questions_and_intents(sentences)
# print(qa_pairs)