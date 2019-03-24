from unittest import TestCase
from unittest.mock import patch, MagicMock, ANY

from requests.exceptions import RequestException

import dakara_server


class ServerHTTPConnectionTestCase(TestCase):
    """Test the HTTP connection with a server
    """
    def setUp(self):
        # create a token
        self.token = "token value"

        # create a server address
        self.address = "www.example.com"

        # create a server URL
        self.url = "http://www.example.com/api/"

        # create a login and password
        self.login = "test"
        self.password = "test"

        # create a ServerHTTPConnection instance
        self.dakara_server = dakara_server.ServerHTTPConnection({
            'address': self.address,
            'login': self.login,
            'password': self.password,
        })

    def test_init(self):
        """Test the created object
        """
        self.assertEqual(self.dakara_server.server_url, self.url)
        self.assertEqual(self.dakara_server.login, self.login)
        self.assertEqual(self.dakara_server.password, self.password)
        self.assertIsNone(self.dakara_server.token)

    @patch('dakara_server.requests.post')
    def test_send_request_successful(self, mock_post):
        """Test to send a request with the generic method
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        self.dakara_server.send_request(
            'post',
            self.url,
            data={'content': 'test'},
            message_on_error='error message'
        )

        # assert the call
        mock_post.assert_called_with(
            self.url,
            headers={'Authorization': 'Token token value'},
            data={'content': 'test'}
        )

    def test_send_request_error_method(self):
        """Test that a wrong method name fails for a generic request
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        with self.assertRaises(ValueError):
            with self.assertLogs("dakara_server", "DEBUG"):
                self.dakara_server.send_request(
                    'invalid',
                    self.url,
                    data={'content': 'test'},
                    message_on_error='error message'
                )

    @patch('dakara_server.requests.post')
    def test_send_request_error_network(self, mock_post):
        """Test to send a request when there is a network error
        """
        # set the token
        self.dakara_server.token = self.token

        # mock the response of the server
        mock_post.side_effect = RequestException()

        # call the method
        with self.assertLogs("dakara_server", "DEBUG"):
            self.dakara_server.send_request(
                'post',
                self.url,
                data={'content': 'test'},
                message_on_error='error message'
            )

    @patch('dakara_server.requests.get')
    def test_get(self, mock_get):
        """Test the get method
        """
        # set the token
        self.dakara_server.token = self.token

        # mock the response
        response = MagicMock()
        response.data = "data"
        mock_get.return_value = response

        # call the method
        response_obtained = self.dakara_server.get(
            self.url,
        )

        # assert the call
        mock_get.assert_called_with(
            self.url,
            headers=ANY,
        )

        # assert the result
        self.assertEqual(response_obtained.data, 'data')

    @patch('dakara_server.requests.post')
    def test_post(self, mock_post):
        """Test the post method
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        self.dakara_server.post(
            self.url,
            data={'content': 'content'}
        )

        # assert the call
        mock_post.assert_called_with(
            self.url,
            headers=ANY,
            data={'content': 'content'}
        )

    @patch('dakara_server.requests.patch')
    def test_patch(self, mock_patch):
        """Test the patch method
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        self.dakara_server.patch(
            self.url,
            data={'content': 'content'}
        )

        # assert the call
        mock_patch.assert_called_with(
            self.url,
            headers=ANY,
            data={'content': 'content'}
        )

    @patch('dakara_server.requests.put')
    def test_put(self, mock_put):
        """Test the put method
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        self.dakara_server.put(
            self.url,
            data={'content': 'content'}
        )

        # assert the call
        mock_put.assert_called_with(
            self.url,
            headers=ANY,
            data={'content': 'content'}
        )

    @patch('dakara_server.requests.post')
    def test_authenticate_successful(self, mock_post):
        """Test a successful authentication with the server
        """
        # mock the response of the server
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {'token': self.token}

        # pre assertions
        self.assertFalse(self.dakara_server.token)

        # call the method
        with self.assertLogs("dakara_server", "DEBUG"):
            self.dakara_server.authenticate()

        # call assertions
        mock_post.assert_called_with(
            self.url + "token-auth/",
            data={
                'username': self.login,
                'password': self.password,
            }
        )

        # post assertions
        self.assertTrue(self.dakara_server.token)
        self.assertEqual(self.dakara_server.token, self.token)

    @patch('dakara_server.requests.post')
    def test_authenticate_error_network(self, mock_post):
        """Test a network error when authenticating
        """
        # mock the response of the server
        mock_post.side_effect = RequestException()

        # call the method
        with self.assertRaises(dakara_server.NetworkError):
            with self.assertLogs("dakara_server", "DEBUG"):
                self.dakara_server.authenticate()

    @patch('dakara_server.requests.post')
    def test_authenticate_error_authentication(self, mock_post):
        """Test an authentication error when authenticating
        """
        # mock the response of the server
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 400

        # call the method
        with self.assertRaises(dakara_server.AuthenticationError):
            with self.assertLogs("dakara_server", "DEBUG"):
                self.dakara_server.authenticate()

    @patch('dakara_server.requests.post')
    def test_authenticate_error_other(self, mock_post):
        """Test a server error when authenticating
        """
        # mock the response of the server
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 999
        mock_post.return_value.test = 'error'

        # call the method
        with self.assertRaises(dakara_server.AuthenticationError):
            with self.assertLogs("dakara_server", "DEBUG"):
                self.dakara_server.authenticate()

    def test_get_token_header(self):
        """Test the helper to get token header
        """
        # set the token
        self.dakara_server.token = self.token

        # call the method
        result = self.dakara_server.get_token_header()

        # call assertions
        self.assertEqual(result, {
            'Authorization': 'Token ' + self.token
        })


class AuthenticatedTestCase(TestCase):
    """Test the `authenticated` decorator
    """
    class Authenticated:
        def __init__(self):
            self.token = None

        @dakara_server.authenticated
        def dummy(self):
            pass

    def test_authenticated_sucessful(self):
        """Test the authenticated decorator when token is set
        """
        instance = self.Authenticated()

        # set the token
        instance.token = True

        # call a protected method
        instance.dummy()

    def test_authenticated_error(self):
        """Test the authenticated decorator when token is not set
        """
        instance = self.Authenticated()

        # call a protected method
        with self.assertRaises(dakara_server.AuthenticationError):
            instance.dummy()
