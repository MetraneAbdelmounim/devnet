import os

def main(runtime):
    # Set required job name
    runtime.job.name = "example-pyats-jobfile"

    # Build testscript path
    testscript = os.path.join(
        os.path.dirname(__file__),
        "testscript_connect.py"
    )

    # Run task with required task ID
    runtime.tasks.run(
        testscript=testscript,
        taskid="Example-01"
    )