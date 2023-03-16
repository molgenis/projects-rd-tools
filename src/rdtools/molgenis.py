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
from rdtools.utils import print2
from os import path
import numpy as np
import mimetypes
import tempfile
import json
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

  def importFile(self, file):
    """Import a file into Molgenis
    Import a file (pdf, txt, docx, etc.) into the files table. Content type
    and size is automatically determined.
    
    @param file location and name of the file to import
    
    @section
    If the file was successfully imported, you will receive information about
    the file and the location in the database. Use the file identifier to set
    additional permissions. This can be done using the molgenis commander.
    
    ```zsh
    mcmd config set host
    mcmd give \ 
      --user <user> <read|view|write|...> \
      --entity <file-identifier-in-database> \
      --package sys_FileMetaa
    ```
    
    @return a status message with import metadata
    """
    with open(file, 'rb') as stream:
      data = stream.read()
      stream.close()
    
    headers = self._headers.token_header
    headers['x-molgenis-filename'] = file
    headers['Content-Type'] = mimetypes.guess_type(file)[0]
    headers['Content-Size'] = str(path.getsize(file))
  
    url = f"{self._root_url}api/files"
    response = self._session.post(url=url, headers=headers, data=data)

    if response.status_code // 100 == 2:
      result = json.loads(response.text)
      print2(response.status_code)
      print2(result)
      return response
    else:
      print2(f"Failed to import {file}")
      print2(response.status_code)
      return response
