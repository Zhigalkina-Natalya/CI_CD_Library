from .models import Book, Review

class BookService:

    @staticmethod
    def calculate_average_rating(book_id):
        # Получаем все отзывы для книги
        reviews = Review.objects.filter(book_id=book_id)
        # Если отзывов нет, возвращаем None
        if not reviews.exists():
            return None
        # Вычисляем сумму всех рейтингов
        total_rating = sum(review.rating for review in reviews)
        # Вычисляем средний рейтинг
        average_rating = total_rating / reviews.count()
        return average_rating

    @staticmethod
    def is_popular(book_id, threshold=4):
        # Вычисляем средний рейтинг книги
        average_rating = BookService.calculate_average_rating(book_id)
        # Если средний рейтинг не вычислен (нет отзывов), возвращаем False
        if average_rating is None:
            return None
        # Проверяем, является ли книга популярной (средний рейтинг >= порогу)
        return average_rating >= threshold