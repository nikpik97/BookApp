"""Main Module containing all the functionality for Stage 2.0
"""
import sys
import os
import time
import uuid
import json
import argparse
import copy
from pprint import pprint
from random import randint
from bs4 import BeautifulSoup as bs
import validators as va
import requests
import pymongo
from dotenv import load_dotenv


class GoodReadsScrapper():
    """Class that handles all work of scraping GoodReads
    """

    book_urls_to_scrape = set()
    author_urls_to_scrape = set()
    books_scrapped = dict()
    authors_scrapped = dict()
    num_authors = 50
    num_books = 200
    start_url = 'https://www.goodreads.com/book/show/3735293-clean-code'
    load_dotenv()
    user_name_db = str(os.getenv("MONGO_DB_USER_NAME"))
    password_db = str(os.getenv("MONGO_DB_PASSWORD"))
    client = pymongo.MongoClient("mongodb+srv://"
                                 +user_name_db+":"+password_db
                                 +"@sp2020-cs242-assignment2-xcjvb.mongodb.net/test?retryWrites"
                                 +"=true&w=majority")
    rest_time = 0

    def find_if_book_exists(self, url):
        goordreads_db = self.client['GoodReads']
        collection_B = goordreads_db["books"]
        print("check book: ", url)
        x = collection_B.find_one({'book_url':url},{}) 
        if x != None:
            print('\t book exists')
            return True
        else:
            print('\t book does not exists')
            return False
    
    def find_if_author_exists(self, url):
        goordreads_db = self.client['GoodReads']
        collection_A = goordreads_db["authors"]
        print("check author: ", url)
        x = collection_A.find_one({'author_url': url},{})
        if x != None:
            print('\t author exists')
            return True
        else:
            print('\t author does not exists')
            return False

    def setup_db(self):
        """This function sets up the database with the proper schema.
        """
        goordreads_db = self.client['GoodReads']
        collection_A = goordreads_db["authors"]
        collection_B = goordreads_db["books"]
        collection_A.create_index('book_url', unique=True)
        collection_B.create_index('author_url', unique=True)
        pass

    def push_all_authors_to_db(self, author_dict):
        """This function takes a container of scraped authors and pushes each one to the db
        Arguments:
            author_arr Dictionary -- container of author containers
        """
        i = copy.deepcopy(author_dict)
        for value in i.values():
            self.add_to_db_author(value)

    def push_all_books_to_db(self, book_dict):
        """This function takes a container of scraped books and pushes each one to the db
        Arguments:
            book_dict Dictionary -- container of book containers
        """
        i = copy.deepcopy(book_dict)
        for value in i.values():
            self.add_to_db_book(value)

    def pull_all_authors_from_db(self):
        """This function pulls all of the authors from the db and returns them
           as a container of authors (ie same internal format)
        Returns:
            Dictionary -- container of author containers
        """
        goordreads_db = self.client['GoodReads']
        collection = goordreads_db["authors"]
        cursor = collection.find({})
        complete_dict = dict()
        for document in cursor:
            construct_doc = dict()
            for key, value in document.items():
                if key != '_id':
                    construct_doc[key] = value
            complete_dict[document['author_name']] = construct_doc
        return complete_dict

    def pull_all_books_from_db(self):
        """This function pulls all of the books from the db and returns them
           as a container of books (ie same internal format)
        Returns:
            Dictionary -- container of book containers
        """
        goordreads_db = self.client['GoodReads']
        collection = goordreads_db["books"]
        cursor = collection.find({})
        complete_dict = dict()
        for document in cursor:
            construct_doc = dict()
            for key, value in document.items():
                if key != '_id':
                    construct_doc[key] = value
            complete_dict[document['book_title']] = construct_doc
        return complete_dict

    def add_to_db_author(self, author):
        """This function pushes an author container to the db
        Arguments:
            author Dictionary -- author container
        """
        i = copy.deepcopy(author)
        goordreads_db = self.client['GoodReads']
        # print(self.client.list_database_names())
        authors_collection = goordreads_db['authors']
        print()
        if self.find_if_author_exists(i['author_url']) == False:
            authors_collection.insert_one(i)
        self.find_if_author_exists(i['author_url'])
        print()

    def add_to_db_book(self, book):
        """This function pushes an book container to the db
        Arguments:
            book Dictionary -- book container
        """
        i = copy.deepcopy(book)
        goordreads_db = self.client['GoodReads']
        books_collection = goordreads_db['books']
        print()
        if self.find_if_book_exists(i['book_url']) == False:
            books_collection.insert_one(i)
        self.find_if_book_exists(i['book_url'])
        print()

    def clear_db(self):
        """This function deletes all of the documents from the db
        """
        goordreads_db = self.client['GoodReads']
        goordreads_db.drop_collection('books')
        goordreads_db.drop_collection('authors')

    def print_collection(self, col_name):
        """This function displays all of the documents in a collection within the db
        """
        goordreads_db = self.client['GoodReads']
        collection = goordreads_db[col_name]
        cursor = collection.find({})
        for document in cursor:
            pprint(document)

    def import_from_json_file(self, path_json):
        """This function imports a json file into a corresponding internal format
        Arguments:
            path_json   str -- path the to the json file
        Returns:
            Dictionary      -- container of authors or books
        """
        with open(path_json, 'r') as file:
            return json.load(file)

    def export_to_json_file(self, item, name_of_json):
        """This function takes a container and exports it as a json file
        Arguments:
            item Dictionary         -- container of books or authors
            name_of_json    str    -- name of the outputted json file
        """
        with open(name_of_json, 'w') as file:
            json.dump(item, file, indent=4)

    def import_from_json(self, json_str):
        """This function imports a json string into a corresponding internal fromat
        Arguments:
            json_str    str    -- json string
        Returns:
            Dictionary         -- container of books or authors
        """
        return json.loads(json_str)

    def export_as_json(self, item):
        """This function takes a conatiner of authors or books and converts it to json format
        Arguments:
            item    Dictionary -- conatiner of books or authors
        Returns:
            str                -- json output
        """
        return json.dumps(item, indent=4)

    def request_page(self, url):
        """This function requests a html page that corresponds to the url. 
           It also has a sleep function to ensure that requests are made at non-standard timings.
           (Ie avoid looking like a bot)
        Arguments:
            url                 str -- url of the target web page
        Returns:
            beautifulsoap_object    -- html content within a the beautiful soap parser
        """
        sleep_time = randint(0, 3)
        self.rest_time += sleep_time
        time.sleep(sleep_time)
        return bs(requests.get(url).content, 'html.parser')

    def scrape_related_authors(self, related_authors_link):
        """This function scrapes the "related authors" page for an author
        Arguments:
            related_authors_link str    -- url to the "related authors" page
        Returns:
            list((str,str))             -- container of related authors (name, url)
        """
        soup = self.request_page(related_authors_link)
        related_authors = soup.findAll('a', attrs={'class':'gr-h3 gr-h3--serif gr-h3--noMargin',
                                                   'itemprop':'url'})
        related_authors_list = []
        # print(len(related_authors))
        # print('\n\n\nAuthor Tags:')
        for author in related_authors:
            author_related_url = "https://www.goodreads.com"
            author_related_name = author.find('span').text.strip()
            author_related_url += author.get('href').strip()
            # print(author_related_name, author_related_url, '\n', sep=' | ')
            related_authors_list.append({"name":author_related_name, "URL":author_related_url})
        return related_authors_list

    def scrape_author_books(self, author_books_link):
        """This function scrapes the "author's books" page for an author
        Arguments:
            related_authors_link str    -- url to the author's "distinct works" page
        Returns:
            list((str,str))             -- container of books (name, url)
        """
        soup = self.request_page(author_books_link)
        titles = soup.findAll('a', attrs={'class':'bookTitle', 'itemprop':'url'})
        author_own_books = []
        # print('\n\n\nTitle Tags:')
        for title in titles:
            author_own_book_url = "https://www.goodreads.com"
            author_own_book_name = title.find('span').text.strip()
            author_own_book_url += title.get('href').strip()
            # print(author_own_book_name, author_own_book_url, '\n', sep =' | ')
            author_own_books.append({"name":author_own_book_name, "URL":author_own_book_url})
        return author_own_books

    def scrape_similar_books(self, similar_books_url):
        """This function scrapes the "similar books" page for an book
        Arguments:
            related_authors_link str    -- url to the books's "similar books" page
        Returns:
            list((str,str))             -- container of similar books (name, url)
        """
        soup = self.request_page(similar_books_url)
        titles = soup.findAll('a', attrs={'class':'gr-h3 gr-h3--serif gr-h3--noMargin',
                                          'itemprop':'url'})
        similar_books = []
        # print('\n\n\nTitle Tags:')s
        for title in titles:
            similar_book_url = "https://www.goodreads.com"
            similar_book_name = title.find('span').text.strip()
            similar_book_url += title.get('href').strip()
            # print(similar_book_name, similar_book_url, '\n', sep =' | ')
            similar_books.append({"name": similar_book_name, "URL": similar_book_url})
        return similar_books

    def scrape_author(self, author_url):
        """This function scrapes an author page and outputs the necessary information 
           as described in the assignment 2.0 specification.
        Arguments:
            author_url  str     -- author page url
        Returns:
            Dictionary          -- author conatiner; fields are described in the assignment 2.0 specification
        """
        related_authors_link = ''
        author_books_link = ''
        soup = self.request_page(author_url)
        if soup.find('h1', attrs={'class':'authorName'}):
            author_name = soup.find('h1', attrs={'class':'authorName'}).find('span').text.strip()
        else:
            author_name = ''
        # print(author_name)
        author_id = str(uuid.uuid4())
        author_rating_tag = soup.find('div', attrs={'class':'hreview-aggregate',
                                                    'itemprop':'aggregateRating'})
        if author_rating_tag:
            if author_rating_tag.find('span', attrs={'class': 'average', 'itemprop':'ratingValue'}):
                author_rating = float(author_rating_tag.find('span',
                                                             attrs={'class': 'average',
                                                                    'itemprop':'ratingValue'}
                                                            ).text.strip())
            else:
                author_rating = 0.0
            if author_rating_tag.find('span', attrs={'itemprop':'ratingCount'}):
                author_rating_num = int(author_rating_tag.find('span',
                                                               attrs={'itemprop':'ratingCount'}
                                                              ).get('content').strip())
            else:
                author_rating_num = 0
            if author_rating_tag.find('span', attrs={'itemprop':'reviewCount'}):
                author_review_num = int(author_rating_tag.find('span',
                                                               attrs={'itemprop':'reviewCount'}
                                                              ).get('content').strip())
            else:
                author_review_num = 0
            if author_rating_tag.findAll('a'):
                if len(author_rating_tag.findAll('a')) >= 2:
                    related_authors_link += "https://www.goodreads.com"
                    related_authors_link += author_rating_tag.findAll('a')[1].get('href').strip()
                    related_authors_link += '?page=1&per_page=10000'
                else:
                    related_authors_link = ''
                if len(author_rating_tag.findAll('a')) >= 1:
                    author_books_link += "https://www.goodreads.com"
                    author_books_link += author_rating_tag.findAll('a')[0].get('href').strip()
                    author_books_link += '?page=1&per_page=10000'
                else:
                    related_authors_link = ''
        if soup.find('a', attrs={'title':author_name, "rel": "nofollow"}):
            if soup.find('a', attrs={'title':author_name, "rel": "nofollow"}).find('img'):
                author_image_link = soup.find('a', attrs={'title':author_name,
                                                          'rel': "nofollow"
                                                         }).find('img').get('src')
            else:
                author_image_link = ''
        else:
            author_image_link = ''
        if va.url(author_books_link):
            books_by_author = self.scrape_author_books(author_books_link)
        else:
            books_by_author = []
        if va.url(related_authors_link):
            related_authors = self.scrape_related_authors(related_authors_link)
        else:
            related_authors = []
        # print(author_name, author_url, author_id, author_rating, author_rating_num,
        #       author_review_num, author_image_link, related_authors, books_by_author,
        #       sep='\n\n\n')
        return {"author_name": author_name, "author_url": author_url, "author_id": author_id,
                "author_rating": author_rating, "author_rating_num": author_rating_num,
                "author_review_num": author_review_num, "author_image_link": author_image_link,
                "author_books_link": author_books_link, "books_by_author": books_by_author,
                "related_authors_link": related_authors_link, "related_authors": related_authors}

    def scrape_book(self, book_url):
        """This function scrapes an book page and outputs the necessary information 
           as described in the assignment 2.0 specification.
        Arguments:
            book_url  str       -- book page url
        Returns:
            Dictionary          -- book conatiner; fields are described in the assignment 2.0 specification
        """
        # print('\n\n\n')
        soup = self.request_page(book_url)
        book_title = ''
        book_image_link = ''
        if soup.find('h1', attrs={'id':"bookTitle"}):
            book_title = soup.find('h1', attrs={'id':"bookTitle"}).text.strip()
        if soup.find('a', attrs={"itemprop":"image", "rel": "nofollow"}):
            if soup.find('a', attrs={"itemprop":"image", "rel": "nofollow"}).find('img'):
                book_image_link = soup.find('a', attrs={"itemprop":"image",
                                                        "rel": "nofollow"
                                                       }).find('img').get('src')
        book_id = str(uuid.uuid4())
        if soup.find('span', attrs={'itemprop': 'isbn'}):
            book_isbn = soup.find('span', attrs={'itemprop': 'isbn'}).text.strip()
        else:
            book_isbn = ''
        author_info_tags = soup.findAll('a', attrs={'class':'authorName', 'itemprop': 'url'})
        all_authors = []
        for author in author_info_tags:
            if author:
                url = author.get('href')
                if author.find('span', attrs={'itemprop': 'name'}):
                    name = author.find('span', attrs={'itemprop': 'name'}).text.strip()
                else:
                    name = ''
                all_authors.append({'name': name, 'URL':url})
        if len(author_info_tags) >= 1 and author_info_tags[0]:
            author_url = author_info_tags[0].get('href')
            author_name = author_info_tags[0].find('span',
                                                   attrs={'itemprop': 'name'}
                                                  ).text.strip()
        book_rate_tag = soup.findAll('div', attrs={'id':'bookMeta', 'itemprop':'aggregateRating'})
        if len(book_rate_tag) >= 1 and book_rate_tag[0]:
            book_rating = float(book_rate_tag[0].find('span',
                                                      attrs={'itemprop':'ratingValue'}
                                                     ).text.strip())
            book_rating_num = int(book_rate_tag[0].find('meta',
                                                        attrs={'itemprop':'ratingCount'}
                                                       ).get('content').strip())
            book_review_num = int(book_rate_tag[0].find('meta',
                                                        attrs={'itemprop':'reviewCount'}
                                                       ).get('content').strip())
        # print(book_title)
        similar_books_link = ''
        if soup.find('a', attrs={'class':'actionLink right seeMoreLink'}):
            similar_books_link = soup.find('a',
                                           attrs={'class':'actionLink right seeMoreLink'}
                                          ).get('href')
            similar_books_link += '?page=1&per_page=10000'
        similar_books = []
        if va.url(similar_books_link):
            similar_books = self.scrape_similar_books(similar_books_link)
        # print(book_url, book_title, book_id, book_isbn, author_url, author_name,
        #       book_rating, book_rating_num, book_review_num, book_image_link, similar_books,
        #       sep='\n\n\n')
        return {"book_url":book_url, 'book_title': book_title, "book_image_link": book_image_link,
                "book_id":book_id, "book_isbn": book_isbn, "author_url": author_url,
                "author_name": author_name, 'all_authors': all_authors, "book_rating": book_rating,
                "book_rating_num": book_rating_num, "book_review_num": book_review_num,
                "similar_books_link": similar_books_link, "similar_books": similar_books}

    def scraper(self):
        """This function performs the main scraping duties by:
                parsing the cmd line
                calling the scrapers on the intial book link
                scraping the similar books, author's books, and related authors
                uploads authors and books to the db while parsing
        """
        # TODO: replace with argparse
        if len(sys.argv) >= 2:
            if va.url(sys.argv[1]):
                if "goodreads.com/book/show/" in sys.argv[1]:
                    self.start_url = sys.argv[1]
                else:
                    self.start_url = 'https://www.goodreads.com/book/show/3735293-clean-code'
                    print('Can only use a goodreads-book url as a starting point')
            else:
                self.start_url = 'https://www.goodreads.com/book/show/3735293-clean-code'
                print('Invalid url')
        else:
            self.start_url = 'https://www.goodreads.com/book/show/3735293-clean-code'
        if len(sys.argv) >= 3:
            if sys.argv[2].isnumeric() and int(sys.argv[2]) >= 0 and int(sys.argv[2]) <= 2000:
                self.num_books = int(sys.argv[2])
            else:
                print('You must enter a number between 0 and 2000')
                self.num_books = 5
        else:
            self.num_books = 5
        if len(sys.argv) >= 4:
            if sys.argv[3].isnumeric() and int(sys.argv[3]) >= 0 and int(sys.argv[3]) <= 200:
                self.num_authors = int(sys.argv[3])
            else:
                print('You must enter a number between 0 and 2000')
                self.num_authors = 5
        else:
            self.num_authors = 5
        start_time = time.time()
        # parse initial url and add authors and books to the *_to_scrape dicts
        result_book = self.scrape_book(self.start_url)
        result_author = self.scrape_author(result_book['author_url'])
        for book in result_book['similar_books']:
            self.book_urls_to_scrape.add(book['URL'])
        for book in result_author['books_by_author']:
            self.book_urls_to_scrape.add(book['URL'])
        for author in result_author['related_authors']:
            self.author_urls_to_scrape.add(author['URL'])
        self.books_scrapped[result_book['book_title']] = result_book
        self.authors_scrapped[result_author['author_name']] = result_author
        # print("add to db: ", result_author['author_url'])
        # self.add_to_db_author(result_author)
        # print("add to db: ", result_book['book_url'])
        # self.add_to_db_book(result_book)
        while len(self.books_scrapped) < self.num_books and len(self.author_urls_to_scrape) > 0:
            book_url = self.book_urls_to_scrape.pop()
            if va.url(book_url):
                # print("\tbook_url: ", book_url)
                scraped_book_result = self.scrape_book(book_url)
                # self.add_to_db_book(copy.deepcopy(scraped_book_result))
                self.author_urls_to_scrape.add(scraped_book_result['author_url'])
                for author in scraped_book_result['all_authors']:
                    self.author_urls_to_scrape.add(author['URL'])
                for book in scraped_book_result['similar_books']:
                    self.book_urls_to_scrape.add(book['URL'])
                self.books_scrapped[scraped_book_result['book_title']] = scraped_book_result
                # print("add to db: ", scraped_book_result['book_url'])
                # self.add_to_db_book(scraped_book_result)
        while len(self.authors_scrapped) < self.num_authors and len(self.author_urls_to_scrape) > 0:
            author_url = self.author_urls_to_scrape.pop()
            if va.url(author_url):
                # print("\tauthor_url: ", author_url)
                scraped_author_result = self.scrape_author(author_url)
                for author in scraped_author_result['related_authors']:
                    self.author_urls_to_scrape.add(author['URL'])
                for book in scraped_author_result['books_by_author']:
                    self.book_urls_to_scrape.add(book['URL'])
                self.authors_scrapped[scraped_author_result['author_name']] = scraped_author_result
                # self.add_to_db_author(scraped_author_result)
                # print("add to db: ", scraped_author_result['author_url'])
        end_time = time.time()
        print((end_time - start_time) - self.rest_time)
        
        self.push_all_books_to_db(self.books_scrapped)
        self.push_all_authors_to_db(self.authors_scrapped)
        # print(len(self.books_scrapped))
        # print(len(self.authors_scrapped))
        # print('\n\n\n')

    def test(self):
        """ 6 basic test cases that check db and json functionality
        """
        # self.print_collection('authors')
        # self.print_collection('books')
        temp2_a = self.pull_all_authors_from_db()
        temp2_b = self.pull_all_books_from_db()
        print(self.authors_scrapped == temp2_a)
        print(self.books_scrapped == temp2_b)
        print('\n\n\n')
        self.clear_db()
        self.export_to_json_file(self.books_scrapped, "books.json")
        self.export_to_json_file(self.authors_scrapped, "authors.json")
        temp_b = self.import_from_json_file("books.json")
        temp_a = self.import_from_json_file("authors.json")
        print(self.authors_scrapped == temp_a)
        print(self.books_scrapped == temp_b)
        print('\n\n\n')
        # self.clear_db()
        # self.push_all_books_to_db(temp_b)
        # self.push_all_authors_to_db(temp_a)
        # temp1_a = self.pull_all_authors_from_db()
        # temp1_b = self.pull_all_books_from_db()
        # print(temp1_a == temp_a)
        # print(temp1_b == temp_b)

if __name__ == "__main__":
    i = GoodReadsScrapper()
    i.export_to_json_file(i.pull_all_books_from_db(), "books.json")
    i.export_to_json_file(i.pull_all_authors_from_db(), "authors.json")
    # i.setup_db()
    # i.scraper()
    # i.test()
