from flask import Flask, render_template,jsonify,request,abort
import os
import shutil
import datetime
from flask_cors import CORS
from yoyo import read_migrations, get_backend
from dbops import DB

DATABASE_URI = os.getenv('DATABASE_URI')

app = Flask(__name__)
CORS(app)

# Set up the database backend
backend = get_backend(DATABASE_URI)
# Load migrations from a specific directory
migrations = read_migrations('./migrations')
# Iterate over the migrations
for migration in migrations:
    # Access information about each migration
    print('migration_id' ,migration.id)
    #print('migration_name' ,migration.name)
    print('migration_src' , migration.source)
    print('migration_path' , migration.path)
    #print('migration_ts' ,migration.timestamp)
    print('migration_hash' ,migration.hash)

migrations_to_apply = backend.to_apply(migrations)
for migration in migrations_to_apply:
    # Access information about each migration
    print('migration_id' ,migration.id)
    #print('migration_name' ,migration.name)
    print('migration_src' , migration.source)
    print('migration_path' , migration.path)
    #print('migration_ts' ,migration.timestamp)
    print('migration_hash' ,migration.hash)
    # Apply pending migrations
    with backend.lock():
        backend.apply_one(migration)

def add_to_db(db,path,title,posttype):
    try:
        if (db.connect()):
            ret=db.add_to_postmaster(path,title,posttype)
            db.con_close()
            return ret
    except Exception as e:
        print ('DB_EXCEPTION_QUERY ', e)
    return False

def delete_folder(folder_path):
    # Verify if the folder exists
    if os.path.exists(folder_path):
        # Iterate over the folder contents
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for file in files:
                # Delete files
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir in dirs:
                # Delete subdirectories
                dir_path = os.path.join(root, dir)
                os.rmdir(dir_path)
        
        # Delete the main folder
        shutil.rmtree(folder_path)
        print(f"Folder '{folder_path}' and its contents deleted successfully.")
        raise Exception("DB Erro __ Post Deleted")
    else:
        print(f"Folder '{folder_path}' does not exist.")

def save_file_bak(post_data,title_data,posttype='post'):
    db=DB()
    #check if path is present if not create it
    if not os.path.exists('./static/posts/post'):
        os.mkdir('./static/posts/post')
    
    with open('./static/posts/post/post.txt', 'w') as f:
        f.write(post_data)
    
    #print("savefile--->image= ",list(enumerate(request.files.getlist('image'))))
    for i, file in enumerate(request.files.getlist('image')):
        filename = f"./static/posts/post/img{i+1}.png"
        file.save(filename)
    # Rename the directory with the format "post_latest_<date>_<number>"
    post_date = datetime.date.today().strftime('%Y-%m-%d')
    new_post_number = 1
    existing_posts = [d for d in os.listdir('./static/posts/') if d.startswith('post_')]
    #print("posts---> ",existing_posts)
    if existing_posts:
        latest_post = max(existing_posts, key=lambda x: int(x.split('_')[2]))
        #print("latest_post---> ",latest_post)
        post_parts = latest_post.split('_')[1:]
        if len(post_parts) > 1:
            post_date, post_number = post_parts
            new_post_number = int(post_number) + 1
        else:
            post_date = datetime.date.today().strftime('%Y-%m-%d')
            new_post_number = 1
    latest_post_directory = f"{post_date}_{new_post_number}"
    #print("new directory---> ",latest_post_directory)
    new_path=f"post_{latest_post_directory}"
    try:
        if(add_to_db(db,new_path,title_data,posttype)):
            os.rename("./static/posts/post", f"./static/posts/{new_path}")
        else:
            delete_folder('./static/posts/post')
    except:
        delete_folder('./static/posts/post')

#@deprecated    
def save_file(path,post_data,title_data, overwrite=False):
    db=DB()
    if not overwrite:
        if os.path.exists(f"./static/posts/{path}"):
            # Rename the directory with the format "post_latest_<date>_<number>"
            post_date = datetime.date.today().strftime('%Y-%m-%d')
            new_post_number = 1
            existing_posts = [d for d in os.listdir('./static/posts/') if d.startswith(f"{path}_")]
            #print("posts---> ",existing_posts)
            if existing_posts:
                latest_post = max(existing_posts, key=lambda x: int(x.split('_')[2]))
                #print("latest_post---> ",latest_post)
                post_parts = latest_post.split('_')[1:]
                if len(post_parts) > 1:
                    post_date, post_number = post_parts
                    new_post_number = int(post_number) + 1
                else:
                    post_date = datetime.date.today().strftime('%Y-%m-%d')
                    new_post_number = 1
            latest_post_directory = f"{post_date}_{new_post_number}"
            #print("new directory---> ",latest_post_directory)
            new_path=f"{path}_{latest_post_directory}"
            if(update_db(db, path,new_path)):
                os.rename(f"./static/posts/{path}", f"./static/posts/{new_path}")
          
        if (add_to_db(db,path,title_data,type)):
            # Create the "post_latest" directory
            os.mkdir(f"./static/posts/{path}")

            
            # Write the new post data to a file called "post.txt"
            with open(f"./static/posts/{path}/post.txt", 'w') as f:
                f.write(post_data)
            
            '''with open(f"./static/posts/{path}/title.txt", 'w') as f:
                f.write(title_data)

            with open(f"./static/posts/{path}/date.txt", 'w') as f:
                f.write(datetime.date.today().strftime('%Y-%m-%d'))'''
        
            # Save the images to files
            print("savefile--->image= ",list(enumerate(request.files.getlist('image'))))
            for i, file in enumerate(request.files.getlist('image')):
                filename = f"./static/posts/{path}/img{i+1}.png"
                file.save(filename)
            return True
        return False
    '''else:
        if not os.path.exists(f"./static/posts/{path}"): #mainpost
            # Create the "post_latest" directory
            os.mkdir(f"./static/posts/{path}")

        # Write the new post data to a file called "post.txt"
        with open(f"./static/posts/{path}/post.txt", 'w') as f:
            f.write(post_data)
        
        # add title to the DB with new date and title
        add_to_db(db,path,title_data)
        with open(f"./static/posts/{path}/title.txt", 'w') as f:
            f.write(title_data)
        
        with open(f"./static/posts/{path}/date.txt", 'w') as f:
            f.write(datetime.date.today().strftime('%Y-%m-%d'))
        
        #add_to_db(db,path,title_data)
        
        # Save the images to files
        for i, file in enumerate(request.files.getlist('image')):
            filename = f"./static/posts/{path}/img{i+1}.png"
            file.save(filename)
        return True'''
    return False


def readfile(path,filename,trimmed=False):
    post_file = os.path.join(path,filename)
        #print("2",post_name)
    if os.path.isfile(post_file):
        with open(post_file, 'r') as f:
            if not trimmed:
                content = f.read().strip()                
            else:
                content = f.read(80)
                content = content.replace('#', '')  # Remove headings
                content = content.replace('*', '')  # Remove emphasis
                content = content.replace('![', '')  # Remove image syntax
                content = content.replace('![Image Alt Text]', '')  # Remove alt text for images
                content = content.replace('[', '')  # Remove link syntax
                content = content.replace(']', '')  # Remove link text
                content = content.replace('(', '')  # Remove link URL
                content = content.replace(')', '')  # Remove closing parenthesis for links
                #add more
            return content
    return None

def createpostarray(FolderName,Id,Date,Title,trimmed=False):
    post_dir = os.path.join('./static/posts/', FolderName)
    if os.path.isdir(post_dir):
        post_desc=readfile(post_dir, 'post.txt',trimmed)
        if post_desc:
            #add Title to the post
            post_desc = f'# {Title}\n\n{post_desc}'
            post_images = []
            for img_name in os.listdir(post_dir):
                if img_name.startswith('img'):
                    #img_path = os.path.join(post_dir, img_name)
                    #if os.path.isfile(img_path):
                    print("img name: ",img_name)
                    img_path=f"static/posts/{FolderName}/{img_name}"
                    #update image path in the markup
                    #print("post desc ",post_desc.find(f'{img_name}'))
                    post_desc_mod=post_desc.replace(f"{img_name}",f"{img_path}")
                    #print ("new post desc ",post_desc_mod)
                    post_images.append(img_path)
            
            if len(post_images)>0:
                post_desc=post_desc_mod           

            post = {
                    'id':Id,
                    'title':f'{Title}',
                    'date':Date.strftime("%Y-%m-%d"),
                    'description': post_desc,
                    'image': post_images
                    }
            return post
    return None

#@deprecated                            
def get_path_value(path):
    path_dict = {"main": 1, "feature": 2, "post": 3}
    return path_dict.get(path, None)

def get_trimmed_resp(path):
    path_dict = {"main": True, "feature": True, "post": False}
    return path_dict.get(path, None)

def getpostfromdb(db,path,id=None):
    posts_dir='./static/posts/'
    if id is None:
        posts=[]
        try:
            if (db.connect()):
                #select all folder from folders which start with pathname return did
                #from postmaster get date and title where did is same
                sql='''
                SELECT f.did, f.folder, m.title, m.date
                FROM (
                SELECT t.did
                FROM posttypes t
                WHERE t.type = '{posttype}'
                ORDER BY t.did DESC
                LIMIT {lim}
                ) AS subquery
                JOIN folders f ON subquery.did = f.did
                JOIN postmaster m ON subquery.did = m.did;
                '''.format(posttype=path, lim=get_path_value(path))
                print(f"/get-posts basic : corresponding sql= {sql}")
                res=db.query(sql)
                if res is not None:
                    #foldername=res[0][0]
                    #print("RES contents  ", res)
                    
                    for each_res in res:
                        #print("RES -------->  ", each_res)
                        Id, FolderName, Title, Date = each_res
                        #print(Id, FolderName, Title, Date)
                        post=createpostarray(FolderName,Id,Date,Title,get_trimmed_resp(path))
                        if post is not None:
                            posts.append(post)
                db.con_close() 
        except Exception as e:
            print ('DB_EXCEPTION_QUERY ', e)          
        return posts

def getpostdatafor(path,trimmed=False):
    posts_dir = './static/posts/'
    posts=[]
    for post_name in os.listdir(posts_dir):
        #print("1",post_name)
        post_dir = os.path.join(posts_dir, post_name)
        if (os.path.isdir(post_dir) and post_name.startswith(path)):
            post_desc=readfile(post_dir, 'post.txt',trimmed)
            if post_desc:
                title_desc=readfile(post_dir, 'title.txt')
                if title_desc:
                    date_desc=readfile(post_dir, 'date.txt')
                    if date_desc:
                        post_images = []
                        for img_name in os.listdir(post_dir):
                            if img_name.startswith('img'):
                                #img_path = os.path.join(post_dir, img_name)
                                #if os.path.isfile(img_path):
                                img_path=f"static/posts/{path}/{img_name}"
                                post_images.append(img_path)

                        post = {
                            'title':title_desc,
                            'date':date_desc,
                            'description': post_desc,
                            'image': post_images
                        }

                        posts.append(post)
    return posts

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
            title=request.form['title']
            if not title:
                title='Good Enough Info'
            if 'mainpost' in request.form:
                #save_file(path='mainpost',post_data=post_data,title_data=title)  #, overwrite=True)
                save_file_bak(post_data,title,'main')
            elif 'featuredpost' in request.form:
                #save_file(path='featuredpost',post_data=post_data,title_data=title)
                save_file_bak(post_data,title,'feature')
            else: # default
                #save_file(post_data=post_data,title_data=title)
                save_file_bak(post_data,title)
            return " "
        else:
            abort(403)
    else:
        return render_template('editor.html')

@app.route('/get-posts')
def get_posts():
    post_id = request.args.get('id')
    db=DB()
    if not post_id:
        return jsonify({'post':getpostfromdb(db,'post'),'feature':getpostfromdb(db,'feature'),'main':getpostfromdb(db,'main')})
    else:
        #find folder name for given ID
        post={}
        try:
            if (db.connect()):
                sql='''
                SELECT folders.did, folders.folder, postmaster.title, postmaster.date
                FROM folders
                JOIN postmaster ON folders.did = postmaster.did
                WHERE folders.did={id};
                '''.format(id=post_id)
                print(f"/get-posts?id={post_id}: corresponding sql= {sql}")
                res=db.query(sql)
                if res is not None:
                    for each_res in res:
                        print("RES -------->  ", each_res)
                        Id, FolderName, Title, Date = each_res
                        print(Id, FolderName, Title, Date)
                        #full response no trimmed response
                        # also we will create a markdown response
                        post=createpostarray(FolderName,Id,Date,Title)
                    '''post_dir = os.path.join('./static/posts/', foldername)
                    if os.path.isdir(post_dir):
                        post_desc=readfile(post_dir, 'post.txt')
                        if post_desc:
                            post_images = []
                            for img_name in os.listdir(post_dir):
                                if img_name.startswith('img'):
                                    #img_path = os.path.join(post_dir, img_name)
                                    #if os.path.isfile(img_path):
                                    img_path=f"static/posts/{foldername}/{img_name}"
                                    post_images.append(img_path)

                            post = {
                                'title':'',
                                'date':'',
                                'description': post_desc,
                                'image': post_images
                            }'''       
                db.con_close()
                
        except Exception as e:
            print ('DB_EXCEPTION_QUERY ', e)
        return jsonify({'post':post})