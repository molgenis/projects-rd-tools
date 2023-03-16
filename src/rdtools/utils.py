from datetime import datetime
from pytz import timezone

def now(tz='Europe/Amsterdam'):
 """Now
 Return a timestamp formated as HH:MM:SSS

 @param tz timezone
 @return time string
 """
 return datetime.now(tz=timezone(tz)).strftime('%H:%M:%S.%f')[:-3]

def print2(*args):
  """Print2
  Extension of print but all messages are printed with a timestamp. By default,
  the timezone is 'Europe/Amsterdam'.
  
  @examples
  ```
  print2('Hello World')
  
  data = [{'id': value} for value in range(0,100)]
  print2('The total number of records is', len(data))
  ```
  """
  message = ' '.join(map(str, args))
  print(f'[{now()}] {message}')
  
class logger:
  def __init__(self, logname: str = 'cosas-daily-import', silent=False, printWithTime=True):
    """Cosas Logger
    Keep records of all processing steps and summarize the daily imports

    @param logname : name of the log
    @param silent : If True, all messages will be disabled
    @param printWithTime: If True and silent is False, all messages will be printed with timestamps
    """
    self.silent = silent
    self.logname = logname
    self.log = {}
    self.currentStep = {}
    self.processingStepLogs = []
    self._printWithTime = printWithTime
    self.tz = 'Europe/Amsterdam'
    self.hhmmss = '%H:%M:%S'
    self.hhmmss_f = '%H:%M:%S.%f'
    self.yyyymmdd_hhmmss = '%Y-%m-%dT%H:%M:%SZ'

  def _now(self, strftime=None):
    if strftime:
      return datetime.now(tz=pytz.timezone(self.tz)).strftime(strftime)
    return datetime.now(tz=pytz.timezone(self.tz))

  def _print(self, *message):
    if not self.silent:
      message = ' '.join(map(str, message))
      if self._printWithTime:
        message = f"[{self._now(strftime=self.hhmmss_f)[:-3]}] {message}"
      print(message)

  def __stoptime__(self, name):
    log = self.__getattribute__(name)
    log['endTime'] = self._now()
    log['elapsedTime'] = (log['endTime'] - log['startTime']).total_seconds()
    log['endTime'] = log['endTime'].strftime(self.yyyymmdd_hhmmss)
    log['startTime'] = log['startTime'].strftime(self.yyyymmdd_hhmmss)
    self.__setattr__(name, log)

  def start(self):
    """Start Log"""
    self.log = {
      'identifier': self._now(strftime='%Y-%m-%d'),
      'name': self.logname,
      'date': self._now(strftime='%Y-%m-%d'),
      'databaseName': 'cosas',
      'startTime': self._now(),
      'endTime': None,
      'elapsedTime': None,
      'steps': [],
      'comments': None
    }
    self._print(self.logname,': log started at',self.log['startTime'].strftime(self.hhmmss))

  def stop(self):
    """Stop Log"""
    self.__stoptime__(name='log')
    self.log['steps'] = ','.join(map(str, self.log['steps']))
    self._print('Logging stopped (elapsed time:', self.log['elapsedTime'], 'seconds')

  def startProcessingStepLog(self, type: str = None, name: str = None, tablename: str = None):
    """Start a new log for a processing step
    Create a new logging object for an individual step such as transforming
    data or importing data.

    @param type : data handling type (see lookups)
    @param name : name of the current step (e.g., 'import-data', 'save-data')
    @param tablename : database table the current step relates to
    """
    stepID = len(self.processingStepLogs) + 1
    self.currentStep = {
      'identifier': int(f"{self._now(strftime='%Y%m%d')}{stepID}"),
      'date': self._now(strftime='%Y-%m-%d'),
      'name': name,
      'step': type,
      'databaseTable': tablename,
      'startTime': self._now(),
      'endTime': None,
      'elapsedTime': None,
      'status': None,
      'comment': None
    }
    self._print(self.logname, ': starting step', name)

  def stopProcessingStepLog(self):
    """Stop a log for a processing step"""
    self.__stoptime__(name='currentStep')
    self.log['steps'].append(self.currentStep['identifier'])
    self.processingStepLogs.append(self.currentStep)
    self._print(
      self.logname, ': finished step',
      self.currentStep['name'],'in',
      self.currentStep['elapsedTime']
    )