from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from fuzzywuzzy import fuzz
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import json


app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=['5 per minute', '1 per second']
)


def update_post_file(posts):
    with open('posts.json', 'w') as file:
        json.dump(posts, file, indent=4)

#user registration
#user login

#versoning 


@app.route('/api/posts', methods=['GET'])
@limiter.limit('5 per minute')
def get_posts():
    #pagination
    page:int = int(request.args.get('page', default=1))
    limit:int = int(request.args.get('limit', default=5))
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_posts = POSTS[start_index:end_index]
    #checking if user has posted a query for sorting out date
    sort:str = request.args.get('sort')
    direction:str = request.args.get('direction')
    #setting sort and direction parameters
    sorting_criteria: list = ['title', 'content', 'author', 'date']
    direction_criteria: list =['asc', 'desc']
    direction_order:bool = False
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
    #if sorting out requested by date
    if sort == 'date':
        for post in paginated_posts:
            #convert date strings into real dates
            date  = datetime.strptime(post['date'], '%Y-%m-%d')
            post['date'] = date
    
    
    if sort in sorting_criteria and direction_order != False:
        return jsonify(sorted(paginated_posts, key=lambda x: x[sort], reverse=True))
    #if no sorting request given and direction not invalid return orignal posts
    elif sort == None:
        return jsonify(paginated_posts)
    elif sort in sorting_criteria and direction_order == False:
        return jsonify(sorted(paginated_posts, key=lambda x: x[sort], reverse=False))
    else:
         abort(400)


@app.errorhandler(400)
def bad_request_error(error):
    
    return jsonify({'error': 'BAD REQUEST'}), 400

def check_keys_in_dict(keys, dictinoary):
    
    return all(key in dictinoary for key in keys)

def make_dictionary(data, last_id):
   
    return {
    "id": last_id + 1,
    "title": data['title'],
    "content": data['content'],
    "author": data['author'],
    "date": datetime.now().strftime('%Y-%m-%d')
}


@app.route('/api/posts', methods=['POST'], )
def add(): 
    #get post from url
    keys_list = ['title', 'content', 'author']
    post:dict = request.get_json()
    #checking if user has entered all the details
    if check_keys_in_dict(keys_list, post):
       #get all ids from posts in database
       all_ids:list = [post['id'] for post in POSTS ]
        #checking if posts in database is not an empty list
       if len(all_ids) != 0:
           #assing max id with increment to new post
           POSTS.append(make_dictionary(post, POSTS[-1]['id'] ))
        #if post list is empty
       else:
           POSTS.append(make_dictionary(post, 0))
       #return 201 response for post succesfully created
       update_post_file(POSTS)
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
        update_post_file(POSTS)
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
        
        update_post_file(POSTS)
        return jsonify({'message': 'Post with id {} updated'.format(id)})
        
    else:
        abort(404)


@app.route('/api/posts/search')
def search():
    #get the params sent for search, if no params use defaults
    all_matched = []
    for post in POSTS:
            for key, value in request.args.items():
                if fuzz.partial_token_set_ratio(value.lower(),\
                                                 post[key].lower())>=90:
                    all_matched.append(post)
    
    return jsonify(all_matched)


class InvalidJsonData(Exception):
    pass

def load_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        raise InvalidJsonData(f'Error Decoding JSON File')

try:
    POSTS = load_json_file('posts.json')
except InvalidJsonData as e:
    print(e)

def main():
        app.run(host="0.0.0.0", port=5002, debug=True)
    



if __name__ == '__main__':
    main()

