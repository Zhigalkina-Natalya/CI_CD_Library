from django.test import TestCase
from .models import Author, Book, Review
from datetime import date
from .forms import AuthorForm
from .services import BookService
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import override_settings

User = get_user_model()


class AuthorModelTest(TestCase):

    def test_create_author(self):
        author = Author.objects.create(
            first_name="Leo",
            last_name="Tolstoy",
            birth_date=date(1828, 9, 9)
        )
        self.assertEqual(str(author), "Leo Tolstoy")
        self.assertEqual(author.first_name, "Leo")


class BookModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="George",
            last_name="Orwell",
            birth_date=date(1903, 6, 25)
        )

    def test_create_book(self):
        book = Book.objects.create(
            title="1984",
            publication_date=date(1949, 6, 8),
            author=self.author
        )
        self.assertEqual(str(book), "1984")
        self.assertEqual(book.author, self.author)


class ReviewModelTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Author",
            last_name="Test",
            birth_date=date(1990, 1, 1)
        )
        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2020, 1, 1),
            author=self.author
        )

    def test_create_review(self):
        review = Review.objects.create(
            book=self.book,
            rating=5,
            comment="Great!"
        )
        self.assertEqual(str(review), f"Review for {self.book.title}")
        self.assertEqual(review.rating, 5)


class AuthorFormTest(TestCase):

    def test_valid_form(self):
        form_data = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "birth_date": "2000-01-01"
        }
        form = AuthorForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_author(self):
        Author.objects.create(
            first_name="Ivan",
            last_name="Ivanov",
            birth_date="2000-01-01"
        )

        form_data = {
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "birth_date": "2000-01-01"
        }
        form = AuthorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Автор с таким именем и фамилией уже существует.", form.errors["__all__"])


class BookServiceTest(TestCase):

    def setUp(self):
        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author",
            birth_date=date(1990, 1, 1)
        )
        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2020, 1, 1),
            author=self.author
        )

    def test_average_rating_no_reviews(self):
        self.assertIsNone(BookService.calculate_average_rating(self.book.id))

    def test_average_rating(self):
        Review.objects.create(book=self.book, rating=4, comment="Good")
        Review.objects.create(book=self.book, rating=2, comment="Bad")

        avg = BookService.calculate_average_rating(self.book.id)
        self.assertEqual(avg, 3)

    def test_is_popular(self):
        Review.objects.create(book=self.book, rating=5, comment="Great")
        Review.objects.create(book=self.book, rating=4, comment="Nice")

        self.assertTrue(BookService.is_popular(self.book.id))

    def test_is_not_popular(self):
        Review.objects.create(book=self.book, rating=2, comment="Bad")

        self.assertFalse(BookService.is_popular(self.book.id))

@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
)
class BookViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@test.com",
            username="testuser",
            password="12345"
        )

        self.author = Author.objects.create(
            first_name="Test",
            last_name="Author",
            birth_date=date(1990, 1, 1)
        )

        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2020, 1, 1),
            author=self.author
        )

    def test_books_list_requires_login(self):
        response = self.client.get(reverse('library:books_list'))
        self.assertEqual(response.status_code, 302)

    def test_books_list_logged_in(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('library:books_list'))
        self.assertEqual(response.status_code, 200)


class BookPermissionTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            username="user",
            password="12345"
        )

        self.author = Author.objects.create(
            first_name="Author",
            last_name="Test",
            birth_date=date(1990, 1, 1)
        )

        self.book = Book.objects.create(
            title="Test Book",
            publication_date=date(2020, 1, 1),
            author=self.author
        )

    def test_review_without_permission(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('library:book_review', args=[self.book.id]),
            {"review": "Nice book"}
        )

        self.assertEqual(response.status_code, 403)

    def test_review_with_permission(self):
        permission = Permission.objects.get(codename='can_review_book')
        self.user.user_permissions.add(permission)

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('library:book_review', args=[self.book.id]),
            {"review": "Nice book"}
        )

        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertEqual(self.book.review, "Nice book")

    def test_recommend_without_permission(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('library:book_recommend', args=[self.book.id])
        )

        self.assertEqual(response.status_code, 403)

    def test_recommend_with_permission(self):
        permission = Permission.objects.get(codename='can_recommend_book')
        self.user.user_permissions.add(permission)

        self.client.force_login(self.user)

        response = self.client.post(
            reverse('library:book_recommend', args=[self.book.id])
        )

        self.assertEqual(response.status_code, 302)
        self.book.refresh_from_db()
        self.assertTrue(self.book.recommend)
