#!/usr/bin/env python

import click
from prettytable import PrettyTable
import requests
import os
from urllib3.exceptions import InsecureRequestWarning
from utils import _colorize_status, _get_all_data

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab-01.ppm.example.com")
HEADERS = {"Content-type": "application/json", "Accept": "application/json"}


class GitLab(object):
    def __init__(self):
        payload = {
            "username": os.environ["GITLAB_USERNAME"],
            "password": os.environ["GITLAB_PASSWORD"],
            "grant_type": "password",
        }
        # Login and obtain an auth token for further use.
        response = requests.post(
            f"{GITLAB_URL}/oauth/token", json=payload, headers=HEADERS, verify=False
        )
        response.raise_for_status()
        
        self.token = response.json()["access_token"]


# TODO: This needs to accept a click context and instantiate a GitLab object within that context
# in order to handle authentication between the other commands.
@click.group()
@click.pass_context
def gitlab(ctx):
    """
    Retrieve GitLab project data and retry pripeline jobs
    """
    if "GITLAB_USERNAME" not in os.environ or "GITLAB_PASSWORD" not in os.environ:
        click.secho(
            "ERROR: You must specify GITLAB_USERNAME and GITLAB_PASSWORD as environment variables.",
            fg="red"
        )
        exit(1)
    
    # TODO: Instantiate the GitLab class and save it to the click context.
    ctx.obj = GitLab()

# TODO: This function needs to accept a GitLab object instance to obtaining the authorization token.
@click.command()
@click.pass_obj
@click.option(
    "--all/--pipelines-only",
    default=True,
    show_default=False,
    required=False,
    help="Display all projects or just those with pipelines (default: all projects are shown)",
)
def projects(gitlab_obj, all):
    """
    Display a list of projects in tabular format
    """
    table = PrettyTable()
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {gitlab_obj.token}"

    # Get all GitLab projects.
    try:
        project_list = _get_all_data(
            url=f"{GITLAB_URL}/api/v4/projects", headers=headers
        )
    except Exception as e:
        click.secho(f"ERROR: Unable to get GitLab projects: {e}", fg="red")
        exit(1)
    
    table.field_names = ["ID", "Name", "Group", "URL", "Pipeline Status"]
    table.align = "l"
    for proj in project_list:
        add_row = True
        
        row = [
            proj["id"],
            proj["name"],
            proj["name_with_namespace"].split("/")[0].strip(),
            proj["web_url"],
        ]
        try:
            response = requests.get(
                f"{GITLAB_URL}/api/v4/projects/{proj['id']}/pipelines", 
                params={"ref": proj["default_branch"]},
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
        except Exception as e:
            click.secho(
                f"WARNING: Unable to get pipeline list for project {proj ['name']}: {e}",
                fg="yellow",
            )
            continue

        pipeline_list = response.json()
        if len(pipeline_list) > 0:
            # Check the _first_ pipeline in the list (sorted in descending order).
            # Pipelines that have failed will display red text whereas success is
            # displayed as green.
            row.append(_colorize_status(pipeline_list[0]["status"]))
        else:
            row.append("N/A")
        
        if not all:
            # Get the pipeline details for the project.
            # Only check the default branch as that is what we deploy from.
            if len(pipeline_list) == 0:
                add_row = False
        
        if add_row:
            table.add_row(row)
    
    click.echo(table)


@click.group()
def pipelines():
    """
    Operate on CI/CD pipelines
    """
    pass


# TODO: This function needs to accept a GitLab object instance to obtaining the authorization token.
@click.command()
@click.pass_obj
@click.option(
    "--all/--latest",
    default=True,
    show_default=False,
    required=False,
    help="Show all pipelines or just the latest",
)
@click.option(
    "--project",
    required=True,
    type=int,
    help="Project ID for which pipelines will be listed",
)
def list_pipelines(gitlab_obj, all, project):
    """
    List pipelines for a given project
    """
    table = PrettyTable()
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {gitlab_obj.token}"
    params = {}

    # Get the default branch from the project.
    try:
        response = requests.get(
            f"{GITLAB_URL}/api/v4/projects/{project}", headers=headers, verify=False
        )
        response.raise_for_status()
    except Exception as e:
        click.secho(
            f"ERROR: Failed to get project details for {project}: {e}", fg="red"
        )
        exit(1)
    
    project_dict = response.json()
    params["ref"] = project_dict["default_branch"]
    
    # Get the pipelines for a given project.
    try:
        pipelines_list = _get_all_data(
            url=f"{GITLAB_URL}/api/v4/projects/{project}/pipelines", 
            params=params, 
            headers=headers,
        )
    except Exception as e:
        click.secho(
            f"ERROR: Failed to load pipelines for {project}: {e}", fg="red"
        )
        exit(1)

    table.field_names = [
        "ID",
        "Branch",
        "Started At",
        "Finished At",
        "URL",
        "Status",
    ]
    table.align = "l"

    for pipeline in pipelines_list:
        try:
            # Fetch _all_ of the pipeline details to get start and finish times.
            response = requests.get(
                f"{GITLAB_URL}/api/v4/projects/{project}/pipelines/{pipeline['id']}",
                headers=headers,
                verify=False,
            )
            response.raise_for_status()
        except Exception as e:
            click.secho(
                f"WARNING: Unable to get pipeline details for {pipeline}: {e}", fg="yellow"
            )
            continue

        pipeline_details = response.json()
        table.add_row(
            [
                pipeline_details["id"],
                pipeline_details["ref"],
                pipeline_details["started_at"],
                pipeline_details["finished_at"],
                pipeline_details["web_url"],
                _colorize_status(pipeline_details["status"]),
            ]
        )
        
        if not all:
            # The first entry will be latest (since it's sorted in desc order).
            break

    click.echo(table)


# TODO: This function needs to accept a GitLab object instance to obtaining the authorization token.
@click.command()
@click.pass_obj
@click.option(
    "--project",
    required=True,
    type=int,
    help="Project ID for which containing pipeline to be retried",
)
@click.option("--pipeline", required=True, type=int, help="Pipeline ID to retry")
def retry_pipeline(gitlab_obj, project, pipeline):
    """
    Retry a given pipeline job
    """
    headers = HEADERS.copy()
    headers["Authorization"] = f"Bearer {gitlab_obj.token}"

    try:
        response = requests.post(
            f"{GITLAB_URL}/api/v4/projects/{project}/pipelines/{pipeline}/retry",
            headers=headers,
            verify=False,
        )
        response.raise_for_status()
    except Exception as e:
        click.secho(
            f"ERROR: Failed to retry pipeline {pipeline} for project {project}: {e}",
            fg="red",
        )
        exit(1)

    click.secho(
        f"INFO: Pipeline {pipeline} in a project {project} has been successfully retried.",
        fg="green",
    )


gitlab.add_command(projects)
gitlab.add_command(pipelines)

pipelines.add_command(list_pipelines, name="list")
pipelines.add_command(retry_pipeline, name="retry")

if __name__ == "__main__":
    gitlab()
