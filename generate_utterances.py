from transformers import pipeline

def generate_utterances(question):
    paraphrase = pipeline('paraphrase', model='tuner007/pegasus_paraphrase')
    paraphrases = paraphrase(question, num_return_sequences=10)
    return [paraphrase['generated_text'] for paraphrase in paraphrases]

# USAGE

# question = "Can I get a refund?"
# utterances = generate_utterances(question)
# print(utterances)
