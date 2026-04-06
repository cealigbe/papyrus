import os
import xml.etree.cElementTree as ET
from datetime import datetime

def generate_sitemap(dir, url, outfile="sitemap.xml"):
  # generate a sitemap from files in the specified folder using the url provided
  root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

  for dirpath, _, filenames in os.walk(dir):
    for filename in filenames:
      if filename.endswith('.html') == True:
        fp = os.path.join(dirpath, filename)
        rp = os.path.relpath(fp, dir).replace(os.sep, '/')
        loc = url + "/" + rp

        url_entry = ET.SubElement(root, "url")
        ET.SubElement(url_entry, "loc").text = loc

        mtime = os.path.getmtime(fp)
        lastmod = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        ET.SubElement(url_entry, "lastmod").text = lastmod

  tree = ET.ElementTree(root)
  ET.indent(tree, space="\t")
  tree.write(outfile, encoding='utf-8', xml_declaration=True)
  print("Sitemap generated: " + outfile)


if __name__ == "__main__":
  import tomllib

  with open("config.toml", "rb") as tomlfile:
    config = tomllib.load(tomlfile)

  siteurl = config["site_url"]
  generate_sitemap("build", siteurl)
