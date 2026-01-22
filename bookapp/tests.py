from datetime import date
import shutil

from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from bookapp.forms import BookForm
from bookapp.models import Author, Book


class BookModelTest(TestCase):
    def test_correct_book_without_authors_and_cover(self):
        book = Book.objects.create(
            title="My Book",
            pages=100,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 1),
        )
        book.full_clean()
        self.assertEqual(book.title, "My Book")
        self.assertEqual(book.pages, 100)
        self.assertEqual(book.rating, 3)
        self.assertEqual(book.status, "PE")
        self.assertEqual(book.published_date, date(2020, 1, 1))
        self.assertIsNone(book.read_date)

    def test_incorrect_pages(self):
        book = Book(
            title="My Book",
            pages=0,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 1),
        )
        with self.assertRaises(Exception):
            book.full_clean()

    def test_incorrect_rating(self):
        book = Book(
            title="My Book",
            pages=100,
            rating=6,
            status="PE",
            published_date=date(2020, 1, 1),
        )
        with self.assertRaises(Exception):
            book.full_clean()

    def test_read_date_before_published_date(self):
        book = Book(
            title="My Book",
            pages=100,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 2),
            read_date=date(2020, 1, 1),
        )
        with self.assertRaises(Exception):
            book.full_clean()

    def test_with_author(self):
        author = Author.objects.create(
            name="John",
            last_name="Doe",
        )
        book = Book.objects.create(
            title="My Book",
            pages=100,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 1),
        )
        book.authors.add(author)
        book.full_clean()
        self.assertIn(author, book.authors.all())

    def test_with_cover(self):
        cover = SimpleUploadedFile(
            name="cover.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )
        book = Book(
            title="My Book",
            pages=100,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 1),
            cover_image=cover,
        )
        book.full_clean()
        self.assertEqual(book.cover_image.name, "cover.jpg")


@override_settings(MEDIA_ROOT="test_media")
class BookFormTest(TestCase):
    def test_correct_book_without_authors_and_cover(self):
        form = BookForm(
            {
                "title": "My Book",
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            }
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertEqual(book.title, "My Book")
        self.assertEqual(book.pages, 100)
        self.assertEqual(book.rating, 3)
        self.assertEqual(book.status, "PE")
        self.assertEqual(book.published_date, date(2020, 1, 1))
        self.assertIsNone(book.read_date)
        self.assertFalse(book.authors.exists())
        self.assertFalse(bool(book.cover_image))

    def test_title_more_than_50_characters(self):
        form = BookForm(
            {
                "title": "a" * 51,
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn(
            "The title must be less than 50 characters long", form.errors["title"]
        )

    def test_empty_title(self):
        form = BookForm(
            {
                "title": "",
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("The title is mandatory", form.errors["title"])

    def test_incorrect_pages(self):
        form = BookForm(
            {
                "title": "My Book",
                "pages": 0,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("pages", form.errors)

    def test_incorrect_rating(self):
        form = BookForm(
            {
                "title": "My Book",
                "pages": 100,
                "rating": 10,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_read_date_before_published_date(self):
        form = BookForm(
            {
                "title": "My Book",
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 2),
                "read_date": date(2020, 1, 1),
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("read_date", form.errors)
        self.assertIn(
            "The read date must be after the published date", form.errors["read_date"]
        )

    def test_with_author(self):
        author = Author.objects.create(
            name="John",
            last_name="Doe",
        )
        form = BookForm(
            {
                "title": "My Book",
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
                "authors": [author.id],
            }
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertIn(author, book.authors.all())

    def test_with_cover(self):
        fake_file = SimpleUploadedFile(
            name="cover.jpg",
            content=b"fake-image-content",
            content_type="image/jpeg",
        )
        form = BookForm(
            {
                "title": "My Book",
                "pages": 100,
                "rating": 3,
                "status": "PE",
                "published_date": date(2020, 1, 1),
            },
            {
                "cover_image": fake_file,
            },
        )
        self.assertTrue(form.is_valid())
        book = form.save()
        self.assertEqual(book.cover_image.name, "covers/cover.jpg")
        shutil.rmtree("test_media")


class BookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_admin = User.objects.create_user(
            username="admin", password="admin"
        )
        self.user_other = User.objects.create_user(
            username="other", password="other"
        )

        self.admin_group = Group.objects.create(name="Admin")
        content_type = ContentType.objects.get_for_model(Book)
        add_perm = Permission.objects.get(
            codename="add_book", content_type=content_type
        )
        change_perm = Permission.objects.get(
            codename="change_book", content_type=content_type
        )
        delete_perm = Permission.objects.get(
            codename="delete_book", content_type=content_type
        )
        view_perm = Permission.objects.get(
            codename="view_book", content_type=content_type
        )
        self.admin_group.permissions.add(add_perm, change_perm, delete_perm, view_perm)
        self.user_admin.groups.add(self.admin_group)

        self.book = Book.objects.create(
            title="My Book",
            pages=100,
            rating=3,
            status="PE",
            published_date=date(2020, 1, 1),
        )

    def test_form_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("form")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_form_other(self):
        self.client.login(username="other", password="other")
        url = reverse("form")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_list_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_list_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_edit", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_edit", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_delete_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_delete", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_delete", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_detail_admin(self):
        self.client.login(username="admin", password="admin")
        url = reverse("book_detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_detail_other(self):
        self.client.login(username="other", password="other")
        url = reverse("book_detail", kwargs={"pk": 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
