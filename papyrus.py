"""
Papyrus.py static site generator, http://github.com/cealigbe/papyrus
Written by Chuck Aligbe [http://chuck.aligbe.com]
based on Cacty.py [https://claudio.uk/posts/cacty.html]
"""

import os, sys, shutil, markdown, time, datetime, http.server, socketserver, toml
import markdown.extensions.fenced_code
import markdown.extensions.tables
import markdown.extensions.attr_list

from collections import defaultdict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# from papyrus_filters import Folio, build_folios

# Get config
with open("config.toml", "r") as tomlfile:
    config = toml.load(tomlfile)

build_date = datetime.datetime.now()

config["build_date"] = build_date.strftime("%Y-%m-%d")

"""
Class Definitions
- Post: generates a post page from markdown with author, date, and taxonomy meta using the post.html jinja template
- Page: generates a standard (non-collection) page from a jinja template; used for index.html, posts.html, etc.
- Category: generates a page listing all the posts of that category using the category.html template
"""

class Post:
  # represents the Post page type built from a markdown source file

  def __init__(self, filename, env, tempfile="post.html", sitedata=config):
    # initialize
    self.filename = filename
    self.tempfile = tempfile

    self.page_id = slugify(self.filename.split(".")[0])

    with open(os.path.join('posts', self.filename), 'r') as mdfile:
       extensions = ['fenced_code', 'tables', 'meta', 'md_in_html', 'attr_list']
       md = markdown.Markdown(extensions=extensions)
       self.html = md.convert(mdfile.read())
       self.meta = {k: v[0] for k, v in md.Meta.items()}

    # adjust meta values
    self.meta["category"] = self.meta.get('category', 'uncategorized').strip()
    self.meta["date"] = datetime.datetime.strptime(self.meta['date'], '%Y-%m-%d')
    self.meta["draft"] = self.meta.get('draft', 'false').lower() == 'true'

    self.out_filename = self.page_id + ".html"
    self.href = "posts/" + self.out_filename

    pagedata = {"id": self.page_id, "type": "post", "created": config["build_date"]}
    template = env.get_template(os.path.join("templates", tempfile))
    self.page_html = template.render(
        post=dict(html=self.html, **self.meta),
        page=pagedata,
        site=sitedata
    )

  def write(self):
    # write rendered html to file
    out_path = os.path.join('build', 'posts', self.out_filename)
    with open(out_path, 'w') as f:
      f.write(self.page_html)

  def get_meta(self, key=""):
    # get mata values fast
    if key.strip() == "":
      return self.meta

    if key in self.meta:
      return self.meta[key]
    else:
      print(key + " not in ")
      return None

  def as_dict(self):
    # return a plain dict for passing into listing templates
    return dict(
        filename=self.filename,
        href=self.href,
        page_id=self.page_id,
        **{k: v for k, v in self.meta.items()},
    )

class Page:
  # represents a standard page from a top-level template

  def __init__(self, filename, env, posts=[], categories=[], sitedata=config):
    # initialize
    self.filename = filename
    self.page_id = slugify(self.filename.split(".")[0])

    pagedata = {"id": self.page_id, "type": "page", "created": config["build_date"]}
    template = env.get_template(os.path.join("templates", filename))
    self.page_html = template.render(
      posts=posts,
      categories=categories,
      page=pagedata,
      site=sitedata
    )

  def write(self):
    # write rendered html to file
    out_path = os.path.join('build', self.filename)
    with open(out_path, 'w') as f:
      f.write(self.page_html)

  def as_dict(self):
    # return a plain dict for passing into listing templates
    return dict(
        filename=self.filename,
        page_id=self.page_id,
    )

class Category:
  # represents a listing page of posts that share a category

  def __init__(self, name, all_categories, env, tempfile="category.html", posts=[], sitedata=config):
    # initialize
    self.name = name
    self.slug = slugify(name)
    self.page_id = f"category-{self.slug}"

    self.posts = posts
    self.all_categories = all_categories

    pagedata = {"id": self.page_id, "type": "taxonomy", "created": config["build_date"]}
    template = env.get_template(os.path.join("templates", tempfile))
    self.page_html = template.render(
        category=self.name,
        category_slug=self.slug,
        posts=self.posts,
        all_categories=self.all_categories,
        page=pagedata,
        site=sitedata
    )

    self.out_filename = self.slug + ".html"
    self.href = "categories/" + self.out_filename

  def write(self):
    # write rendered html to file
    out_path = os.path.join('build', "categories", self.out_filename)
    with open(out_path, 'w') as f:
      f.write(self.page_html)

  def as_dict(self):
    # return a plain dict for passing into listing templates
    return dict(
      name=self.name,
      slug=self.slug,
      id=self.page_id,
      posts=self.posts,
      href=self.href
    )


"""
Page builders - generates html files and returns lists of their respective class objects
"""

def build_posts(env):
  """creates a Post object for each markdown file in posts/ with meta tag "draft = false", then writes each post's html to the output path and returns a list of Post objects sorted by newest-first"""

  posts = []
  for filename in os.listdir('posts'):
    if not filename.endswith('.md'): continue
    post = Post(filename, env)
    if post.get_meta("draft") == True: continue
    print(f'building post: {post.out_filename}')
    post.write()
    posts.append(post)

  posts.sort(key=lambda p: p.get_meta("date"), reverse=True)
  return posts

def build_pages(env, posts, categories=[]):
  """creates a Page object for each top-level tempate in tempates/. Skips partials (files starting with _) and collection templates in ignored (post.html, category.html, etc) which are handled by their own build functions. Also writes a each page's HTML to its output path, and returns a list of Page objects"""

  post_dicts = [p.as_dict() for p in posts]
  cat_dicts = [c.as_dict() for c in categories]
  # folio_dicts = [f.as_dict() for f in folios]
  pages = []
  ignored = ['post.html', 'category.html']

  for filename in os.listdir('templates'):
    if os.path.isfile(os.path.join('templates', filename)) == False: continue
    name, ext = filename.split(".")
    if ext not in ('html', 'xml'): continue
    if filename.startswith('_') or filename in ignored: continue

    page = Page(filename, env, post_dicts, cat_dicts)
    print(f"building page: {page.filename}")
    page.write()
    pages.append(page)

  return pages


def build_categories(env, posts):
  """Creates a Category object for each unique category found across all posts. Requires category.html jinja template to render; skips gracefully if absent. Also writes each category's rendered HTML to its output path and returns a list of category objects"""

  if not os.path.exists('templates/category.html'):
    print("no category template found -- skipping category pages.\n")
    return []

  post_groups = defaultdict(list)
  for post in posts:
    post_groups[post.get_meta("category")].append(post.as_dict())

  all_categories = []
  for name, cat_posts in sorted(post_groups.items()):
    c = dict(name=name, slug=slugify(name), count=len(cat_posts))
    all_categories.append(c)

  categories = []
  for name, post_dicts in post_groups.items():
    category = Category(name, all_categories, env, posts=post_dicts)
    print(f"building category page: {category.out_filename} ({len(post_dicts)} posts)")
    category.write()
    categories.append(category)

  print(f'built {len(categories)} category page(s)\n')
  return categories

# -----------------------
# Utility Functions
# -----------------------

def slugify(text):
  return text.lower().strip().replace(' ', '-')

def build():
  # build and transfer all posts, pages, and collections to their respective locations in build/
  # add additional collection folders in the list below

  folders = ["static", "posts", "categories"]

  for fd in folders:
    fpath = os.path.join("build", fd)
    os.makedirs(fpath, exist_ok=True)

  jinja = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(),
        extensions=['jinja_markdown.MarkdownExtension']
  )

  jinja.filters["slugify"] = slugify
  posts = build_posts(jinja)
  categories = build_categories(jinja, posts)
  # folios = build_folios(jinja)
  build_pages(jinja, posts, categories)

  shutil.copytree("static", os.path.join("build", "static"), dirs_exist_ok=True)

  with open("config.toml", "w") as tomlfile:
    toml.dump(config, tomlfile)

  print('build complete\n')

def watch_files():
    # If any file changes in templates/ posts/ categories/ or static/, rebuild the site.
    class Handler(FileSystemEventHandler):
        def __init__(self):
            super().__init__()
            self.last_run = time.time()

        def on_any_event(self, event):
            if time.time() - self.last_run < 1:
                return
            print(f'{event.src_path} changed, rebuilding')
            build()
            self.last_run = time.time()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, '.', recursive=True)
    print('watching files')
    observer.start()


def start_http_server():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory='build', **kwargs)

    try:
        port = 8246
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print("serving at http://localhost:" + str(port))
            httpd.serve_forever()
    except KeyboardInterrupt as exc:
        httpd.shutdown()
        httpd.server_close()
        raise


if __name__ == '__main__':
  build()
  if '-w' in sys.argv:
    watch_files()
    start_http_server()
