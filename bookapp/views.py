from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Avg, Count
from django.db.models.functions import Lower

from bookapp.forms import BookForm
from bookapp.models import Book

# Create your views here.
class BookCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    # Bug: la creación de libros debe requerir el permiso add_book (grupo Admin)
    permission_required = 'bookapp.add_book'
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookList(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'bookapp/list.html'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(title__icontains=query)
        sort = self.request.GET.get('sort', 'title')
        if sort in ['title', 'pages', 'rating', 'status', 'published_date']:
            if sort in ['title', 'status']:
                queryset = queryset.order_by(Lower(sort))
            else:
                queryset = queryset.order_by(sort)
        return queryset

class BookUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # Bug: la edición de libros debe requerir usuario autenticado y permiso change_book
    permission_required = 'bookapp.change_book'
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # Bug: el borrado de libros debe requerir usuario autenticado y permiso delete_book
    permission_required = 'bookapp.delete_book'
    model = Book
    template_name = 'bookapp/confirm_delete.html'
    success_url = reverse_lazy('book_list')

class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookapp/detail.html'
    context_object_name = 'book'

def stats(request):
    most_pages = Book.objects.order_by('-pages').first()
    least_pages = Book.objects.order_by('pages').first()
    avg_pages = Book.objects.aggregate(avg=Avg('pages'))['avg']
    avg_rating = Book.objects.aggregate(avg=Avg('rating'))['avg']

    books_by_status = (
        Book.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    status_labels = [dict(Book.STATUS_CHOICES).get(b['status'], b['status']) for b in books_by_status]
    status_values = [b['count'] for b in books_by_status]

    books_by_rating = (
        Book.objects
        .values('rating')
        .annotate(count=Count('id'))
        .order_by('rating')
    )
    rating_labels = [b['rating'] for b in books_by_rating]
    rating_values = [b['count'] for b in books_by_rating]

    return render(request, 'bookapp/stats.html', {
        'most_pages': most_pages,
        'least_pages': least_pages,
        'avg_pages': avg_pages,
        'avg_rating': avg_rating,
        'status_labels': status_labels,
        'status_values': status_values,
        'rating_labels': rating_labels,
        'rating_values': rating_values
    })

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('book_list')
    return render(request, 'bookapp/form.html', {'form': form})