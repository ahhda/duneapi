"""
A simple framework for interacting with not officially supported DuneAnalytics API
Code adapted from https://github.com/itzmestar/duneanalytics
at commit bdccd5ba543a8f3679e2c81e18cee846af47bc52
"""
from __future__ import annotations

import os
import time

from dotenv import load_dotenv
from requests import Session, Response

from .logger import set_log
from .response import (
    validate_and_parse_dict_response,
    validate_and_parse_list_response,
)
from .types import DuneRecord, QueryResults, DuneQuery, Post

log = set_log(__name__)

BASE_URL = "https://dune.xyz"
GRAPH_URL = "https://core-hsr.dune.xyz/v1/graphql"


class DuneAPI:
    """
    Acts as API client for dune.xyz. All requests to be made through this class.
    """

    def __init__(
        self,
        username: str,
        password: str,
        max_retries: int = 2,
        ping_frequency: int = 5,
    ):
        """
        Initialize the object
        :param username: username for dune.xyz
        :param password: password for dune.xyz
        """
        self.csrf = None
        self.auth_refresh = None
        self.token = None
        self.username = username
        self.password = password
        self.session = Session()
        self.max_retries = max_retries
        self.ping_frequency = ping_frequency
        headers = {
            "origin": BASE_URL,
            "sec-ch-ua": "empty",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "dnt": "1",
        }
        self.session.headers.update(headers)

    @staticmethod
    def new_from_environment() -> DuneAPI:
        """Initialize & authenticate a Dune client from the current environment"""
        load_dotenv()
        dune = DuneAPI(
            os.environ["DUNE_USER"],
            os.environ["DUNE_PASSWORD"],
        )
        # loging and fetch_auth token don't really need to be here
        dune.login()
        return dune

    def login(self) -> None:
        """Attempt to log in to dune.xyz & get the token"""
        login_url = BASE_URL + "/auth/login"
        csrf_url = BASE_URL + "/api/auth/csrf"
        auth_url = BASE_URL + "/api/auth"

        # fetch login page
        self.session.get(login_url)

        # get csrf token
        self.session.post(csrf_url)
        self.csrf = self.session.cookies.get("csrf")

        # try to log in
        form_data = {
            "action": "login",
            "username": self.username,
            "password": self.password,
            "csrf": self.csrf,
            "next": BASE_URL,
        }

        self.session.post(auth_url, data=form_data)
        self.auth_refresh = self.session.cookies.get("auth-refresh")

    def fetch_auth_token(self) -> None:
        """Fetch authorization token for the user"""
        session_url = BASE_URL + "/api/auth/session"

        response = self.session.post(session_url)
        if response.status_code == 200:
            self.token = response.json().get("token")
        else:
            # TODO - should probably raise a different exception here.
            raise SystemExit(response)

    def refresh_auth_token(self) -> None:
        """Set authorization token for the user"""
        self.fetch_auth_token()
        self.session.headers.update({"authorization": f"Bearer {self.token}"})

    def initiate_query(self, query: DuneQuery) -> bool:
        """
        Initiates a new query.
        """
        post_data = query.upsert_query_post()
        response = self.post_dune_request(post_data)
        validate_and_parse_dict_response(response, post_data.key_map)
        # Return True to indicate method was success.
        return True

    def execute_query(self, query: DuneQuery) -> str:
        """Executes query at query_id"""
        post_data = query.execute_query_post()
        response = self.post_dune_request(post_data)
        validate_and_parse_dict_response(response, post_data.key_map)
        return str(response.json()["data"]["execute_query"]["job_id"])

    def get_results(self, job_id: str) -> list[DuneRecord]:
        """Fetch the result for a query by id"""
        queue_position_post = DuneQuery.get_queue_position(job_id)

        queue_position = self.post_dune_request(queue_position_post)
        while queue_position.json()["data"]["jobs_by_pk"] is not None:
            log.debug("Waiting for queue to end...")
            time.sleep(self.ping_frequency)
            queue_position = self.post_dune_request(queue_position_post)

        find_result_post = DuneQuery.find_result_by_job(job_id)
        response = self.post_dune_request(find_result_post)
        parsed_response = validate_and_parse_list_response(
            response, find_result_post.key_map
        )
        return QueryResults(parsed_response).data

    def post_dune_request(self, post: Post) -> Response:
        """
        Refresh Authorization Token and posts query.
        Parses response for errors by key and raises runtime error if they exist.
        Only successful responses are returned
        :param post: JSON content and validation parameters for request
        :return: response in json format
        """
        self.refresh_auth_token()
        log.debug(f"Posting Dune Request {post.data}")
        response = self.session.post(GRAPH_URL, json=post.data)
        log.debug(f"Received Response {response.json()}")

        return response

    def execute_and_await_results(self, query: DuneQuery) -> list[DuneRecord]:
        """
        Executes query by ID and awaits completion.
        :return: parsed list of dict records returned from query
        """
        job_id = self.execute_query(query)
        data_set = self.get_results(job_id)
        log.info(f"got {len(data_set)} records from last query")
        return data_set

    def fetch(self, query: DuneQuery) -> list[DuneRecord]:
        """
        Pushes new query, executes and awaiting query completion
        :return: list query records as dictionaries
        """
        log.info(f"Fetching {query.name} on {query.network}...")
        self.initiate_query(query)
        for _ in range(0, self.max_retries):
            try:
                return self.execute_and_await_results(query)
            except RuntimeError as err:
                log.warning(
                    f"failed with {err}. Re-establishing connection and trying again"
                )
                self.login()
                self.refresh_auth_token()
        raise Exception(f"Maximum retries ({self.max_retries}) exceeded")
