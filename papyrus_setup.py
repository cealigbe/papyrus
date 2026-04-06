"""
  Script to set up the directory and files for the Papyrus.py SSG
"""

import os, sys

from papyrus_post import newpost


# JINJA HTML TEMPLATES

BASE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>{% block title %}{% endblock %} - {{ site.site_name }}</title>
	<link rel="stylesheet" href="/static/style.css" />
	<link rel="icon" href="/static/img/favicon.png" />
</head>

{% if page.id == "index" %}
<body id="home" class="{{ page.type }}">
{% else %}
<body id="{{ page.id }}" class="{{ page.type }}">
{% endif %}

  <header id="header">
      <h1>{{ site.site_name }}</h1>
      <nav id="site-nav">
        <menu>
          <li><a href="/">Home</a></li>
          <li><a href="/#work">Work</a></li>
          <li><a href="/posts.html">Posts</a></li>
        </menu>
      </nav>
    </header>

  <main id="main">
  {% block content %}
    <p>This is the content block of the website. This will be filled in by Papyrus.py with your templates.</p>
  {% endblock %}
  </main>

  <footer id="footer">
		<p>
		  {{ site.site_name }}, &copy; {{ page.created.split('-')[0] }} &emsp; | &emsp; powered by <a href="https://github.com/cealigbe/papyrus" target="_blank">Papyrus.py</a>
		</p>
	</footer>

  <script src="/static/script.js"></script>
</body>
</html>
"""

INDEX_HTML = """{% extends 'templates/_base.html' %}

<title>
  {% block title %}Home{% endblock %}
</title>

{% block content %}

<section>
  <h2>Hello World</h2>
  <p>
    Welcome to my website. Lorem ipsum and all that jazz... Dolore nisi in magna amet occaecat minim in. Sunt sint eiusmod officia dolor culpa ex. Anim elit lorem exercitation in. Excepteur elit reprehenderit dolor cupidatat minim.
  </p>
  <br />
  <figure>
    <img src="http://static.photos/blue/640x360/137" alt="this is a picture">
    <figcaption>This is a picture</figcaption>
  </figure>
</section>

{% endblock %}
"""

POSTS_HTML = """{% extends 'templates/_base.html' %}

<title>
  {% block title %}Posts{% endblock %}
</title>

{% block content %}

<section id="article-listing">
  <h2>My Posts</h2>

 <ul id="articles">
  {% for post in posts %}
  <li>
    <a href="/{{ post.href }}">{{ post.title }}</a>
    <span class="date">{{ post.date.strftime('%Y-%m-%d') }}</span>
  </li>
  {% endfor %}
 </ul>
</section>

{% endblock %}
"""

POST_HTML = """{% extends 'templates/_base.html' %}

<title>
  {% block title %}{{ post.title }}{% endblock %}
</title>

{% block content %}

<article id="{{ post.title | slugify }}" class="post {{ post.category | slugify }}">
  <header class="article-header">
    <h2>{{ post.title }}</h2>
    <p class="meta">written by {{ post.author }}, on {{ post.date.strftime('%Y-%m-%d') }}</p>
  </header>

  {{ post.html | safe }}

  <footer class="article-footer">
    <p>
      Category: <a href="/categories/{{ post.category | slugify }}.html">{{ post.category }}</a>
    </p>
  </footer>
</article>

{% endblock %}
"""

CATEGORY_HTML = """{% extends 'templates/_base.html' %}

<title>
  {% block title %}"{{ category | capitalize }}" posts{% endblock %}
</title>

{% block content %}

<section id="article-listing">
  <h2>Posts in the "{{ category }}" category</h2>

 <ul id="articles">
  {% for post in posts %}
  <li>
    <a href="/{{ post.href }}">{{ post.title }}</a>
    <span class="date">{{ post.date.strftime('%Y-%m-%d') }}</span>
  </li>
  {% endfor %}
 </ul>
</section>

{% if all_categories %}
<aside id="categories">
  <h3>All Categories</h3>
  <ul class="category-list">
    {% for cat in all_categories %}
    <li>
      <a href="/categories/{{ cat.slug }}.html"
         {% if cat.slug == category_slug %}aria-current="page"{% endif %}>
        {{ cat.name }}
      </a>
      <span class="count"> ({{ cat.count }})</span>
    </li>
    {% endfor %}
  </ul>
</aside>
{% endif %}

{% endblock %}
"""

# STYLESHEET AND SCRIPT TEMPLATES

STYLESHEET = """/* Papyrus.py SSG Starter CSS */

*, *::before, *::after {
  box-sizing: border-box;
}
*:not(dialog) {
  margin: 0;
}
:root {
  accent-color: #08f;
}
html {
  color-scheme: light dark;
}
body {
  -webkit-font-smoothing: antialiased;
  background-color: light-dark(#f9f9f9, #222);
  color: light-dark(#222, #fff);
  min-height: 100vh;
  padding: 1.5rem;
  font-family: system-ui, Helvetica, Arial, sans-serif;
  font-size: 1.125rem;
  line-height: 1.5;
  display: flex;
  flex-direction: column;
}
img, picture, video, canvas, svg {
  display: block;
  max-width: 100%;
}
figcaption, caption, .caption {
  font-size: 0.9em;
  text-align: center;
  padding: 1rem 0;
}
figure > img {
  margin: 0 auto;
}
input, button, textarea, select {
  font: inherit;
}
input:not([type='radio'], [type='checkbox']), button, textarea, select {
  display: block;
  min-width: 20rem;
  margin-block: 0.5rem 1rem;
}
input, textarea, select {
  padding: 0.5rem 0.75rem;
  border: 2px solid light-dark(#333, #ccc);
  border-radius: 4px;
  background-color: light-dark(#eee, #202020);
}
button, input:is([type='button'], [type='submit'], [type='reset']) {
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 4px;
  background-color: #08f;
  color: #eee;
  font-weight: bold;
  transition: opacity 0.2s ease;
  cursor: pointer;
}
button:is(:hover, :focus), input:is([type='button'], [type='submit'], [type='reset']):is(:hover, :focus) {
  opacity: 0.75;
}
input:is([type='radio'], [type='checkbox']) {
  position: relative;
  padding: 0;
  margin-inline-end: 0.25rem;
  width: 1em;
  height: 1em;
  top: 0.125em;
  cursor: pointer;
}
label {
  display: block;
  margin-bottom: 0.5rem;
}
p, h1, h2, h3, h4, h5, h6 {
  overflow-wrap: break-word;
}
p {
  text-wrap: pretty;
  margin-block: 0 1rem;
}
h1, h2, h3, h4, h5, h6 {
  text-wrap: balance;
  margin-block: 0.5rem 1rem;
}
h1, h2, h3, h4 {
  line-height: 1.2;
}
a {
  color: #08f;
  font-weight: bold;
  transition: opacity 0.2s ease;
}
a:hover, a:focus {
  opacity: 0.75;
}
hr {
  background-color: transparent;
  border-bottom: 2px solid light-dark(#666, #ccc);
  height: 0;
  margin-block: 0.75rem;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
}
table th, table td {
  padding: 0.5rem;
  text-align: left;
  border: none;
}
table tr:nth-of-type(2n) td {
  background-color: light-dark(#e0e0e0, #404040);
}
table th {
  border-bottom: 2px solid light-dark(#666, #ccc);
  font-weight: bold;
}
header, main, footer, section, article, aside {
  margin-bottom: 2rem;
}
body > :is(header, main, footer) {
  width: 100%;
  flex: 0 0 auto;
}
body > header {
  display: grid;
  grid-template-columns: max-content 1fr;
  align-items: center;
}
body > main {
  max-width: min(50rem, 100%);
  margin-inline: auto;
  flex: 2 0 auto;
}
body > footer {
  text-align: center;
  margin-block: 2rem 0;
  font-size: 1rem;
}
aside {
  padding: 1rem;
  background-color: light-dark(#ddd, #333);
  border: 2px solid light-dark(#666, #ccc);
  border-radius: 0.5rem;
}
nav#site-nav {
  width: 100%;
}
nav > menu {
  list-style: none;
  display: flex;
  margin: 0;
  gap: 4px;
  padding: 0;
  justify-content: right;
  align-items: center;
}
nav#site-nav li {
  padding: 0.5rem 1rem;
}
ul#articles {
  padding: 1rem 0;
  list-style: none;
}
ul#articles li {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
ul.category-list {
  margin-bottom: 1rem;
}
"""

JAVASCRIPT = """// Papyrus.py SSG Starter JS

console.log('Hello World');
"""

# SET UP FOLDER + FILE LISTS

folders = ["posts", "templates", "static", "build", os.path.join("static", "img")]
templates = [
    {"name": "_base", "html": BASE_HTML},
    {"name": "index", "html": INDEX_HTML},
    {"name": "posts", "html": POSTS_HTML},
    {"name": "post", "html": POST_HTML},
    {"name": "category", "html": CATEGORY_HTML}
]
stylescript = [
    {"name": "style.css", "content": STYLESHEET},
    {"name": "script.js", "content": JAVASCRIPT},
]

# INITIALIZE FUNCTION TO CREATE FOLDERS AND WRITE FILES

def initalize():
  for folder in folders:
    if not os.path.exists(folder):
      os.makedirs(folder)

  for temp in templates:
    name = temp["name"]
    html = temp["html"]
    with open(os.path.join('templates', name+'.html'), 'w') as htmlfile:
      htmlfile.write(html)
      print(f"Created Jinja template file for {name}.html in 'templates' folder")

  for item in stylescript:
    name = item["name"]
    content = item["content"]
    with open(os.path.join('static', name), 'w') as sfile:
      sfile.write(content)
      print(f"Created static file for {name} in 'static' folder")

  newpost("my-first-post.md")

if __name__ == "__main__":
  initalize()
