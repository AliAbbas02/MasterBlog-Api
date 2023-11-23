from flask import Flask, render_template, url_for, redirect,request
import json
app = Flask(__name__)


# @app.route('/', methods=['GET', 'POST'])
# def login():
    
#     return render_template('loginpage.html')

# def get_users():
#     with open('backend\users.json') as f:
#         users = json.loads(f)
#         return users
# def add_new_user(user):
#     all_users = get_users()
#     new_id = all_users[-1]['id'] + 1
#     user['id'] = new_id
#     all_users.append(user)
#     with open('\backend\user.json', 'w') as f:
#         f = json.dump(all_users)
    
    
# @app.route('/register', methods=['GET','POST'])
# def register():
#     if request.method == 'post':
#         user_name = request.args.get('user')
#         password = request.args.get('password')
#         new_user = {'name': user_name, 'password': password}
#         add_new_user(new_user)
#         return redirect('login')


#     return render_template('register.html')

@app.route('/api/posts', methods=['GET'])
def home():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
