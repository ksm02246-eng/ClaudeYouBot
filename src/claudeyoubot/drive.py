"""Step 6: upload the generated files to a Google Drive folder."""

from __future__ import annotations

from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _credentials(credentials_file: str, token_file: str):
    """OAuth client secrets or a service-account key, whichever the file holds."""
    import json

    from google.oauth2 import service_account

    info = json.loads(Path(credentials_file).read_text())
    if info.get("type") == "service_account":
        return service_account.Credentials.from_service_account_info(info, scopes=SCOPES)

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    creds = None
    if Path(token_file).exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
        creds = flow.run_local_server(port=0)
        Path(token_file).write_text(creds.to_json())
    return creds


def upload_folder(local_dir: Path, folder_id: str, credentials_file: str,
                  token_file: str = "token.json") -> list[str]:
    """Create a subfolder named after `local_dir` inside `folder_id` and upload every file."""
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    service = build("drive", "v3", credentials=_credentials(credentials_file, token_file))
    sub = service.files().create(
        body={"name": local_dir.name, "mimeType": "application/vnd.google-apps.folder",
              "parents": [folder_id]},
        fields="id",
    ).execute()
    links = []
    for path in sorted(p for p in local_dir.iterdir() if p.is_file()):
        f = service.files().create(
            body={"name": path.name, "parents": [sub["id"]]},
            media_body=MediaFileUpload(str(path), resumable=True),
            fields="id, webViewLink",
        ).execute()
        links.append(f.get("webViewLink", f["id"]))
    return links
