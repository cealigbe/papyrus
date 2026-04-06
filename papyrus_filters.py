"""
Additional classes and functions that you can import to build additional collections pages.

- Folio: generates a post-like folio page for a portfolio, using the folio.html jinja template
"""

class Folio:
  # represents a special collection item for portfolio pages

  def __init__(self, filename, env, tempfile="folio.html", sitedata=config):
    # initialize
    self.filename = filename
    self.tempfile = tempfile

    self.page_id = slugify(self.filename.split(".")[0])

    with open(os.path.join('folios', self.filename), 'r') as foliofile:
       extensions = ['fenced_code', 'tables', 'meta', 'md_in_html', 'attr_list']
       md = markdown.Markdown(extensions=extensions)
       self.html = md.convert(foliofile.read())
       self.meta = {k: v[0] for k, v in md.Meta.items()}

    # adjust meta values
    self.meta["date"] = datetime.datetime.strptime(self.meta['date'], '%Y-%m-%d')
    self.meta["draft"] = self.meta.get('draft', 'false').lower() == 'true'

    self.out_filename = self.page_id + ".html"
    self.href = "folios/" + self.out_filename

    pagedata = {"id": self.page_id, "type": "folio", "created": config["build_date"]}
    template = env.get_template(os.path.join("templates", tempfile))
    self.page_html = template.render(
        folio=dict(html=self.html, **self.meta),
        page=pagedata,
        site=sitedata
    )

  def write(self):
    # write rendered html to file
    out_path = os.path.join('build', 'folios', self.out_filename)
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


def build_folios(env):
  # creates a Folio page object for each markdown file in folios/ with meta tag "draft = false"
  # then writes each post's html to the output path and returns a list of Post objects sorted by newest-first

  if not os.path.exists('templates/folio.html'):
    print("no folio template found -- skipping folio pages.\n")
    return []

  folios = []
  for filename in os.listdir('folios'):
    if not filename.endswith('.md'): continue
    folio = Folio(filename, env)
    if folio.get_meta("draft") == True: continue
    print(f'building folio page: {folio.out_filename}')
    folio.write()
    folios.append(folio)

  folios.sort(key=lambda fl: fl.get_meta("date"), reverse=True)
  return folios

