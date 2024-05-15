import os
from util import get_logger, get_submissions, get_submission_dir, get_trino_creds, get_runtime_env, get_changed_files
from trino.dbapi import connect
from trino.auth import BasicAuthentication

logger = get_logger()
submission_dir = get_submission_dir()
testing = get_runtime_env()
trino_host, trino_port, trino_username, trino_password, trino_catalog, trino_schema = get_trino_creds()


assignment_schema = os.environ.get('ASSIGNMENT_SCHEMA')
create_sql = f"CREATE SCHEMA IF NOT EXISTS {assignment_schema}"
use_sql = f"USE {assignment_schema}"



def init_trino():
  try:
    conn = connect(
        host=trino_host,
        port=trino_port,
        user=trino_username,
        catalog=trino_catalog,
        schema=trino_schema,
        auth=BasicAuthentication(trino_username, trino_password),
    )
    cur = conn.cursor()
    cur.execute(create_sql)
    return True, 'Success'
  except Exception as e:
    error_message = f"Failed to initalize Trino! Error message: {str(e)}. You may need to wait a couple minutes and then try again."
    logger.info(error_message)
    return False, error_message


def execute_sql(query):
  try:
    conn = connect(
        host=trino_host,
        port=trino_port,
        user=trino_username,
        catalog=trino_catalog,
        schema=trino_schema,
        auth=BasicAuthentication(trino_username, trino_password),
    )
    cur = conn.cursor()
    cur.execute(use_sql)
    cur.execute(query)
    return True, 'Success'
  except Exception as e:
    error_message = f'{str(e.message)}'
    return False, error_message


def run_tests(filename, submission):
  passed, results = execute_sql(submission)
  if not passed:
      comment = f'Failed to run `{filename}` ➡️ "{results}"'
      return passed, comment
  return passed, results


def main(submissions: dict, files_to_process: list):
  if not submissions:
    logger.info('WARNING: No submissions found')
    return None
  if not files_to_process:
    logger.info('WARNING: No files specified for processing')
    return None
  
  initalized, results = init_trino()
  if not initalized:
    return False, results
  
  valid_submissions = {}
  comments = []
  for filename, submission in submissions.items():
    file_path = os.path.join(submission_dir, filename)
    if file_path in files_to_process:
      passed, comment = run_tests(filename, submission)
      if not passed:
          comments.append(comment)
      else:
        valid_submissions[filename] = submission
  
  if comments:
    formatted_text = '\n'.join(comments)
    return False, formatted_text
  else:
    return True, "All tests passed successfully"


if __name__ == "__main__":
  submissions = get_submissions(submission_dir)
  files_to_process = get_changed_files()
  passed, comment = main(submissions, files_to_process)
  print(comment)