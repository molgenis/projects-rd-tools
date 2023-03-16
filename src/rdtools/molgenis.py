#////////////////////////////////////////////////////////////////////////////
# FILE: molgenis2.py
# AUTHOR: David Ruvolo
# CREATED: 2022-07-28
# MODIFIED: 2023-03-16
# PURPOSE: molgenis.client extensions
# STATUS: stable
# PACKAGES: molgenis-py-client >= 2.4.0
# COMMENTS: This class extension includes methods for importing DataTable-
# and Pandas DataFrame objects, as well as the ability to import files.
#////////////////////////////////////////////////////////////////////////////

import molgenis.client as molgenis
from . utils import print2
from os import path
import numpy as np
import tempfile
import csv

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
