from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from .models import Author, Book
from django.urls import reverse_lazy
from .forms import AuthorForm, BookForm
from django.core.cache import  cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .services import BookService


class ReviewBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        if not request.user.has_perm('library.can_review_book'):
            return HttpResponseForbidden("У вас нет прав для рецензирования книги.")

        # Логика рецензирования книги
        book.review = request.POST.get('review')
        book.save()

        return redirect('library:book_detail', pk=book.id)


class RecommendBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)

        if not request.user.has_perm('library.can_recommend_book'):
            return HttpResponseForbidden("У вас нет прав для рекомендации книги.")

        # Логика рекомендации книги
        book.recommend = True
        book.save()

        return redirect('library:book_detail', pk=book.pk)


class AuthorListView(ListView):
    model = Author
    template_name = 'library/authors_list.html'
    context_object_name = 'authors'

    def get_queryset(self):
        queryset = cache.get('authors_queryset')
        if not queryset:
            queryset = super().get_queryset()
            cache.set('authors_queryset', queryset, 60 * 15) # Кешируем данные на 15 минут
            return queryset


class AuthorCreateView(CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library/author_form.html'
    success_url = reverse_lazy('library:authors_list')


class AuthorUpdateView(UpdateView):
    model = Author
    form_class = AuthorForm
    template_name = 'library/author_form.html'
    success_url = reverse_lazy('library:authors_list')

@method_decorator(cache_page(60 * 15), name='dispatch')
class BooksListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'library/books_list.html'
    context_object_name = 'books'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(publication_date__year__gt=1900)

# @method_decorator(cache_page(60 * 15), name='dispatch')
class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'library/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        # Получаем стандартный контекст данных из родительского класса
        context = super().get_context_data(**kwargs)
        context['author_books_count'] = Book.objects.filter(author=self.object.author).count()

        # Получаем ID книги из объекта
        book_id = self.object.id
        # Добавляем в контекст средний рейтинг и статус популярности книги
        context['average_rating'] = BookService.calculate_average_rating(book_id)
        context['is_popular'] = BookService.is_popular(book_id)
        return context


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.add_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'library/book_form.html'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.change_book'


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Book
    template_name = 'library/book_confirm_delete.html'
    success_url = reverse_lazy('library:books_list')
    permission_required = 'library.delete_book'
