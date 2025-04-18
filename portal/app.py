import os
import json
import time
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory

from langchain_google_vertexai import ChatVertexAI
from quiz import generate_quiz_question
from answer import answer_thinking
from onramp_workaround import get_next_region,get_next_thinking_region
from google.cloud import storage  

from render import render_assignment_page

# ENV SETUP
project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")  # Get project ID from env
COURSE_BUCKET_NAME = os.environ.get("COURSE_BUCKET_NAME", "aidemy-course")  


app = Flask(__name__)

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')
@app.route('/quiz',methods=['GET'])
def quiz():
    return render_template('quiz.html')
@app.route('/courses',methods=['GET'])
def courses():
    return render_template('courses.html')
@app.route('/assignment',methods=['GET'])
def assignment():
    return render_template('assignment.html')



#curl -X GET -H "Content-Type: application/json" http://localhost:8080/generate_quiz 


@app.route('/generate_quiz', methods=['GET'])
def generate_quiz():
    """Generates a quiz with a specified number of questions."""
    #num_questions = 5  # Default number of questions
    # Can I turn this into Langgraph
    quiz = []
    quiz.append(generate_quiz_question("teaching_plan.txt", "easy", get_next_old_region()))
    quiz.append(generate_quiz_question("teaching_plan.txt", "medium", get_next_old_region()))
    quiz.append(generate_quiz_question("teaching_plan.txt", "hard", get_next_old_region()))

    return jsonify(quiz)



@app.route('/check_answers', methods=['POST'])
def check_answers():
    try:
        submitted_data = request.json  # Get the complete submitted data
        quiz = submitted_data.get('quiz')  # Extract the quiz data
        user_answers = submitted_data.get('answers') # Extract answers
        print(f"submitted_data: {submitted_data}")

        if quiz is None or user_answers is None:
            return jsonify({"error": "Missing quiz or answer data"}), 400

        results = []
        for i in range(len(user_answers)):
            question_data = quiz[i]
            question = question_data['question']
            options = question_data['options']
            correct_answer = question_data['answer']
            user_answer = user_answers[i]

            print(f"Question: {question}")
            print(f"User Answer: {user_answer}")
            print(f"Correct Answer: {correct_answer}")

            is_correct = (user_answer == correct_answer)

            reasoning=None
            if(not is_correct):
                time.sleep(60)
                region = get_next_thinking_region()
                reasoning = answer_thinking(question, options, user_answer, correct_answer, region)
            else:
                reasoning = "You are correct!"

            results.append({
                "question": question,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "reasoning": reasoning
            })

        return jsonify(results)

    except Exception as e:
        print(f"Error checking answers: {e}")
        return jsonify({"error": str(e)}), 500



@app.route('/download_course_audio/<int:week>')
def download_course_audio(week):
    filename = f"course-week-{week}.wav"
    local_path = "/tmp" 
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(COURSE_BUCKET_NAME)
        blob = bucket.blob(filename)

        local_file_path = os.path.join(local_path, filename)
        blob.download_to_filename(local_file_path)
        
        # Serve the downloaded file
        return send_from_directory(local_path, filename, as_attachment=True)

    except Exception as e:
        print(f"Error generating download link: {e}")
        return "Error generating download link", 500 



## Add your code here
        
## Add your code here

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
