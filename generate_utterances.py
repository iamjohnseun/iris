from transformers import pipeline

def generate_utterances(question):
    # paraphrase = pipeline('paraphrase', model='tuner007/pegasus_paraphrase')
    paraphrase = pipeline('text2text-generation', model='tuner007/pegasus_paraphrase')
    paraphrases = paraphrase(question, num_return_sequences=5, clean_up_tokenization_spaces=True)
    return [p['generated_text'] for p in paraphrases]

# USAGE
# question = "Can I get a refund?"
# utterances = generate_utterances(question)
# print(utterances)
