# Validation method

## Software checks

Run the complete unittest suite with:

~~~sh
PYTHONPATH=src python -m unittest discover -s tests -v
~~~

The parent release report records the observed test count, pass/fail/skip totals, and process exit code. No test result should be inferred from documentation alone.

## Public artifact checks

The preserved Public Submission is checked structurally against the original permitted question IDs and order with tools/validate_submission.py. This check reads no answer labels and does not invoke inference. Its SHA-256 and MD5 are recorded beside the artifact.

Public answer labels are unavailable. Coverage and abstention counts are not accuracy or Penalized Accuracy. This release therefore makes no Public Test accuracy claim.

## Data boundaries

The release source contains synthetic test fixtures only. The training archive is copied only into the Docker build context because the official Docker guide calls for it in the image. Public/private test inputs and labels are excluded from source and Docker context. No prediction is regenerated from Public Test as part of this release.
