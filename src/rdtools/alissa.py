# ////////////////////////////////////////////////////////////////////////////
# FILE: alissa.py
# AUTHOR: David Ruvolo
# CREATED: 2022-04-13
# MODIFIED: 2023-03-16
# PURPOSE: custom Alissa public api client
# STATUS: stable
# PACKAGES: requests
# COMMENTS: mini client for the Alissa Interpret Public API (v5.3) to get
# molecular variant information per patient. The `Alissa` class is designed to
# run in several steps that are controlled by the user. In order to extract
# the data, you must execute these methods in the following way.
#
#   1. `login`: Login
#   2. `getPatients`: Get all patients and extract patient IDs
#   3. `getPatientAnalyses`: For each patient, get all analyses and extract
#           analysis identifiers
#   4. `getPatientVariantExportId`: For each analysis, get all variant exports
#           and extract all export identifiers
#   5. `getPatientVariantExportData`: For each export identifier, get variant
#           data.
#
# Steps 3 to 5 can be run only if you have the patient, analysis, and export
# identifiers.
#
# All Alissa Public API parameters listed in the documentation are supported.
# Each method returns all records unless filters have been supplied. Additional
# processing can be done in between each request.
#
# This script was adapted from the Alissa Interpret Client written by the
# UMCU Genetics GitHub Organisation. In that version, it didn't quite work
# for out use case as either some of the endpoints have changed since the
# last release or they are using a different version.
# https://github.com/UMCUGenetics/alissa_interpret_client/blob/main/alissa_interpret_client/alissa_interpret.py
# ////////////////////////////////////////////////////////////////////////////

from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session
from . utils import print2

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
