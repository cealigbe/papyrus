"""
  Script to automatically create a Markdown file with metadata for the Papyrus.py SSG
"""

import os, sys
from datetime import date

POST_TEMPLATE = """---
title: Post Title
description: This is the post description
author: Author
category: uncategorized
date: {0}
---

This is the post body. Replace this, as well as the title, description, author, and category meta tags above with real data.
"""

def newpost(filename):
  namelist = filename.split(".")

  if len(namelist) > 1 and namelist[-1] != "md":
    print("Error: expected Markdown file")
    return

  if len(namelist) == 1:
    filename = filename + ".md"

  today = date.today()
  blank_post = POST_TEMPLATE.format(today)

  with open(os.path.join('posts', filename), "w") as mdfile:
    mdfile.write(blank_post)
    print(f"Created Markdown file for {filename} in 'posts' folder")


if __name__ == "__main__":
  filename = sys.argv[1]
  newpost(filename)
