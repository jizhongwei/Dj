from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify
from django.db.models import Q

from .models import *

import markdown
from markdown.extensions.toc import TocExtension


def index(request):
    post_all = Post.objects.all().order_by('-created_time')
    tags = Tag.objects.all()
    paginator = Paginator(post_all,4)
    page = request.GET.get('page')
    try:
        post_list = paginator.page(page)
    except PageNotAnInteger:
        post_list = paginator.page(1)
    except EmptyPage:
        post_list = paginator.page(paginator.num_pages)
    return render(request, 'blog/index.html',{
        'post_list': post_list,
        'tags': tags
    })

def detail(request, pk):
    post = get_object_or_404(Post, pk = pk)
    tags = Tag.objects.all()
    post.increase_views()
    md = markdown.Markdown(extensions = [
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      # 'markdown.extensions.toc',
                                     TocExtension(slugify = slugify)
                                  ])
    post.body = md.convert(post.body)
    post.toc = md.toc
    return render(request, 'blog/detail.html', {'post': post, 'tags': tags})

def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year= year,
                                    created_time__month= month
                                    ).order_by('-created_time')
    return render(request, 'blog/index.html', {'post_list': post_list})

def category(request, pk):
    cate = get_object_or_404(Category, pk = pk)
    tags = Tag.objects.all()
    post_list = Post.objects.filter(category = cate).order_by('-created_time')
    return render(request, 'blog/index.html', {'post_list': post_list, 'tags': tags})

def tag(request, pk):
    tag = get_object_or_404(Tag, pk = pk)
    tags = Tag.objects.all()
    post_list = Post.objects.filter(tags= tag)
    return render(request, 'blog/index.html', {'post_list': post_list, 'tags': tags})

def search(request):
    q = request.GET.get('q')
    error_msg = ''
    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html',{'error_msg': error_msg})
    post_list = Post.objects.filter(Q(title__icontains= q) | Q(body__icontains= q))
    return render(request, 'blog/index.html', {'error_msg': error_msg,'post_list': post_list})

class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

class CategoryView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk = self.kwargs.get('pk'))
        return super(CategoryView,self).get_queryset().filter(category= cate)

class ArchiveView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchiveView, self).get_queryset().filter(created_time__year = year, created_time__month = month)

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request,*args, **kwargs):
        response = super(PostDetailView,self).get(request, *args,**kwargs)
        self.object.increase_views()
        return response