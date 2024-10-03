from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Group
from django.contrib.messages import get_messages
from django.contrib import messages
from .forms import FeedbackForm
from .models import Post, Comment

class RegisterViewTests(TestCase):
    
    def setUp(self):
        """Sets up the test environment, creating the 'User' group."""
        self.group, _ = Group.objects.get_or_create(name='User')
    
    def test_register_user_success(self):
        """Tests the successful registration of a new user."""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpassword123'
        })
        # Verifies that the user was created
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.groups.filter(name='User').exists())  # Checks if the user belongs to the group
        self.assertRedirects(response, reverse('home'))
        
    def test_register_user_empty_username(self):
        """Tests user registration with an empty username."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'newuser@example.com',
            'password': 'testpassword123'
        })
        # Verifies that the user count has not changed
        self.assertEqual(User.objects.count(), 0)
        # Captures the messages
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)  # Verifies there is one message
        self.assertEqual(str(messages_list[0]), "Username is mandatory")
        self.assertEqual(response.status_code, 302)  # Verifies redirection

    def test_register_user_existing_username(self):
        """Tests user registration with an existing username."""
        User.objects.create_user(username='existinguser', email='existing@example.com', password='testpassword123')
        response = self.client.post(reverse('register'), {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'password': 'testpassword123'
        })
        # Verifies that the user count has not changed
        self.assertEqual(User.objects.count(), 1)  # Only the first user should exist
        # Captures the messages
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)  # Verifies there is one message
        self.assertEqual(str(messages_list[0]), "Username already in use")
        self.assertEqual(response.status_code, 302)  # Verifies redirection

    def test_register_user_invalid_data(self):
        """Tests registration with invalid data (empty username)."""
        response = self.client.post(reverse('register'), {
            'username': '',
            'email': 'invaliduser@example.com',
            'password': 'testpassword123'
        })
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(response.status_code, 302)  # Verifies redirection
        # Captures the messages
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_list), 1)  # Verifies there is one message
        self.assertEqual(str(messages_list[0]), "Username is mandatory")

        
class LoginViewTests(TestCase):
    def setUp(self):
        """Creates a user for testing."""
        self.username = 'testuser'
        self.password = 'testpassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_success(self):
        """Tests successful login with correct credentials."""
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password
        })
        # Verifies if the user was authenticated
        self.assertEqual(response.status_code, 302)  # Verifies redirection
        self.assertRedirects(response, reverse('home'))  # Verifies redirection to home
        self.assertTrue(response.wsgi_request.user.is_authenticated)  # Verifies if the user is authenticated

    def test_login_invalid_credentials(self):
        """Tests login with invalid credentials."""
        response = self.client.post(reverse('login'), {
            'username': 'invaliduser',
            'password': 'wrongpassword'
        })
        # Verifies if the user was not authenticated
        self.assertEqual(response.status_code, 302)  # Verifies redirection
        self.assertRedirects(response, reverse('login'))  # Verifies redirection to the login page
        
        # Verifies if the error message was added
        messages_list = list(get_messages(response.wsgi_request))
        self.assertTrue(any(msg.message == "Invalid Credentials." for msg in messages_list))

    def test_login_empty_fields(self):
        """Tests login with empty fields."""
        response = self.client.post(reverse('login'), {
            'username': '',
            'password': ''
        })
        # Verifies if the redirection occurs
        self.assertEqual(response.status_code, 302)  # Verifies redirection
        self.assertRedirects(response, reverse('login'))
        
class LogoutViewTests(TestCase):

    def setUp(self):
        """Sets up a user for testing."""
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
    
    def test_logout_view(self):
        """Tests the logout view."""
        # Logs in as the created user
        self.client.login(username='testuser', password='testpassword')
        
        # Verifies that the user is authenticated before logging out
        response = self.client.get(reverse('logout'))  # Calls the logout view

        # Verifies that the user is logged out
        self.assertNotIn('_auth_user_id', self.client.session)

        # Verifies if the redirection was to the home page
        self.assertRedirects(response, reverse('home'))

class CreatePostViewTests(TestCase):

    def setUp(self):
        # Creates a user for testing
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_create_post_view_with_valid_data(self):
        # Logs in the user
        self.client.login(username='testuser', password='testpass')
        
        # Defines the post data
        post_data = {
            'title': 'Test Post',
            'content': 'This is a test post.',
            'image': 'images/unitedfood.png'
        }

        # Makes a POST request to create a post
        response = self.client.post(reverse('new-post'), data=post_data)

        # Verifies if the post was created
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.first().title, 'Test Post')
        self.assertEqual(Post.objects.first().content, 'This is a test post.')

        # Verifies if the redirection occurred correctly
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the success message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Success")

    def test_create_post_view_without_login(self):
        # Makes a POST request without being logged in
        response = self.client.post(reverse('new-post'))

        # Verifies if the response redirects to the login page
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('new-post')}")

class EditPostViewTests(TestCase):

    def setUp(self):
        # Creates a user for testing
        self.author = User.objects.create_user(username='author', password='authorpass')
        self.non_author = User.objects.create_user(username='non_author', password='non_author_pass')
        
        # Creates a post to be edited
        self.post = Post.objects.create(title='Original Title', content='Original content.', author=self.author)

    def test_edit_post_view_as_author(self):
        # Logs in as the post author
        self.client.login(username='author', password='authorpass')
        
        # Defines the edited post data
        post_data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
            'image': 'images/unitedfood.png'
        }

        # Makes a POST request to edit the post
        response = self.client.post(reverse('edit_post', args=[self.post.id]), data=post_data)

        # Verifies if the post was edited correctly
        self.post.refresh_from_db()  # Refreshes the post instance from the database
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.content, 'Updated content.')

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the success message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Success")

    def test_edit_post_view_as_non_author(self):
        # Logs in as a user who is not the post author
        self.client.login(username='non_author', password='non_author_pass')

        # Defines the edited post data
        post_data = {
            'title': 'Attempted Title Change',
            'content': 'This change should not happen.',
            'image': 'images/unitedfood.png'
        }

        # Attempts to edit the post
        response = self.client.post(reverse('edit_post', args=[self.post.id]), data=post_data)

        # Verifies if the post was not edited
        self.post.refresh_from_db()  # Refreshes the post instance from the database
        self.assertEqual(self.post.title, 'Original Title')

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the error message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "No Permission")

    def test_edit_post_view_as_superuser(self):
        # Creates a superuser for testing
        superuser = User.objects.create_superuser(username='superuser', password='superpass')

        # Logs in as superuser
        self.client.login(username='superuser', password='superpass')

        # Defines the edited post data
        post_data = {
            'title': 'Superuser Title Change',
            'content': 'This change should be allowed by superuser.',
            'image': 'images/unitedfood.png'
        }

        # Makes a POST request to edit the post
        response = self.client.post(reverse('edit_post', args=[self.post.id]), data=post_data)

        # Verifies if the post was edited correctly
        self.post.refresh_from_db()  # Refreshes the post instance from the database
        self.assertEqual(self.post.title, 'Superuser Title Change')

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the success message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Success")

class DeletePostViewTests(TestCase):

    def setUp(self):
        # Creates an author user and a non-author user
        self.author = User.objects.create_user(username='author', password='authorpass')
        self.non_author = User.objects.create_user(username='non_author', password='non_author_pass')

        # Creates a post to be deleted
        self.post = Post.objects.create(title='Post to be deleted', content='This post will be deleted.', author=self.author)

    def test_delete_post_view_as_author(self):
        # Logs in as the post author
        self.client.login(username='author', password='authorpass')

        # Makes a POST request to delete the post
        response = self.client.post(reverse('delete_post', args=[self.post.id]))

        # Verifies if the post was deleted
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the success message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Success")  # Success message

    def test_delete_post_view_as_non_author(self):
        # Logs in as a user who is not the post author
        self.client.login(username='non_author', password='non_author_pass')

        # Attempts to delete the post
        response = self.client.post(reverse('delete_post', args=[self.post.id]))

        # Verifies if the post was not deleted
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the error message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "No Permission")

    def test_delete_post_view_as_superuser(self):
        # Creates a superuser for testing
        superuser = User.objects.create_superuser(username='superuser', password='superpass')

        # Logs in as superuser
        self.client.login(username='superuser', password='superpass')

        # Makes a POST request to delete the post
        response = self.client.post(reverse('delete_post', args=[self.post.id]))

        # Verifies if the post was deleted
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

        # Verifies if the response redirects to the posts page
        self.assertRedirects(response, reverse('posts'))

        # Verifies if the success message was added
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), "Success")  # Success message

    def test_delete_post_view_get_request(self):
        # Logs in as the post author
        self.client.login(username='author', password='authorpass')

        # Makes a GET request to check the delete confirmation page
        response = self.client.get(reverse('delete_post', args=[self.post.id]))

        # Verifies if the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Verifies if the post is in the context
        self.assertContains(response, self.post.title)
    
class PostListViewTests(TestCase):
    def setUp(self):
        # Creates a user to be the author of the posts
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Creates test posts
        Post.objects.create(title='First Post', content='Content of the first post', author=self.user)
        Post.objects.create(title='Second Post', content='Content of the second post', author=self.user)

    def test_posts_view_status_code(self):
        """Tests if the 'posts' view returns a status code of 200 (OK)."""
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)

    def test_posts_view_template_used(self):
        """Tests if the 'posts' view uses the correct template."""
        response = self.client.get(reverse('posts'))
        self.assertTemplateUsed(response, 'blog/posts.html')

    def test_posts_view_list_all_posts(self):
        """Tests if the 'posts' view lists all the posts."""
        response = self.client.get(reverse('posts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First Post')
        self.assertContains(response, 'Second Post')
        self.assertEqual(len(response.context['posts']), 2)

class PostDetailViewTest(TestCase):

    def setUp(self):
        """Sets up the necessary data for the tests, including a user and a post."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(title='Test Post', content='Test content', author=self.user)

    def test_post_detail_view_template_used(self):
        """Tests if the 'post_detail' view uses the correct template when the user is logged in."""
        self.client.login(username='testuser', password='12345')  # Logs in with the test user
        url = reverse('post_detail', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)  # Verifies if the response has status code 200
        self.assertTemplateUsed(response, 'blog/post_detail.html')  # Verifies if the correct template was used

    def test_post_detail_view_shows_comments(self):
        """Tests if the post's comments are correctly displayed on the post detail page."""
        self.client.login(username='testuser', password='12345')
        comment = Comment.objects.create(post=self.post, author=self.user, content="Test comment")
        url = reverse('post_detail', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertContains(response, "Test comment")  # Verifies if the created comment appears on the page

    def test_post_detail_view_can_add_comment(self):
        """Tests if a comment can be correctly added to the post."""
        self.client.login(username='testuser', password='12345')
        url = reverse('post_detail', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'comment': 'Another test comment'})
        self.assertEqual(Comment.objects.count(), 1)  # Verifies if a comment was added
        self.assertRedirects(response, reverse('post_detail', kwargs={'post_id': self.post.id}))  # Verifies redirection
        
class AddCommentViewTest(TestCase):
    def setUp(self):
        """Sets up a test user and a post."""
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.post = Post.objects.create(title='Test Post', content='Test content', author=self.user)

    def test_add_comment_redirects_when_not_logged_in(self):
        """Tests if the view correctly redirects to the login page when the user is not logged in."""
        url = reverse('add_comment', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'content': 'Test comment'})
        self.assertRedirects(response, '/login/?next=' + url)

    def test_add_comment_with_valid_content(self):
        """Tests if the comment is correctly added when the content is valid."""
        self.client.login(username='testuser', password='12345')
        url = reverse('add_comment', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'content': 'This is a valid comment!'})

        # Verifies if the comment was added
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'This is a valid comment!')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

        # Verifies if there was a redirection to the 'posts' page
        self.assertRedirects(response, reverse('posts'))

    def test_add_comment_with_empty_content(self):
        """Tests if the view does not allow adding empty comments."""
        self.client.login(username='testuser', password='12345')
        url = reverse('add_comment', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'content': ''})

        # Verifies if no comment was added
        self.assertEqual(Comment.objects.count(), 0)

        # Verifies if there was a redirection to the 'posts' page
        self.assertRedirects(response, reverse('posts'))

    def test_add_comment_with_empty_content_shows_error_message(self):
        """Tests if an error message is displayed when trying to add an empty comment."""
        self.client.login(username='testuser', password='12345')
        url = reverse('add_comment', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'content': ''}, follow=True)

        # Verifies if the error message was displayed
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Comment content cannot be empty.')

    def test_add_comment_shows_success_message(self):
        """Tests if the success message is displayed when adding a valid comment."""
        self.client.login(username='testuser', password='12345')
        url = reverse('add_comment', kwargs={'post_id': self.post.id})
        response = self.client.post(url, {'content': 'This is a valid comment!'}, follow=True)

        # Verifies if the success message was displayed
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Comment added successfully!')

class AboutUsViewTest(TestCase):
    def test_about_us_view_status_code(self):
        """Tests if the 'About Us' view returns a status of 200 (OK)."""
        response = self.client.get(reverse('about-us'))
        self.assertEqual(response.status_code, 200)

    def test_about_us_view_template_used(self):
        """Tests if the 'About Us' view uses the correct template."""
        response = self.client.get(reverse('about-us'))
        self.assertTemplateUsed(response, 'blog/about_us.html')

class SearchPostsViewTest(TestCase):
    def setUp(self):
        """Initial setup for the tests, creates a user and some posts."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        # Creates posts for the test
        Post.objects.create(title='Delicious Pasta Recipe', content='How to make pasta...', author=self.user)
        Post.objects.create(title='Tasty Pizza', content='Pizza is great!', author=self.user)
        Post.objects.create(title='Healthy Salad', content='Salad is good for health', author=self.user)

    def test_search_posts_view_with_results(self):
        """Tests if the search returns the correct posts when there are results."""
        response = self.client.get(reverse('search_posts'), {'query': 'Pasta'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delicious Pasta Recipe')
        self.assertNotContains(response, 'Tasty Pizza')
        self.assertNotContains(response, 'Healthy Salad')

    def test_search_posts_view_no_results(self):
        """Tests if the search returns a page with no results when the query finds nothing."""
        response = self.client.get(reverse('search_posts'), {'query': 'Burger'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No posts found')  # Adjust if there is a "no results" message
        self.assertNotContains(response, 'Delicious Pasta Recipe')
        self.assertNotContains(response, 'Tasty Pizza')

    def test_search_posts_view_empty_query(self):
        """Tests the behavior of the view when the query is empty."""
        response = self.client.get(reverse('search_posts'), {'query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delicious Pasta Recipe')
        self.assertContains(response, 'Tasty Pizza')
        self.assertContains(response, 'Healthy Salad')

    def test_search_posts_view_without_login(self):
        """Tests if the view redirects to the login page if the user is not logged in."""
        self.client.logout()  # Logs out the user
        response = self.client.get(reverse('search_posts'), {'query': 'Pasta'})
        self.assertRedirects(response, '/login/?next=%2Fsearch%2F%3Fquery%3DPasta')  # Verifies redirection to login

class FeedbackViewTest(TestCase):
    def setUp(self):
        """Initial setup for the tests: creates a user and logs in."""
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_feedback_view_get(self):
        """Tests if the view renders the form correctly on a GET request."""
        response = self.client.get(reverse('feedback'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], FeedbackForm)  # Verifies if the form is in the context
        self.assertTemplateUsed(response, 'blog/feedback.html')  # Verifies if the correct template was used

    def test_feedback_view_without_login(self):
        """Tests if the view redirects to the login page if the user is not logged in."""
        self.client.logout()  # Logs out the user
        response = self.client.get(reverse('feedback'))
        self.assertRedirects(response, '/login/?next=/feedback/') 