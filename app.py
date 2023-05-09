from flask import Flask, render_template,jsonify,request,abort
import os
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    data = {
        'title': 'My Title',
        'description': 'This is a description'
    }
    return jsonify(data)


@app.route('/editor', methods=['GET', 'POST'])
def editor():
    if request.method == 'POST':
        # Get the post data from the request
        post_data = request.form['post_data']

        if post_data:

            # Check if the "post_latest" directory exists
            if os.path.exists('./static/posts/post'):
                # Rename the directory with the format "post_latest_<date>_<number>"
                post_date = datetime.date.today().strftime('%Y-%m-%d')
                new_post_number = 1
                existing_posts = [d for d in os.listdir('./static/posts/') if d.startswith('post_')]
                print("posts---> ",existing_posts)
                if existing_posts:
                    latest_post = max(existing_posts, key=lambda x: int(x.split('_')[2]))
                    print("latest_post---> ",latest_post)
                    post_parts = latest_post.split('_')[1:]
                    if len(post_parts) > 1:
                        post_date, post_number = post_parts
                        new_post_number = int(post_number) + 1
                    else:
                        post_date = datetime.date.today().strftime('%Y-%m-%d')
                        new_post_number = 1
                latest_post_directory = f"{post_date}_{new_post_number}"
                print("new directory---> ",latest_post_directory)
                os.rename('./static/posts/post', f"./static/posts/post_{latest_post_directory}")

            # Create the "post_latest" directory
            os.mkdir('./static/posts/post')

            # Write the new post data to a file called "post.txt"
            with open('./static/posts/post/post.txt', 'w') as f:
                f.write(post_data)

            # Check if there are any images in the request
            if 'image' in request.files:
                # Get the number of existing images
                existing_images = [f for f in os.listdir('./static/posts/post') if f.startswith('img')]
                img_number = len(existing_images) + 1

                image = request.files['image']
                # Save the image with the extension png and name img_<number>.png
                image.save(f'./static/posts/post/img_{img_number}.png')

            return " "
        else:
            abort(403)
    else:
        return render_template('editor.html')