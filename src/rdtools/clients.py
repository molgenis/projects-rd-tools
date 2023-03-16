
from .utils import print2
from os import path
import numpy as np
import tempfile
import csv
import molgenis.client as molgenis
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import LegacyApplicationClient

class Molgenis(molgenis.Session):
  def __init__(self, *args, **kwargs):
    super(Molgenis, self).__init__(*args, **kwargs)
    self.fileImportEndpoint = f"{self._root_url}plugin/importwizard/importFile"
  
  def _datatableToCsv(self, path, datatable):
    """To CSV
    Write datatable object as CSV file

    @param path location to save the file
    @param data datatable object
    """
    data = datatable.to_pandas().replace({np.nan: None})
    data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)
    
  def _dfToCsv(self, path, df):
    """To CSV
    Write pandas dataframe as CSV file

    @param path location to save the file
    @param df pandas data.frame
    """
    data = df.replace({np.nan: None})
    data.to_csv(path, index=False, quoting=csv.QUOTE_ALL)
  
  def importDatatableAsCsv(self, pkg_entity: str, data):
    """Import Datatable As CSV
    Save a datatable object to as csv file and import into MOLGENIS using the
    importFile api.
    
    NOTE: The File API will return a response if the file was imported. The
    response is NOT an indicator that the file is valid. Please check the
    entity sys_Import for more information.
    
    @param pkg_entity table identifier in emx format: package_entity
    @param data a datatable object
    
    @return status message
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      filepath=f"{tmpdir}/{pkg_entity}.csv"
      self._datatableToCsv(filepath, data)
      with open(path.abspath(filepath), 'r') as file:
        response = self._session.post(
          url = self.fileImportEndpoint,
          headers = self._headers.token_header,
          files = {'file': file},
          params = {'action': 'add_update_existing', 'metadataAction': 'ignore'}
        )
        if (response.status_code // 100 ) != 2:
          print2('Failed to import data into',pkg_entity,'(',response.status_code,')')
        else:
          print2('Imported data into', pkg_entity)
        return response
      
  def importPandasAsCsv(self, pkg_entity, data):
    """Import Pandas data.frame As CSV
    Save a datatable object to as csv file and import into MOLGENIS using the
    importFile api.
    
    NOTE: The File API will return a response if the file was imported. The
    response is NOT an indicator that the file is valid. Please check the
    entity sys_Import for more information.
    
    @param pkg_entity table identifier in emx format: package_entity
    @param data a python data.frame
    
    @return status message
    """
    with tempfile.TemporaryDirectory() as tmpdir:
      filepath=f"{tmpdir}/{pkg_entity}.csv"
      self._dfToCsv(filepath, data)
      with open(path.abspath(filepath), 'r') as file:
        response = self._session.post(
          url=self.fileImportApi,
          headers = self._headers.token_header,
          files={'file': file},
          params = {'action': 'add_update_existing', 'metadataAction': 'ignore'}
        )
        
        if (response.status_code // 100) != 2:
          print2('Failed to import data into',pkg_entity,'(',response.status_code,')')
        else:
          print2('Imported data into',pkg_entity)
      return response


class Alissa:
  """Alissa Interpret Public API (v5.3)"""
  
  def __init__(self, host, clientId, clientSecret, username, password):
    """Create new instance of the client
    A mini api client to get molecular variant information per patient.

    @param host The url of your Alissa Interpret instance
    @param clientId provided by Alissa Support
    @param clientSecret provided by Alissa Support
    @param username username of the API account
    @param password password of the API account
    
    @reference Alissa Interpret Public API documentation v5.3
    @return class
    """
    self.host=host
    self.apiUrl=f"{host}/interpret/api/2"
    self.session=OAuth2Session(client=LegacyApplicationClient(client_id=clientId))
    self.session.fetch_token(
      token_url=f"{host}/auth/oauth/token",
      username=username,
      password=password,
      client_id=clientId,
      client_secret=clientSecret
    )

    if self.session.access_token:
      print2(f"Connected to {host} as {username}")
    else:
      print2(f"Failed to connect to {host} as {username}")
      

  def _formatOptionalParams(self, params: dict=None) -> dict:
    """Format Optional Parameters
    
    @param params dictionary containg one or more parameter
    @return dict
    """
    return {
      key: params[key]
      for key in params.keys()
      if (key != 'self') and (params[key] is not None)
    }
  
  def _get(self, endpoint, params=None, **kwargs):
    """GET
    @param endpoint the Alissa Interpret endpoint where data should be
      sent to. The path "/interpret/api/2" is prefilled.
    @param params Optional parameters to add to the request
    """
    uri = f'{self.apiUrl}/{endpoint}'
    response = self.session.get(uri, params=params, **kwargs)
    response.raise_for_status()
    return response.json()
      
  def _post(self, endpoint, data=None, json=None, **kwargs):
    """POST
    @param endpoint the Alissa Interpret endpoint where data should be
      sent to. The path "/interpret/api/2" is prefilled.
    @param data Optional dictionary, list of tuples, bytes, or file-like object
    @param json Optional json data
    """
    uri = f'{self.apiUrl}/{endpoint}'
    response = self.session.post(uri, data, json, **kwargs)
    response.raise_for_status()
    return response.json()

  def getPatientByInternalId(self, patientId: str = None):
    """Get Patient By ID
    Retrieve patient information using Alissa's internal identifier for 
    patients rather than accession number.
    
    @param patientId the unique internal identifier of a patient (Alissa ID)
    @return json
    """
    url = f'{self.apiUrl}/patients/{patientId}'
    response = self.session.get(url)
    response.raise_for_status()
    return response.json()

  def getPatients(
    self,
    accessionNumber: str = None,
    createdAfter: str = None,
    createdBefore: str = None,
    createdBy: str = None,
    familyIdentifier: str = None,
    lastUpdatedAfter: str = None,
    lastUpdatedBefore: str = None,
    lastUpdatedBy: str = None
  ) -> dict:
    """Get Patients
    Get all patients. When filter criteria are provided, the result is
    limited to the patients matching the criteria.

    @param accessionNumber The unique identifier of the patient
    @param createdAfter Filter patients with a creation date after the
        specific date time (ISO 8601 date time format)
    @param createdBefore Filter patients with a creation date before the
        specific date time (ISO 8601 date time format)
    @param createdBy User that created the patient
    @param familyIdentifier The unique identifier of the family.
    @param lastUpdatedAfter Filter patients with a last updated date after
        the specified date time (ISO 8601 date time format)
    @param lastUpdatedBefore Filter patients with a last updated date
        before the specified date time (ISO 8601 date time format)
    @param lastUpdatedBy User that updated the patient.
    
    @reference Alissa Interpret Public API (v5.3; p21)
    @return dictionary containing one or more patient records
    """
    params = self._formatOptionalParams(params=locals())
    return self._get(endpoint='patients', params=params)

  def getPatientAnalyses(self, patientId: str) -> dict:
    """Get Analyses of Patient

    @param patientId The unique internal identifier of the patient

    @reference Alissa Interpret Public API (v5.3; p42)
    @return dictionary containing metadata for one or more analyses
    """
    return self._get(endpoint=f"patients/{patientId}/analyses")

  def getPatientVariantExportId(
    self,
    analysisId: int,
    markedForReview: bool=True,
    markedIncludeInReport: bool=True
  ) -> dict:
    """Request Patient Molecular Variants Export
    Request an export of all variants. When filter criteria are provided,
    the result is limited to the variants matching the criteria. By default
    the parameters `markedForReview` and `markedIncludeInReport` are set to
    True. This will return all results that have been selected.

    @param analysisId ID of the analysis
    @param markedForReview Is the variant marked for review
    @param markedIncludeInReport Is the variant included in the report

    @reference Alissa Interpret Public API (v5.3; p44)
    @param dictionary containing the export identifier
    """
    data={'markedForReview': markedForReview, 'markedIncludeInReport': markedIncludeInReport}
    api=f"patient_analyses/{analysisId}/molecular_variants/exports"
    return self._post(endpoint=api,json=data)

  def getPatientVariantExportData(self, analysisId: int, exportId: str) -> dict:
    """Get Patient Molecular Variants Export
    Get the exported variants of a patient analysis via the export ID
    returned when requesting the export.

    @param analysisId The unique internal identifier of an analysis
    @param exportId The unique internal identifier of the export

    @reference Alissa Interpret Public API (v5.3; p45)
    @return dictionary containing the molecular variant export data from a
        single analysis of one patient
    """
    api=f"patient_analyses/{analysisId}/molecular_variants/exports/{exportId}"
    return self._get(endpoint=api)
