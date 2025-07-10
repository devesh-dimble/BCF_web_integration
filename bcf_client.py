# bcf_client.py
import requests

class BcfClient:
    def __init__(self, cde_url, bcf_suffix="/opencde-api/bcf/3.0", project_id=None):
        self.cde_url = cde_url
        self.bcf_suffix = bcf_suffix
        self.project_id = project_id
        self.session = requests.Session()
        self.token = None

    def authenticate(self, username, password):
        url = f"{self.cde_url}/Authentication/login"
        payload = {"userName": username, "password": password}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        self.token = response.json().get("token")
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_projects(self):
        url = f"{self.cde_url}/Projects"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_topics(self):
        url = f"{self.cde_url}{self.bcf_suffix}/projects/{self.project_id}/topics"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_comments(self, topic_id):
        url = f"{self.cde_url}{self.bcf_suffix}/projects/{self.project_id}/topics/{topic_id}/comments"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
