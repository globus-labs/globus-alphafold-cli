import os
import sys
from typing import Optional
import typer
import requests
import globus_sdk

from pathlib import Path
from fair_research_login import NativeClient
from globus_automate_client import create_flows_client


app = typer.Typer()

FLOW_ID = '7c277b80-2cca-42b7-a75d-a970841ee874'
FLOW_SCOPE = 'https://auth.globus.org/scopes/7c277b80-2cca-42b7-a75d-a970841ee874/flow_7c277b80_2cca_42b7_a75d_a970841ee874_user'


def login():
    """Do a login flow to get both an access token and the user's email address.

    Returns:
        str: Access token
        str: email address
    """
    client = NativeClient(client_id='7414f0b4-7d05-4bb6-bb00-076fa3f17cf5')
    tokens = client.login(requested_scopes=['https://auth.globus.org/scopes/a3411a10-da2d-4b44-82f4-d6f5006d6da2/https', 
                                            'openid', 'email'],
                          no_local_server=True, no_browser=True)
    auth_token = tokens['a3411a10-da2d-4b44-82f4-d6f5006d6da2']['access_token']

    auth_authorizer = globus_sdk.AccessTokenAuthorizer(access_token=tokens['auth.globus.org']['access_token'])
    ac = globus_sdk.AuthClient(authorizer=auth_authorizer)

    primary_identity = ac.oauth2_userinfo()
    email_address = primary_identity['email']
    typer.echo(f"Results will be sent to: {email_address}")

    return auth_token, email_address


def upload_file(fasta, auth_token):
    """Upload the file to ALCF

    Args:
        fasta (Path): The Path for a fasta file to upload.
        auth_token (str): Access token to upload the file.
    """
    typer.echo("Uploading FASTA.")
    headers = {'Authorization': f'Bearer {auth_token}'}

    r = requests.put(f'https://g-719d9.fd635.8443.data.globus.org/fasta/{fasta.name}', 
                     data=open(fasta, 'rb'), headers=headers)

    if r.ok:
        typer.echo('OK!')
    else:
        typer.echo('Upload failed!')
        typer.echo(r.text)
        return False
    return True


@app.command()
def run(fasta: Optional[Path] = typer.Option(None)):
    """Start an AlphaFold flow.

    Args:
        fasta (Path): The path to the FASTA file to process.
    """

    # Create a temp fasta file to run with if none is specified
    if not fasta:
        fasta = Path('/tmp/GB98_DM_3.fasta')
        typer.echo(f'No file specified, using {fasta.name}')
        if not fasta.is_file():
            with open(fasta, 'w') as fp:
                fp.write(""">GB98_DM.3 GB98 Deletion Mutation Sequence
        TTYKLILNKQAKEEAIKELVDAGTAEKYFKLIANAKTVEGVWTYKDEIKTFTVTE""")

    # Login for an access token and email address
    auth_token, email_address = login()

    # Send the file to ALCF
    if not upload_file(fasta, auth_token):
        return

    flow_input = {
        "input": {
            "fasta": fasta.name,
            "email": email_address,
        }
    }

    flows_client = create_flows_client()

    flow_action = flows_client.run_flow(FLOW_ID, FLOW_SCOPE, flow_input)
    flow_action_id = flow_action['action_id']
    typer.echo(f"Flow started with run id: {flow_action_id}\nMonitor your flow here: https://app.globus.org/runs/{flow_action_id}")



@app.command()
def status(run_id: str):
    flows_client = create_flows_client()

    flow_action = flows_client.flow_action_status(FLOW_ID, FLOW_SCOPE, run_id)
    flow_status = flow_action['status']
    typer.echo(f'Flow status: {flow_status}')


if __name__ == "__main__":
    app()