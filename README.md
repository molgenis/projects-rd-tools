# rdtools

## Getting Started

This package includes a number of methods and class extensions that are commonly used across multiple projects. It was decided to bundle all of these scripts into a single package to make deployment a bit easier. This package contains the following tools.

- Molgenis PyClient Extensions: quickly import DataTable or DataFrame objects as csv files
- Alissa API client: interact with Alissa Interpret instances
- And more!

### Installation

For now, this package is only released on GitHub. To install it, use the following command.

```py
pip install https://github.com/molgenis/projects-rd-tools/dist/rdtools-0.0.0.tar.gz
```

### Using rdtools

This package includes the following methods.

| Name | Description | Import |
|------|------------|----------|
| Molgenis | molgenis-py-client extensions | `from rdtools.clients import Molgenis`
| Alissa | interact with an Alissa Interpret instance |  `from rdtools.clients import Alissa`
| Logger | log script actions\* | `from rdtools.utils import Logger`
| now | create a timestamp `HH:MM:SSS` | `from rdtools.utils import now`
| print2 | print a message with timestamp |  `from rdtools.utils import print2`

The `Logger` class is designed to capture information for the [reports.yaml datamodel](https://github.com/molgenis/molgenis-cosas/blob/main/model/cosasreports.yaml).

### Notes

#### Importing DataTable objects

One of the primary features of this package is the ability to import DataTable objects into a Molgenis database using the File API. This makes it easier to import large datasets without running into REST API limitations and a elastic search indexing backlog. For example:

```py
from rdtools.clients import Molgenis
from datatable import dt,fread

mydatabase = Molgenis(...)
mydatabase.login(...)

data = fread('path/to/some/dataset.csv')
mydatabase.importDataTableAsCsv(pkg_entity='...', data=data)
```

In order to use this in your database, you will need to install the [datatable](https://pypi.org/project/datatable/) package. Datatable can be installed from PyPI, but we have used the github build for many of the projects as this version includes more features and it installs on newer version of macOS. Please check the [DataTable GitHub repo](https://github.com/h2oai/datatable) for the latest installation instructions. For now, you can install DataTable from GitHub using the following command.

```py
pip install git+https://github.com/h2oai/datatable
```

> Note: The file API returns a status that indicates if the file successfully imported or not. It does not inform you if the contents of the file was valid. You will have to check the 'sys_Imports' table to confirm the status of the import.
