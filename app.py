from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np

popular_df = pickle.load(open('model/popular.pkl', 'rb'))
books = pickle.load(open('model/books.pkl', 'rb'))
pt = pickle.load(open('model/pt.pkl', 'rb'))
similarity_scores = pickle.load(open('model/similarity_scores.pkl', 'rb'))

app = Flask(__name__)

@app.route('/')
def index():
    books = []

    for i in range(len(popular_df)):
        books.append({
            'title': popular_df['Book-Title'][i],
            'author': popular_df['Book-Author'][i],
            'image': popular_df['Image-URL-M'][i],
            'votes': int(popular_df['num-ratings'][i]),
            'rating': round(popular_df['avg-rating'][i], 2)
        })

    return render_template(
        'index.html',
        books=books
    )

@app.route('/recommend')
def recommend_ui():
    user_input = request.args.get('book')

    if not user_input:
        return render_template('recommend.html')

    matches = np.where(pt.index == user_input)[0]

    if len(matches) == 0:
        return render_template('recommend.html',
                               error='Book not found. Please enter the exact book title.',
                               user_input=user_input)

    index = matches[0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:7]

    data = []
    for i in similar_items:
        item = []

        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Title'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Book-Author'].to_list())
        item.extend(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].to_list())

        data.append(item)

    return render_template('recommend.html', data=data, user_input=user_input)

@app.route('/recommend_books',methods=['POST'])
def recommend_books():

    user_input = request.form.get('user_input').strip()

    return redirect(url_for('recommend_ui', book=user_input))

if __name__ == '__main__':
    app.run(debug=True)