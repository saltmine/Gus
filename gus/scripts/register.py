"""
Tasks for registering data with Gus
"""


def build(project_name, branch_name, revision_id, code_path,
    venv_path):
  """Register a release candidate with the gus system.  Jenkins should call
  this after a successful build
  """
  from gus.models import project
  from gus.models import release_candidate
  project_id = project.create_or_get(project_name)
  release_candidate.create(project_id, branch_name, revision_id, code_path,
      venv_path)
