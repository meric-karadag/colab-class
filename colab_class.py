from flask import Flask, request
import json
import requests
app = Flask(__name__)
import signal

# Set the host url on which the application will run
host_url = "http://localhost:5000/"
no_questions = 1

# Hello route for testing purposes
@app.route('/hello')
def hello():
    return 'Hello, World!'

# Initializes answers.json file on which every function operates on
# And sets first questions answer based on the request
@app.route('/init', methods = ["POST"])
def initialize():
    data = request.get_json()
    answer = data["answer"]
    file = open("answers.json", "w")

    file.write('[{"id": 1, "truth":' + f'{answer}' + ', "student_ids_answers": {}, "trues": {}, "falses": {}}]')

    file.close()

    return 'First question has been succesfully created'

# Listens for requests for the given amount of time
@app.route("/listen-requests", methods = ["POST"])
def listen_requests():
    data = request.get_json()
    seconds = data["seconds"]
    def handler(signum, frame):
    # This function will be called when the alarm goes off
        raise Exception("Time's up!")

    # Set up the alarm signal to go off after 10 seconds
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)

    try:
        app.run(host = "0.0.0.0")
    except Exception as e:
        # If an exception is raised by the handler function, catch it here
        print("Exception:", e)
    finally:
        # Cancel the alarm when the program is finished
        signal.alarm(0)
    
# Writes students' answer to answers.json file
# Keeps track of students who answered the question right and wrong.
@app.route("/submit-answer", methods=["POST"])
def submit_answer():
    data = request.get_json()
    question_id = data["question_id"]
    student_id = data["student_id"]
    answer = data["answer"]
    is_true_ans = None

    with open('answers.json', 'r') as infile:
        answers_json = json.load(infile)


    for question in answers_json:
        if question["id"] == question_id:
            real_answer = question["truth"]
            '''question["student_ids"].append(student_id)
            question["answers"].append(answer)'''
            question["student_ids_answers"][str(student_id)] = answer
            # Give feedback to student's answer
            if real_answer == answer:
                question["trues"][str(student_id)] = student_id
                if str(student_id) in question["falses"].keys():
                    question["falses"].pop(str(student_id))
                is_true_ans = True
                
            else:
                question["falses"][str(student_id)] = student_id
                is_true_ans = False
                
    # Write updated Python object back to JSON file
    with open('answers.json', 'w') as outfile:
        json.dump(answers_json, outfile)

    if is_true_ans:
        return "Answer submitted succesfully, Correct answer!"
    else:
        return "Answer submitted succesfully, however your answer was incorrect"

# Allows teacher to post new questions and collect their answers
# Creates a new question with the given question id and true answer of the question
@app.route("/new-question", methods = ["POST"])
def new_question():
    data = request.get_json()
    question_id = data["question_id"]
    answer = data["answer"]

    # Open a file for reading and writing in the current working directory
    file = open("answers.json", "r+")

    
    contents = file.read()

    # Insert some text at a specific position in the file
    position = len(contents) - 1
    file.seek(position)
    file.write('\n' + ', {' + f'"id": {question_id}, "truth": {answer},' + '"student_ids_answers": {}, "trues": {}, "falses": {}}]')

    # Close the file
    file.close()

    return f"Question with question id = {question_id} has been succesfully added!"

# Allows teacher to see the total number of students who answered
# question with the given question id and the percentage of true answers.
@app.route("/get-summary", methods = ["POST"])
def get_summary():
    data = request.get_json()
    question_id = data["question_id"]
    
    with open('answers.json', 'r') as infile:
        answers_json = json.load(infile)
    
    for question in answers_json:
        if question["id"] == question_id:
            num_trues = len(question["trues"])
            num_falses = len(question["falses"])
    
    total = num_trues + num_falses
    percentage = 100 * num_trues / total

    return f"A total number of {total} students answered the question.\n\
    {percentage}% of them answered the question right."

# Basic function for testing purposes
def test_server():
    url = host_url + "hello"
    response = requests.get(url)
    print(response.text)

# Sends request to 
# Initiate answers.json and 
# sets first question's answer = 'answer' 
def init_fist_question(answer):
    data = {"answer" : answer}
    url = host_url + "init"
    response = requests.post(url, json = data)
    print(response.text)

# Sends request to create a new
# question with id = 'question_id'
# sets question's answer = 'answer'
def create_question(answer, question_id = no_questions+1):
    global no_questions
    no_questions += 1 
    data = {"question_id": question_id, "answer": answer}
    url = host_url + "new-question"
    response = requests.post(url, json = data)
    print(response.text)

# Sends request to collect answers 
# from students for 'seconds' seconds
def collect_answers(seconds):
    data = {"seconds": seconds}
    url = host_url + "listen-requests"
    response = requests.post(url, json = data)
    print(response.text)

# Sends request to answer the question with
# question id = "question_id" and answer = 'answer'
# Students also should provide students id = 'student_id'
def submit_answer(question_id, student_id, answer):
    data = {"question_id": question_id, "student_id": student_id, "answer": answer}
    url = host_url + "submit-answer"
    response = requests.post(url, json=data)
    print(response.text)

# Sends request to view summary(stats) of
# question with question id = 'question_id' 
def question_summary(question_id):
    url = host_url + "get-summary"
    data = {"question_id": question_id}
    response = requests.post(url, json = data)
    print(response.text)

# Let the server listen the requests for 
# "seconds" seconds
def listen_my_requests(seconds):
    def handler(signum, frame):
    # This function will be called when the alarm goes off
        raise Exception("Time's up!")

    # Set up the alarm signal to go off after 10 seconds
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)

    try:
        app.run(host = "0.0.0.0")
    except Exception as e:
        # If an exception is raised by the handler function, catch it here
        print("Exception:", e)
    finally:
        # Cancel the alarm when the program is finished
        signal.alarm(0)