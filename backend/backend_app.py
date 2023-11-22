from flask import Flask, jsonify, redirect, request, url_for, abort
from flask_cors import CORS
from fuzzywuzzy import fuzz, process

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    #checking if user has posted a query
    sort = request.args.get('sort')
    direction = request.args.get('direction')
    #setting sort and direction parameters
    sorting_criteria: list = ['title', 'content']
    direction_criteria: list =['asc', 'desc']
    direction_order = ''
    #if direction provided in request
    if direction in direction_criteria:
        if direction == 'asc':                    
            direction_order = False
        elif direction == 'desc':
            direction_order = True
    #if direction not provided        
    elif direction == None:
        pass
    #if direction provided doesnot match criteria
    else:
        abort(400)
    #sorting out posts 
    if sort in sorting_criteria and direction_order != False:
        return jsonify(sorted(POSTS, key=lambda x: x[sort], reverse=True))
    #if no sorting request given and direction not invalid return orignal posts
    elif sort == None:
        return jsonify(POSTS)
    elif sort in sorting_criteria and direction_order == False:
        return jsonify(sorted(POSTS, key=lambda x: x[sort], reverse=False))
    else:
         abort(400)

@app.errorhandler(400)
def bad_request_error(error):
    
    return jsonify({'error': 'BAD REQUEST'}), 400

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


@app.route('/api/posts/search')
def search():
    #get the params sent for search, if no params use defaults
    title = request.args.get('title', default='none').lower()
    content = request.args.get('content', default='none').lower()
    all_matched = []
    for post in POSTS:
        #if ratio of compare is more than 90 then add that post
        if fuzz.partial_token_sort_ratio(title, post['title'].lower()) >= 90\
              or fuzz.partial_token_sort_ratio\
                (content, post['content'].lower()) >= 90:
            #append the matched posts with ratio 90 or above 
            all_matched.append(post)
    
    return jsonify(all_matched)
   



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
