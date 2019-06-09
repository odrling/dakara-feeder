import logging
import urllib.parse

from path import Path

import requests


logger = logging.getLogger(__name__)


def authenticated(fun):
    """Decorator that ensures the token is set

    It makes sure that the given function is callel once authenticated.

    Args:
        fun (function): function to decorate.

    Returns:
        function: decorated function.
    """

    def call(self, *args, **kwargs):
        if self.token is None:
            raise AuthenticationError("No connection established")

        return fun(self, *args, **kwargs)

    return call


class ServerHTTPConnection:
    """Object representing a HTTP connection with a server

    Args:
        config (dict): config of the server.
    """

    def __init__(self, config):
        try:
            # setting config
            self.server_url = urllib.parse.urlunparse(
                (
                    "https" if config.get("ssl") else "http",
                    config["address"],
                    "/api/",
                    "",
                    "",
                    "",
                )
            )

            # authentication
            self.token = None
            self.login = config["login"]
            self.password = config["password"]

        except KeyError as error:
            raise ValueError(
                "Missing parameter in server config: {}".format(error)
            ) from error

    @authenticated
    def send_request(self, method, *args, message_on_error="", **kwargs):
        """Generic method to send requests to the server

        It adds token header for authentication and takes care of errors.

        Args:
            method (str): name of the HTTP method to use.
            message_on_error (str): message to display in logs in case of
                error. It should describe what the request was about.

        Raises:
            ValueError: if the method is not supported.
        """
        # handle method function
        if not hasattr(requests, method):
            raise ValueError("Method {} not supported".format(method))

        send_method = getattr(requests, method)

        # handle message on error
        if not message_on_error:
            message_on_error = "Unable to request the server"

        try:
            response = send_method(*args, headers=self.get_token_header(), **kwargs)

        except requests.exceptions.RequestException:
            logger.error("{}, network error".format(message_on_error))
            return None

        if response.ok:
            return response

        logger.error(message_on_error)
        logger.debug(
            "Error {code}: {message}".format(
                code=response.status_code, message=display_message(response.text)
            )
        )

        return None

    def get(self, *args, **kwargs):
        """Generic method to get data on server
        """
        return self.send_request("get", *args, **kwargs)

    def post(self, *args, **kwargs):
        """Generic method to post data on server
        """
        return self.send_request("post", *args, **kwargs)

    def put(self, *args, **kwargs):
        """Generic method to put data on server
        """
        return self.send_request("put", *args, **kwargs)

    def patch(self, *args, **kwargs):
        """Generic method to patch data on server
        """
        return self.send_request("patch", *args, **kwargs)

    def authenticate(self):
        """Connect to the server

        The authentication process relies on login/password which gives an
        authentication token. This token is stored in the instance.
        """
        data = {"username": self.login, "password": self.password}

        # connect to the server with login/password
        try:
            response = requests.post(self.server_url + "token-auth/", data=data)

        except requests.exceptions.RequestException as error:
            raise NetworkError(
                ("Network error, unable to talk " "to the server for authentication")
            ) from error

        # manage sucessful connection response
        # store token
        if response.ok:
            self.token = response.json().get("token")
            logger.info("Login to server successful")
            logger.debug("Token: %s", self.token)
            return

        # manage failed connection response
        if response.status_code == 400:
            raise AuthenticationError("Login to server failed, check the config file")

        # manage any other error
        raise AuthenticationError(
            "Unable to connect to server, error {code}: {message}".format(
                code=response.status_code, message=display_message(response.text)
            )
        )

    @authenticated
    def get_token_header(self):
        """Get the connection token as it should appear in the header

        Can be called only once login has been sucessful.

        Returns:
            dict: formatted token.
        """
        return {"Authorization": "Token " + self.token}


class DakaraServer(ServerHTTPConnection):
    def get_songs(self):
        """Retreive the songs of the library containing their path

        Returns:
            list: list of path on the songs.
        """
        url = self.server_url + "library/feeder/retrieve/"
        response = self.get(url)

        # join the directory and the filename
        return [Path(song["directory"]) / song["filename"] for song in response.json()]

    def post_songs_diff(self, added_songs, deleted_songs):
        """Post the lists of added and deleted songs

        Args:
            added_songs (list): list of new songs.
            deleted_songs (list): list of deleted songs.
        """
        url = self.server_url + "library/feeder/"
        data = {"added": added_songs, "deleted": deleted_songs}

        self.post(url, json=data)


def display_message(message, limit=100):
    """Display the 100 first characters of a message
    """
    if len(message) <= limit:
        return message

    return message[: limit - 3].strip() + "..."


class AuthenticationError(Exception):
    """Error raised when authentication fails
    """


class NetworkError(Exception):
    """Error raised when the communication fails during a critical task
    """
