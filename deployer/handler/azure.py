from typing import Optional, Tuple
from urllib.error import HTTPError

import logging

import requests

from ..settings import (
    AZURE_ORGANIZATION_NAME,
    AZURE_PERSONAL_ACCESS_TOKEN,
    AZURE_PROJECT_NAME    
)


from rest_framework import status

LOGGER = logging.getLogger(__name__)
# INFO: le but retrieves tous les bugs à resolved et leur assignee

class AzureHandler:
    _personal_access_token = AZURE_PERSONAL_ACCESS_TOKEN
    _organization_url = f"https://dev.azure.com/{AZURE_ORGANIZATION_NAME}"
    _project_name = AZURE_PROJECT_NAME
    _api_version = "7.1-preview.1"
    
    def __init__(self):
        # TODO check token is still ok
        self.__get_project_id()
        self.__get_project_members()
        self.__get_current_iteration()

    def __get_auth(self) -> Tuple[str, str]:
        """Returns the personal access token in a form that is used in http requests."""
        return "", self._personal_access_token
    
    def __get_project_id(self):
        # TODO mettre l'url de la route
        """"""
        # constructs azure api endpoint with the specified slugs
        endpoint = f"{self._organization_url}/_apis/teams?api-version={self._api_version}"

        # sets the headers and makes the auth request 
        headers = {"Content-Type": "application/json"}
        response = requests.get(endpoint, headers=headers, auth=self.__get_auth())
        
        if response.status_code != status.HTTP_200_OK or response.json()["count"] == 0:
            raise HTTPError(f"the request failed with an error status {response.status_code}")
        
        # filters the response's data to get the teams working on this project
        teams = [team for team in response.json()["value"] if team["projectName"] == self._project_name]
        
        if teams == []:
            raise ValueError("No team found for the specified project name: %s", self._project_name)

        if len(teams) > 1:
            LOGGER.warn("More than one team working on the project, the top first will be taken: %s", teams[0]["name"])
        
        # sets the project_id and team_id from the response fields
        self._project_id = teams[0]["projectId"]
        self._team_id = teams[0]["id"]
        
        # TODO log l'url de l'iteration iterations[0]["url"]

    def __get_project_members(self):
        # constructs azure api endpoint with the specified slugs
        endpoint = f"{self._organization_url}/_apis/projects/{self._project_id}/teams/{self._team_id}/members?api-version={self._api_version}"
        
        # sets the headers and makes the auth request 
        headers = {"Content-Type": "application/json"}
        response = requests.get(endpoint, headers=headers, auth=self.__get_auth())
        
        if response.status_code != status.HTTP_200_OK or response.json()["count"] == 0:
            raise HTTPError(f"the request failed with an error status {response.status_code}")
        
        # retrieves the response's data
        members = response.json()["value"]
        
        # sets the project team members in a dict
        self._normalized_team_members = {member["identity"]["uniqueName"]: member["identity"]["displayName"] for member in members}
    
    def __get_member_id(self, email: str) -> Optional[str]:
        return self._normalized_team_members.get(email, None)
    
    def __get_current_iteration(self):
        """Retrieves the current sprint infos.

        See:
            https://learn.microsoft.com/en-us/rest/api/azure/devops/work/iterations/list?view=azure-devops-rest-7.1&tabs=HTTP
        """
        # constructs the azure api route with the specified slugs
        url = f"{self._organization_url}/{self._project_name}/_apis/work/teamsettings/iterations?$timeframe=current&api-version={self._api_version}"
        
        # requests the data for this url
        response = requests.get(url, headers={}, auth=self.__get_auth())

        if response.status_code != status.HTTP_200_OK or response.json()["count"] == 0:
            raise HTTPError(f"the request failed with an error status {response.status_code}")

        # retrieves the response's data
        iterations = response.json()["value"]
        
        # sets the current_iteration and current_iteration_id from the response fields
        self._current_iteration = int(iterations[0]["name"].split("Sprint ", maxplit="1")[1])
        self._current_iteration_id = iterations[0]["id"]
    
        # TODO log l'url de l'iteration iterations[0]["url"]

    #https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/wiql/query-by-wiql?view=azure-devops-rest-7.1&tabs=HTTP#get-results-of-a-flat-work-item-query.
    def get_resolved_bugs(self):
        #POST https://dev.azure.com/{organization}/{project}/_apis/wit/wiql?api-version=6.1-preview.2
        url = ""
        body = {
            "query": f"""
                SELECT [System.Id], [System.Title]
                FROM WorkItems
                WHERE [System.TeamProject] = '{self._project_name}' AND [System.State] = 'Resolved' AND [System.WorkItemType] = 'Bug'
                ORDER BY [Microsoft.VSTS.Common.Priority] ASC, [System.CreatedDate] DESC
            """
        }
        # todo retrive l'url du bug aussi
        # todo retrive l'assignee du bug aussi
        response = requests.post(url, headers={}, json=body, auth=self.__get_auth())
        
        # todo ça returne pas un 201 created ?
        if response.status_code != 200:
            raise HTTPError(f"the request failed with an error status {response.status_code}")
        
        # todo continuer ici, recup les bugs
        # work_items = response.json()["workItems"]
        pass
    

    

    

    