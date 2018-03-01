"""An Export is a job to get underlying geospatial data out of Raster Foundry"""

from shapely.geometry import mapping, box, MultiPolygon


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

    @classmethod
    def create_export(cls,
                      api,
                      bbox,
                      zoom,
                      project=None,
                      analysis=None,
                      visibility='PRIVATE',
                      source=None,
                      export_type='LOCAL'):
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
            'source': source,
            'visibility': visibility,
            'toolRunId': None,
            'organizationId': None
        }
        export_create.update(update_dict)
        return api.client.Imagery.post_exports(Export=export_create).result()
