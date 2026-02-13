"""MockFactory API Client"""
import os
import requests
from typing import Optional
from .resources import VPCResource, LambdaResource, DynamoDBResource, SQSResource, StorageResource
from .exceptions import APIError, AuthenticationError


class MockFactory:
    """
    MockFactory API Client

    Args:
        api_key: MockFactory API key (or set MOCKFACTORY_API_KEY env var)
        api_url: API base URL (default: https://api.mockfactory.io/v1)
        environment_id: Optional environment ID to scope all operations

    Example:
        >>> mf = MockFactory(api_key="mf_...")
        >>> vpc = mf.vpc.create(cidr_block="10.0.0.0/16")
        >>> print(vpc.id)
        vpc-abc123
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://api.mockfactory.io/v1",
        environment_id: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("MOCKFACTORY_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key= or set MOCKFACTORY_API_KEY env var"
            )

        self.api_url = api_url.rstrip("/")
        self.environment_id = environment_id
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": f"mocklib-python/0.1.0",
        })

        # Initialize resource clients
        self.vpc = VPCResource(self)
        self.lambda_function = LambdaResource(self)
        self.dynamodb = DynamoDBResource(self)
        self.sqs = SQSResource(self)
        self.storage = StorageResource(self)

    def request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """
        Make authenticated request to MockFactory API

        Args:
            method: HTTP method (GET, POST, DELETE, etc.)
            endpoint: API endpoint (e.g., "/aws/vpc")
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            APIError: If request fails
        """
        url = f"{self.api_url}{endpoint}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=json,
                params=params,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code

            if status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif status_code == 429:
                raise APIError("Rate limit exceeded")
            elif status_code >= 500:
                raise APIError(f"Server error: {e.response.text}")
            else:
                raise APIError(f"API error ({status_code}): {e.response.text}")

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}")

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """GET request"""
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, json: Optional[dict] = None) -> dict:
        """POST request"""
        return self.request("POST", endpoint, json=json)

    def delete(self, endpoint: str) -> dict:
        """DELETE request"""
        return self.request("DELETE", endpoint)
