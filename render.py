from __future__ import unicode_literals
import collections
import datetime
import os
import multiprocessing
import shutil
import subprocess

from docutils.core import publish_parts as docutils_publish
from docutils.parsers.rst import directives
from pygments_directive import pygments_directive
from mako.template import Template
from mako.lookup import TemplateLookup

lmap = lambda func, *iterable: list(map(func, *iterable))

class OrderedDefaultdict(collections.OrderedDict):

    def __init__(self, *args, **kwargs):
        if not args:
            self.default_factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.default_factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        self[key] = default = self.default_factory()
        return default

    def __reduce__(self):  # optional, for pickle support
        args = (self.default_factory,) if self.default_factory else ()
        return self.__class__, args, None, None, self.iteritems()

directives.register_directive('code-block', pygments_directive)

shutil.rmtree('_build', ignore_errors=True)

def write_html(html, htmlpath):
    htmldir = os.path.dirname(htmlpath)
    if not os.path.exists(htmldir):
        os.makedirs(htmldir)
    with open(htmlpath, 'w') as htmlfile:
        htmlfile.write(html)

def slug_buildpath_title(rst_path):
    bare_path, ext = os.path.splitext(rst_path)
    slug = os.path.split(bare_path)[-1]
    buildpath = (bare_path + '.html').replace('blog', '_build')
    title = ' '.join(slug.split('-')).capitalize()
    return slug, buildpath, title

def prev_next(rst_path):
    try:
        next_index = rst_paths.index(rst_path) - 1
        if next_index < 0:
            nextpath = nexttitle = None
        else:
            _, nextpath, nexttitle = slug_buildpath_title(rst_paths[next_index])
            nextpath = nextpath.replace('_build', '')
    except IndexError:
        nextpath = nexttitle = None
    try:
        _, previouspath, previoustitle = slug_buildpath_title(rst_paths[rst_paths.index(rst_path) + 1])
        previouspath = previouspath.replace('_build', '')
    except IndexError:
        previouspath = previoustitle = None
    return previouspath, previoustitle, nextpath, nexttitle

def parse_meta(rst_path):
    slug, buildpath, title = slug_buildpath_title(rst_path)
    previouspath, previoustitle, nextpath, nexttitle = prev_next(rst_path)
    return {
        'date': datetime.date(*map(int, rst_path.split(os.sep)[1:4])),
        'title': title,
        'slug': slug,
        'buildpath': buildpath,
        'nextpath': nextpath,
        'nexttitle': nexttitle,
        'previouspath': previouspath,
        'previoustitle': previoustitle,
    }



def render_rst(rst_path):
    with open(rst_path, 'r') as rst_file:
        rst_string = rst_file.read()
    return docutils_publish(rst_string, writer_name='html')['html_body']


def build_index(rst_paths):
    D = OrderedDefaultdict
    month_tree = D(lambda: D(list))
    for rst_path in rst_paths:
        meta = parse_meta(rst_path)
        date = meta['date']
        month_tree[date.year][date.month].append(meta)
    return month_tree


def render_mako(rst_path):
    context = {
        'index': index,
        'meta': parse_meta(rst_path),
        'content_html': render_rst(rst_path),
    }
    template = Template(filename='templates/post.html', lookup=template_lookup)
    write_html(template.render(**context), context['meta']['buildpath'])

def build_blog_page(blog_template):
    buildpath = blog_template.replace('templates', '_build').replace('rst', 'html')
    index_rst = Template(filename=blog_template, lookup=template_lookup).render(index=index)
    content_html = docutils_publish(index_rst, writer_name='html')['html_body']
    context = {
        'index': index,
        'content_html': content_html,
        'meta': {'title': 'Blog'},
    }
    template = Template(filename='templates/page.html', lookup=template_lookup)
    write_html(template.render(**context), buildpath)

def build_page(rst_path):
    bare_path, ext = os.path.splitext(rst_path)
    slug = os.path.split(bare_path)[-1]
    buildpath = (bare_path + '.html').replace('pages', '_build')
    context = {
        'index': index,
        'meta': {
            'title': slug.capitalize(),
            'buildpath': buildpath,
        },
        'content_html': render_rst(rst_path),
    }
    template = Template(filename='templates/page.html', lookup=template_lookup)
    write_html(template.render(**context), context['meta']['buildpath'])

def build_copy_dir(dir_):
    shutil.copytree(dir_, os.path.join('_build', dir_))

def build_copy_file(source, dest):
    shutil.copy(source, dest)

def build():
    global index
    global template_lookup
    global rst_paths

    find = subprocess.check_output(['find', 'blog', '-name', '*.rst'],
                                   universal_newlines=True)
    rst_paths = sorted(find.split(), reverse=True)

    index = build_index(rst_paths)
    template_lookup = TemplateLookup(directories=['.'])

    pool = multiprocessing.Pool(8)

    pool.map_async = lmap
    pool.map_async(build_page, (
        'pages/about.rst',
        'pages/projects.rst',
    ))
    pool.map_async(render_mako, rst_paths)
    pool.map_async(build_copy_dir, (
        'assets/images',
        'assets/js',
        'assets/fonts',
        'bower_components',
    ))
    pool.apply_async(shutil.copy, ('templates/index.html', '_build'))
    build_blog_page('templates/blog.rst')

    pool.close()
    pool.join()
    subprocess.check_call(['sass', 'assets/scss', '_build/assets/css'])
    print('done.')


if __name__ == '__main__':
    build()
