from flask import Flask, jsonify, redirect, request, url_for, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    return jsonify(POSTS)

@app.errorhandler(400)
def bad_request_error(error):
    
    return jsonify({'error': 'Missing Info'}), 400

@app.route('/api/posts', methods=['POST'], )
def add(): 
    #get post from url
    post:dict = request.get_json()
    #checking if user has entered all the details
    if 'title' in post and 'content' in post:
       #get all ids from posts in database
       all_ids:list = [post['id'] for post in POSTS ]
        #checking if posts in database is not an empty list
       if len(all_ids) != 0:
           #assing max id with increment to new post
           POSTS.append({'id': max(all_ids) + 1 ,'title': post['title'],
                      'content': post['content']})
        #if post list is empty
       else:
           POSTS.append({'id': 1 ,'title': post['title'],
                      'content': post['content']})
       #return 201 response for post succesfully created
       return jsonify (POSTS[-1]), 201
    
    else:
    #if any missing info handle error
        abort(400)

def fetch_post(id):
    '''a fucntion that fetches the index of post if id matched
    Args:
        id(int): post id entered by user
    '''
    x:int = 0
    for post in POSTS:
        if id == post['id']:
            return x 
        x += 1
    return None


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'post not found with provided id'}),404

    
@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete(id):
    #checking post with id provided if it exists and return its index
    post_index:int = fetch_post(id)
    #if check has index returned delete the post in database
    if post_index != None:
        del POSTS[post_index]
        return jsonify({'message': 'Post with id {} deleted'.format(id)})
    
    #if id not found send response 404
    abort(404)


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update(id):
    #checking post with id provided if it exists and return its index
    post_index:int = fetch_post(id)
    #if check has index returned delete the post in database
    if post_index != None:
        #get data sent by user
        data_entered = request.get_json()
        #extract keys from data sent
        keys_to_replace = data_entered.keys()
        #iterate on keys and replace data if any sent
        for key in keys_to_replace:
            POSTS[post_index][key] = data_entered[key]
        return jsonify({'message': 'Post with id {} updated'.format(id)})
        
    else:
        abort(404)

    




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
