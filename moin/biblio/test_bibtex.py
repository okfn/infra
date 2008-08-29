import bibtex

bibtex_text = '''
@thesis{gillett_1970,
  title={{Phase transitions in Bak-Sneppen avalanches and in a continuum percolation model}},
  author={Gillett, A.J.},
  year={2007},
  month={sep},
  url={http://dare.ubvu.vu.nl//handle/1871/10887},
}

@book{alexander_1977,
	title = {A Pattern Language: Towns, Buildings, Construction},
	isbn = {0195019199},
	publisher = {Oxford University Press, USA},
	author = {Christopher Alexander},
	year = {1977},
	pages = {1216}
}
'''

class Config(object):
    bibtex_bib2html = 'bibtex2html'

class Request(object):
    
    cfg = Config()

renderer = bibtex.BibtexRenderer(bibtex_text, Request())
out = renderer.render()
out = out.strip()
assert out.startswith('<dl>'), out
assert 'alexander_1977' in out
assert 'gillett_1970' in out
assert out.index('alexander_1977') < out.index('gillett_1970')
# print out

renderer = bibtex.BibtexRenderer(bibtex_text, Request(),
    citations=['gillett_1970'])
out = renderer.render()
out = out.strip()
assert 'gillett_1970' in out
assert 'denman_2003' not in out
# print out
