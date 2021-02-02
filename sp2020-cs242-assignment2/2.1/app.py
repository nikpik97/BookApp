"""Flask API for Assignment 2.1
"""

import os
import json
import copy
from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import pymongo
from pymongo.collection import ReturnDocument

load_dotenv()
USER_NAME_DB = str(os.getenv("MONGO_DB_USER_NAME"))
PASSWORD_DB = str(os.getenv("MONGO_DB_PASSWORD"))
CLIENT = pymongo.MongoClient("mongodb+srv://" + USER_NAME_DB + ":" + PASSWORD_DB
                             + "@sp2020-cs242-assignment2-xcjvb.mongodb.net/test?retryWrites"
                             + "=true&w=majority")
GOODREADS_DB = CLIENT['GoodReads']
COLLECTION_B = GOODREADS_DB["books"]
COLLECTION_A = GOODREADS_DB["authors"]
APP = Flask(__name__)

@APP.route('/', methods=['GET'])
def get_home():
    """This function generates a homepage
    """
    return render_template('home.html', user='Nikhil')

@APP.route('/api/books', methods=['GET'])
def get_books():
    """This function handles the get request for all books
    """
    response = jsonify('malformed request')
    response.status_code = 400
    if len(request.args) == 1 or len(request.args) == 0:
        db_result_incomplete = COLLECTION_B.find({}, {"_id":0})
        db_result = {}
        for i in db_result_incomplete:
            db_result[i['book_title']] = i
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to get'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/authors', methods=['GET'])
def get_authors():
    """This function handles a get request for all authors
    """
    response = jsonify('malformed request')
    response.status_code = 400
    if len(request.args) == 1 or len(request.args) == 0:
        db_result_incomplete = COLLECTION_A.find({}, {"_id":0})
        db_result = {}
        for i in db_result_incomplete:
            db_result[i['author_name']] = i
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to get'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/book', methods=['GET'])
def get_book():
    """This function handles a get request for asingle book.
    """
    response = jsonify('malformed request')
    response.status_code = 400
    # for attribute, value in request.args.items():
    #     print(attribute, value, sep='   ')
    if len(request.args) == 1 or len(request.args) == 2:
        if 'title' in request.args.keys():
            title_query = request.args.get('title')
            db_result = COLLECTION_B.find_one({'book_title': {"$regex": title_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to get'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'author' in request.args.keys():
            author_query = request.args.get('author')
            db_result = COLLECTION_B.find_one({'all_authors.name':  {"$regex": author_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to get'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'related_book' in request.args.keys():
            book_query = request.args.get('related_book')
            db_result = COLLECTION_B.find_one({'similar_books.name':  {"$regex": book_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to get'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            db_result = 'invalid parameter'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/author', methods=['GET'])
def get_author():
    """This function handles the get request for a single author
    """
    response = jsonify('malformed request')
    response.status_code = 400
    for attribute, value in request.args.items():
        print(attribute, value, sep='   ')
    if len(request.args) == 1 or len(request.args) == 2:
        if 'name' in request.args.keys():
            author_query = request.args.get('name')
            db_result = COLLECTION_A.find_one({'author_name': {"$regex": author_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to get'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'book_title' in request.args.keys():
            book_query = request.args.get('book_title')
            db_result = COLLECTION_A.find_one({'books_by_author.name': {"$regex": book_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to get'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            db_result = 'invalid parameter'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/book', methods=['PUT'])
def update_book():
    """This function handles a put request on a single book
    """
    response = jsonify('Unsupported Media Type HTTP status code')
    response.status_code = 415
    for attribute, value in request.args.items():
        print(attribute, value, sep='   ')
    json_input = request.json
    i = list(json_input.keys())[0]
    if len(request.args) == 1 or len(request.args) == 2:
        if 'title' in request.args.keys():
            title_query = request.args.get('title')
            db_result = COLLECTION_B.find_one_and_update({'book_title': {"$regex": title_query}}, {"$set": {i: json_input[i]}}, projection={"_id":0}, return_document=ReturnDocument.AFTER)
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to update'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'author' in request.args.keys():
            author_query = request.args.get('author')
            db_result = COLLECTION_B.find_one_and_update({'all_authors.name':  {"$regex": author_query}}, {"$set": {i: json_input[i]}}, projection={"_id":0}, return_document=ReturnDocument.AFTER)
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to update'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'related_book' in request.args.keys():
            book_query = request.args.get('related_book')
            db_result = COLLECTION_B.find_one_and_update({'similar_books.name':  {"$regex": book_query}}, {"$set": {i: json_input[i]}}, projection={"_id":0}, return_document=ReturnDocument.AFTER)
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to update'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            response = jsonify('invalid parameter')
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/author', methods=['PUT'])
def update_author():
    """This function handle a put request for a single author
    """
    response = jsonify('malformed request')
    response.status_code = 400
    for attribute, value in request.args.items():
        print(attribute, value, sep='   ')
    json_input = request.json
    i = list(json_input.keys())[0]
    if len(request.args) == 1 or len(request.args) == 2:
        if 'name' in request.args.keys():
            author_query = request.args.get('name')
            db_result = COLLECTION_A.find_one_and_update({'author_name': {"$regex": author_query}}, {"$set": {i: json_input[i]}}, projection={"_id":0}, return_document=ReturnDocument.AFTER)
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to update'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'book_title' in request.args.keys():
            book_query = request.args.get('book_title')
            db_result = COLLECTION_A.find_one_and_update({'books_by_author.name': {"$regex": book_query}}, {"$set": {i: json_input[i]}}, projection={"_id":0}, return_document=ReturnDocument.AFTER)
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to update'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            db_result = 'invalid parameter'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/book', methods=['POST'])
def post_book():
    """This function handles a post request for a single book
    """
    response = jsonify('Unsupported Media Type HTTP status code')
    response.status_code = 415
    json_input = request.json
    i = list(json_input.keys())[0]
    if 'book_url' in json_input[i].keys():
        document = COLLECTION_B.find({'book_url': json_input[i]['book_url']}, {}).count()
        if document == 0:
            data_input = copy.deepcopy(json_input)
            COLLECTION_B.insert_one(copy.deepcopy(json_input[i]))
            response = jsonify(json_input)
            response.status_code = 201
        else:
            response = jsonify('Data exists in the db')
            response.status_code = 417
            data_input = 'Data exists in the db'
    else:
        return response
    if 'format' in request.args.keys() and request.args.get('format') == 'html' and data_input:
        return render_template('report.html', data=json.dumps(data_input, indent=4))
    return response

@APP.route('/api/author', methods=['POST'])
def post_author():
    """This function handles a post request for a single author
    """
    response = jsonify('Unsupported Media Type HTTP status code')
    response.status_code = 415
    json_input = request.json
    i = list(json_input.keys())[0]
    if 'author_url' in json_input[i].keys():
        document = COLLECTION_A.find({'author_url': json_input[i]['author_url']}, {}).count()
        if document == 0:
            data_input = copy.deepcopy(json_input)
            COLLECTION_A.insert_one(copy.deepcopy(json_input[i]))
            response = jsonify(json_input[i])
            response.status_code = 201
        else:
            response = jsonify('Data exists in the db')
            response.status_code = 417
            data_input = 'Data exists in the db'
    else:
        return response
    if 'format' in request.args.keys() and request.args.get('format') == 'html' and data_input:
        return render_template('report.html', data=json.dumps(data_input, indent=4))
    return response

@APP.route('/api/books', methods=['POST'])
def post_books():
    """This function handles a post request for multiple books
    """
    #TODO: test
    response = jsonify('Unsupported Media Type HTTP status code')
    response.status_code = 415
    json_input = request.json
    json_r = {}
    for i in json_input.keys():
        if 'book_url' in json_input[i].keys():
            document = COLLECTION_B.find({'book_url': json_input[i]['book_url']}, {}).count()
            if document == 0:
                COLLECTION_B.insert_one(copy.deepcopy(json_input[i]))
                json_r[i] = json_input[i]
            else:
                json_r[i] = 'Data already exists in db'
    if json_r:
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and json_r:
            return render_template('report.html', data=json.dumps(json_r, indent=4))
        response = jsonify(json_r)
        response.status_code = 201
    return response

@APP.route('/api/authors', methods=['POST'])
def post_authors():
    """This function handles a post request for multiple authors
    """
    #TODO: test
    response = jsonify('Unsupported Media Type HTTP status code')
    response.status_code = 415
    json_input = request.json
    json_r = {}
    for i in json_input.keys():
        if 'author_url' in json_input[i].keys():
            document = COLLECTION_A.find({'author_url': json_input[i]['author_url']}, {}).count()
            if document == 0:
                COLLECTION_B.insert_one(copy.deepcopy(json_input[i]))
                json_r[i] = json_input[i]
            else:
                json_r[i] = 'Data already exists in db'
    if json_r:
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and json_r:
            return render_template('report.html', data=json.dumps(json_r, indent=4))
        response = jsonify(json_r)
        response.status_code = 201
    return response

@APP.route('/api/book', methods=['DELETE'])
def delete_book():
    """This function handles a delete request for single book
    """
    response = jsonify('malformed requests')
    response.status_code = 400
    for attribute, value in request.args.items():
        print(attribute, value, sep='   ')
    print(len(request.args))
    if len(request.args) == 1 or len(request.args) == 2:
        if 'title' in request.args.keys():
            title_query = request.args.get('title')
            db_result = COLLECTION_B.find_one_and_delete({'book_title': {"$regex": title_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to delete'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'author' in request.args.keys():
            author_query = request.args.get('author')
            db_result = COLLECTION_B.find_one_and_delete({'all_authors.name':  {"$regex": author_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to delete'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'related_book' in request.args.keys():
            book_query = request.args.get('related_book')
            db_result = COLLECTION_B.find_one_and_delete({'similar_books.name':  {"$regex": book_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['book_title']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to delete'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            db_result = 'invalid parameter'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/api/author', methods=['DELETE'])
def delete_author():
    """This function handles a delete request for single author
    """
    response = jsonify('malformed request')
    response.status_code = 400
    for attribute, value in request.args.items():
        print(attribute, value, sep='   ')
    print(len(request.args))
    if len(request.args) == 1 or len(request.args) == 2:
        if 'name' in request.args.keys():
            author_query = request.args.get('name')
            db_result = COLLECTION_A.find_one_and_delete({'author_name': {"$regex": author_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to delete'
                response = jsonify(db_result)
                response.status_code = 200
        elif 'book_title' in request.args.keys():
            book_query = request.args.get('book_title')
            db_result = COLLECTION_A.find_one_and_delete({'books_by_author.name': {"$regex": book_query}}, {"_id":0})
            if db_result:
                db_result = {db_result['author_name']: db_result}
                response = jsonify(db_result)
                response.status_code = 200
            else:
                db_result = 'unable to delete'
                response = jsonify(db_result)
                response.status_code = 200
        else:
            db_result = 'invalid parameter'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result and response:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/query/most-book-authors', methods=['GET'])
def querry_author_with_most_books():
    """This function handles a get request for a querry.
       It gets the author with the most books written.
    """
    response = jsonify('malformed request')
    response.status_code = 400
    # for attribute, value in request.args.items():
    #     print(attribute, value, sep='   ')
    if len(request.args) == 1 or len(request.args) == 0:
        pipeline = [
                        {"$project":
                            {
                                "author_name": 1,
                                "author_url": 1,
                                "book_total": {"$size": {"$ifNull": ["$books_by_author", []]}}
                            }
                        },
                        {"$sort": {"book_total":-1}},
                        {"$limit": 1},
                        {"$project":
                            {
                                "_id": 0,
                                "author_name": 1,
                                "author_url": 1,
                                "book_total": 1
                            }
                        }
                    ]
        db_result_intermediate = list(COLLECTION_A.aggregate(pipeline))[0]
        db_result_end = COLLECTION_A.find_one({"author_url": db_result_intermediate["author_url"]}, {"_id":0})
        db_result = [db_result_intermediate, db_result_end]
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to querry'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/query/most-similar-books', methods=['GET'])
def querry_book_with_most_similar_books():
    """This function handles a get request for a querry.
       It gets the book with the most similar books.
    """
    response = jsonify('malformed request')
    response.status_code = 400
    if len(request.args) == 1 or len(request.args) == 0:
        pipeline = [
                        {"$project":
                            {
                                "book_title": 1,
                                "book_url": 1,
                                "book_total":  {"$size": {"$ifNull": ["$similar_books", []]}}
                            }
                        },
                        {"$sort": {"book_total":-1}},
                        {"$limit": 1},
                        {"$project":
                            {
                                "_id": 0,
                                "book_title": 1,
                                "book_url": 1,
                                 "book_total": 1
                            }
                        }
                    ]
        db_result_intermediate = list(COLLECTION_B.aggregate(pipeline))[0]
        db_result_end = COLLECTION_B.find_one({"book_url": db_result_intermediate["book_url"]}, {"_id":0})
        db_result = [db_result_intermediate, db_result_end]
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to querry'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/vis/rank-authors', methods=['GET'])
def viz_rank_authors():
    """This function handles a get request for a visualization.
       It gets the top 5 highly rated authors.
    """
    response = jsonify('malformed request')
    if len(request.args) == 1 or len(request.args) == 0:
        pipeline = [
                        {"$sort": {"author_rating":-1}},
                        {"$limit": 5},
                        {"$project":
                            {
                                "_id": 0,
                                "author_name": 1,
                                "author_url": 1,
                                "author_rating": 1
                            }
                        }
                    ]
        db_result_intermediate = list(COLLECTION_A.aggregate(pipeline))
        db_querry_urls = []
        for i in db_result_intermediate:
            db_querry_urls.append(i['author_url'])
        db_result_end = COLLECTION_A.find({"author_url": {"$in": db_querry_urls}}, {"_id":0})
        db_result_dict_end = {}
        for i in db_result_end:
            db_result_dict_end[i['author_name']] = i
        db_result = [db_result_intermediate, db_result_dict_end]
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to querry'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response

@APP.route('/vis/rank-books', methods=['GET'])
def viz_rank_books():
    """This function handles a get request for a visualization.
       It gets the top 5 highly rated books.
    """
    response = jsonify('malformed request')
    if len(request.args) == 1 or len(request.args) == 0:
        pipeline = [
                        {"$sort": {"book_rating":-1}},
                        {"$limit": 5},
                        {"$project":
                            {
                                "_id": 0,
                                "book_title": 1,
                                "book_url": 1,
                                "book_rating": 1
                            }
                        }
                    ]
        db_result_intermediate = list(COLLECTION_B.aggregate(pipeline))
        db_querry_urls = []
        for i in db_result_intermediate:
            db_querry_urls.append(i['book_url'])
        db_result_end = COLLECTION_B.find({"book_url": {"$in": db_querry_urls}}, {"_id":0})
        db_result_dict_end = {}
        for i in db_result_end:
            db_result_dict_end[i['book_title']] = i
        db_result = [db_result_intermediate, db_result_dict_end]
        if db_result:
            response = jsonify(db_result)
            response.status_code = 200
        else:
            db_result = 'unable to querry'
            response = jsonify(db_result)
            response.status_code = 200
        if 'format' in request.args.keys() and request.args.get('format') == 'html' and db_result:
            return render_template('report.html', data=json.dumps(db_result, indent=4))
    return response
