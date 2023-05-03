import flask
import PyPDF2
import re

import nltk
nltk.download('punkt')
nltk.download('stopwords')


from flask import Flask, render_template, request
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from heapq import nlargest




app = Flask(__name__, template_folder='C:\\Users\\a3ter\\Downloads\\text_summarizer\\text_summarizer')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    # Get the uploaded PDF file
    pdf_file = request.files['pdf_file']

    # Read the PDF file
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    # num_pages = pdf_reader.numPages
    pdf_text = ''
    for page_num in range(len(pdf_reader.pages)):
        # page = pdf_reader.getPage(page_num)
        # pdf_text += page.extractText()
        # pdf_reader.pages[page].extract_text()
        pdf_text += pdf_reader.pages[page_num].extract_text()

    # Summarize the PDF text
    # (Replace this with your own summarization code)
    # Tokenize the text into sentences
    sentences = sent_tokenize(pdf_text)

    # Tokenize the text into words
    words = word_tokenize(pdf_text)

    # Remove stop words
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if not word.lower() in stop_words]

    # Calculate the frequency of each word
    word_frequencies = {}
    for word in words:
        if word not in word_frequencies:
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

    # Calculate the weighted frequency of each sentence
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_frequencies:
                if len(sentence.split(' ')) < 30:
                    if sentence not in sentence_scores:
                        sentence_scores[sentence] = word_frequencies[word]
                    else:
                        sentence_scores[sentence] += word_frequencies[word]

    # Get the top 5 sentences with highest scores
    summary_sentences = nlargest(10, sentence_scores, key=sentence_scores.get)
    cleaned_sentences = [sentence.replace("\n", " ") for sentence in summary_sentences]
    summarized_text = ' '.join(cleaned_sentences)


    print(summarized_text)
    return render_template('summary.html', summarized_text=summarized_text)

@app.route('/qa', methods=['POST'])
def qa():
    # Get the summarized text
    summarized_text = request.form['summarized_text']

    # Extract knowledge from the summarized text
    knowledge_base = {}
    sentences = summarized_text.split('. ')
    for sentence in sentences:
        match = re.match(r'The (.*) is (.*)', sentence)
        if match:
            subject = match.group(1)
            obj = match.group(2)
            knowledge_base[subject] = obj

    # Define a function to answer questions
    def answer_question(question):
        answer_found = False
        for subject, obj in knowledge_base.items():
            if question.lower().startswith('what is the ' + subject.lower()):
                answer = obj
                answer_found = True
                break
            elif question.lower().startswith('where is the ' + subject.lower()):
                answer = obj
                answer_found = True
                break
        if not answer_found:
            answer = "I'm sorry, I don't know the answer to that question."
        return answer

    # Answer the user's question
    question = request.form['question']
    answer = answer_question(question)

    return render_template('qa.html', question=question, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)