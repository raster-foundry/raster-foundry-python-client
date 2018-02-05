from future.standard_library import install_aliases  # noqa
install_aliases()  # noqa
import os
import errno

import boto3

from .settings import RV_CPU_JOB_DEF, RV_CPU_QUEUE, DEVELOP_BRANCH


class RasterVisionBatchClient():
    def __init__(self, job_queue=RV_CPU_QUEUE, job_definition=RV_CPU_JOB_DEF,
                 branch_name=DEVELOP_BRANCH, attempts=1):
        """Create a Raster Vision Batch Client

        Args:
            job_queue (str): name of the Batch job queue to run the job in
            job_definition (str): name of the Batch job definition
            branch_name (str): branch of the raster-vision repo to use
            attempts (int): number of attempts for each job
        """

        self.job_queue = job_queue
        self.job_definition = job_definition
        self.branch_name = branch_name
        self.attempts = attempts
        self.batch_client = boto3.client('batch')

    def start_raster_vision_job(self, job_name, command):
        """Start a raster-vision Batch job.

        Args:
            job_name (str): name of the Batch job
            command (str): command to run inside the Docker container

        Returns:
            job_id (str): job_id of job started on Batch
        """
        # `run_script.sh $branch_name $command` downloads a branch of the
        # raster-vision repo and then runs the command.
        job_command = ['run_script.sh', self.branch_name, command]
        job_id = self.batch_client.submit_job(
            jobName=job_name, jobQueue=self.job_queue,
            jobDefinition=self.job_definition,
            containerOverrides={
                'command': job_command
            },
            retryStrategy={
                'attempts': self.attempts
            })['jobId']

        return job_id


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def get_all_paginated(get_page_fn, list_field='results'):
    """Get all objects from a paginated endpoint.

    Args:
        get_page_fn: function that takes a page number and returns results
        list_field: field in the results that contains the list of objects

    Returns:
        List of all objects from a paginated endpoint
    """
    has_next = True
    all_results = []
    page = 0
    while has_next:
        paginated_results = get_page_fn(page)
        has_next = paginated_results.hasNext
        page = paginated_results.page + 1
        for result in getattr(paginated_results, list_field):
            all_results.append(result)

    return all_results
