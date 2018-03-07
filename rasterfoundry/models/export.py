"""An Export is a job to get underlying geospatial data out of Raster Foundry"""

import logging
import time

import requests
from shapely.geometry import mapping, box, MultiPolygon

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel('INFO')


class Export(object):
    def __repr__(self):
        return '<Export - {}>'.format(self.name)

    def __init__(self, export, api):
        """Instantiate a new Export

        Args:
            export (Export): generated Export object from specification
            api (API): api used to make requests on behalf of the export
        """

        self._export = export
        # Someday, exports will have names, but not yet
        self.name = export.id
        self.id = export.id
        self.api = api
        self.export_status = export.exportStatus
        self.path = export.exportOptions.source

    @classmethod
    def poll_export_status(cls,
                           api,
                           export_id,
                           until=['EXPORTED', 'FAILED'],
                           delay=15):
        """Poll the status of an export until it is done

        Note: if you don't include FAILED in the until parameter, polling will continue even
        if the export has failed.

        Args:
            api (API): API to use for requests
            export_id (str): UUID of the export to poll for
            until ([str]): list of statuses to indicate completion
            delay (int): how long to wait between attempts

        Returns:
            Export
        """

        if 'FAILED' not in until:
            logger.warn(
                'Not including FAILED in until can result in states in which this '
                'function will never return. You may have left off FAILED by accident. '
                'If that is the case, you should include FAILED in until and try again.'
            )
        export = api.client.Imagery.get_exports_uuid(uuid=export_id).result()
        while export.exportStatus not in until:
            time.sleep(delay)
            export = api.client.Imagery.get_exports_uuid(
                uuid=export_id).result()
        return Export(export, api)

    @classmethod
    def create_export(cls,
                      api,
                      bbox,
                      zoom,
                      project=None,
                      analysis=None,
                      visibility='PRIVATE',
                      source=None,
                      export_type='S3'):
        """Create an asynchronous export job for a project or analysis

        Only one of project_id or analysis_id should be specified

        Args:
            api (API): API to use for requests
            bbox (str): comma-separated bounding box of region to export
            zoom (int): the zoom level for performing the export
            project (Project): the project to export
            analysis (Analysis): the analysis to export
            visibility (Visibility): what the export's visibility should be set to
            source (str): the destination for the exported files
            exportType (str): one of 'S3', 'LOCAL', or 'DROPBOX'

        Returns:
            ???
        """

        if project is not None and analysis is not None:
            raise ValueError(
                'Ambiguous export target -- only one of project or analysis should '
                'be specified')
        elif project is None and analysis is None:
            raise ValueError(
                'Nothing to export -- one of project or analysis must be specified'
            )
        elif project is not None:
            update_dict = {
                'projectId': project.id,
                'organizationId': project._project.organizationId
            }
        else:
            update_dict = {
                'toolRunId': analysis.id,
                'organizationId': analysis._analysis.organizationId
            }

        box_poly = MultiPolygon([box(*map(float, bbox.split(',')))])

        export_create = {
            'exportOptions': {
                'mask': mapping(box_poly),
                'resolution': zoom
            },
            'projectId': None,
            'exportStatus': 'TOBEEXPORTED',
            'exportType': export_type,
            'visibility': visibility,
            'toolRunId': None,
            'organizationId': None
        }
        export_create.update(update_dict)
        return Export(
            api.client.Imagery.post_exports(Export=export_create).result(),
            api)

    def wait_for_completion(self):
        """Wait until this export succeeds or fails, returning the completed export

        Returns:
            Export
        """
        return self.__class__.poll_export_status(self.api, self.id)

    def download_file_bytes(self):
        """Download the exported file from this export to memory
        """
        fnames = self.api.client.Imagery.get_exports_uuid_files(uuid=self.id).result()
        fname = filter(lambda name: name.upper() != 'RFUploadAccessTestFile'.upper(), fnames)[0]
        url = 'https://{app_host}/api/exports/{export_id}/files/{file_name}'.format(
            app_host=self.api.app_host, export_id=self.id, file_name=fname)
        resp = requests.get(url, params={'token': self.api.api_token})
        resp.raise_for_status()
        return resp.content
