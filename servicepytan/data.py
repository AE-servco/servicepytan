"""Provides methods for simplified and opininated ways of retrieving data from the ServiceTitan API"""
from servicepytan.requests import Endpoint
from servicepytan._dates import _convert_date_to_api_format
from servicepytan.utils import get_timezone_by_file
class DataService:
  """Primary class for executing data methods.

  The DataService class retrieves the configuration file and authentication settings.
  The methods included are a selection of common data pulls with a simplified API generally
  based on retrieving data between a date range.

  Attributes:
      conn: a dictionary containing the credential config.
  """
  def __init__(self, conn=None):
    """Inits DataService with configuration file and authentication settings."""
    self.conn = conn
    self.timezone = get_timezone_by_file(conn)

  def get_api_data(self, folder, endpoint, options=None, version=2):
    """Retrieve data from specified folder and endpoint
    
    Args:
        folder: API folder e.g. 'jpm'
        endpoint: API endpoint e.g. 'jobs'
        options: request parameters e.g. {'createdOnOrAfter': '2025-10-20T20:00:00Z'}
        version: API version (always 2 except for calls endpoint.)
        
    Returns:
        list: list of response dicts
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_api_data('accounting', 'invoices', options={'createdOnOrAfter': '2025-10-20T20:00:00Z'})
    """
    if options is None:
        options = {}
        print(f"WARNING: You have not put any options in so this will call EVERYTHING! Endpoint: {folder}, {endpoint}")
    return Endpoint(folder, endpoint, version=version, conn=self.conn).get_all(options)
    
  def get_api_data_between(self, folder, endpoint, start_date, end_date, date_filter_modifier="completed", options=None, version=2):
    """Retrieve data from specified folder and endpoint between dates
    
    Args:
        folder: API folder e.g. 'jpm'
        endpoint: API endpoint e.g. 'jobs'
        options: request parameters e.g. {'createdOnOrAfter': '2025-10-20T20:00:00Z'}
        version: API version (always 2 except for calls endpoint.)
        date_filter_modifier: the word that is used in the date filters for the request, usually one of "completed", "created", "started".
        
    Returns:
        list: list of response dicts
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_api_data_between('accounting', 'invoices', date(2025,10,20), date(2025,10,21), "created")
    """
    if options is None:
        options = {}

    options[f"{date_filter_modifier}OnOrAfter"] = _convert_date_to_api_format(start_date, self.timezone)
    options[f"{date_filter_modifier}Before"] = _convert_date_to_api_format(end_date, self.timezone)
    return self.get_api_data(folder, endpoint, options=options, version=version)

  def get_jobs_completed_between(self, start_date, end_date, job_status=["Completed","Scheduled","InProgress","Dispatched"], app_guid=None):
    """Retrieve all jobs completed between the start and end date.
    
    Fetches jobs that were completed within the specified date range.
    Can filter by multiple job statuses simultaneously.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        job_status: List of job statuses to include (default includes most common statuses)
        
    Returns:
        list: Combined list of all jobs matching the criteria
        
    Examples:
        >>> data_service = DataService(conn)
        >>> jobs = data_service.get_jobs_completed_between("2024-01-01", "2024-01-31")
        >>> completed_only = data_service.get_jobs_completed_between(
        ...     "2024-01-01", "2024-01-31", job_status=["Completed"]
        ... )
    """
    data = []
    for status in job_status:
      options = {
        "jobStatus": status,
        "completedOnOrAfter": _convert_date_to_api_format(start_date, self.timezone),
        "completedBefore": _convert_date_to_api_format(end_date, self.timezone)
      }
      if app_guid:
        options["externalDataApplicationGuid"] = app_guid
      data.extend(Endpoint("jpm", "jobs", conn=self.conn).get_all(options))
    
    return data

  def get_jobs_created_between(self, start_date, end_date, app_guid=None):
    """Retrieve all jobs created between the start and end date.
    
    Fetches jobs that were originally created within the specified date range,
    regardless of their current status or completion date.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all jobs created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_jobs = data_service.get_jobs_created_between("2024-01-01", "2024-01-31")
    """
    options = {
      "createdOnOrAfter": _convert_date_to_api_format(start_date, self.timezone),
      "createdBefore": _convert_date_to_api_format(end_date, self.timezone)
    }
    if app_guid:
      options["externalDataApplicationGuid"] = app_guid
    return Endpoint("jpm", "jobs", conn=self.conn).get_all(options)

  def get_appointments_between(self, start_date, end_date, appointment_status=["Scheduled", "Dispatched", "Working","Done"]):
    """Retrieve all appointments that start between the start and end date.
    
    Fetches appointments scheduled to start within the specified date range.
    Can filter by multiple appointment statuses simultaneously.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        appointment_status: List of appointment statuses to include
        
    Returns:
        list: Combined list of all appointments matching the criteria
        
    Examples:
        >>> data_service = DataService(conn)
        >>> appointments = data_service.get_appointments_between("2024-01-01", "2024-01-31")
        >>> scheduled_only = data_service.get_appointments_between(
        ...     "2024-01-01", "2024-01-31", appointment_status=["Scheduled"]
        ... )
    """
    data = []
    for status in appointment_status:
      options = {
        "status": status,
        "startsOnOrAfter":_convert_date_to_api_format(start_date, self.timezone),
        "startsBefore":_convert_date_to_api_format(end_date, self.timezone)
      }
      data.extend(Endpoint("jpm", "appointments", conn=self.conn).get_all(options))
    
    return data

  def get_sold_estimates_between(self, start_date, end_date):
    """Retrieve all sold estimates that were sold between the start and end date.
    
    Fetches estimates that were marked as sold within the specified date range.
    Only includes active (not cancelled) estimates.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all sold estimates in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> sold_estimates = data_service.get_sold_estimates_between("2024-01-01", "2024-01-31")
    """
    options = {
        "active": "True",
        "soldAfter":_convert_date_to_api_format(start_date, self.timezone),
        "soldBefore":_convert_date_to_api_format(end_date, self.timezone)
      }
    return Endpoint("sales", "estimates", conn=self.conn).get_all(options)

  def get_total_sales_between(self, start_date, end_date):
    """Retrieves total sales dollar amount between start and end date.
    
    Calculates the total sales amount by summing all sold estimate items
    within the specified date range. This provides a quick way to get
    revenue totals for reporting.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        float: Total sales amount for the period
        
    Examples:
        >>> data_service = DataService(conn)
        >>> total_sales = data_service.get_total_sales_between("2024-01-01", "2024-01-31")
        >>> print(f"Total sales: ${total_sales:,.2f}")
    """
    data = self.get_sold_estimates_between(start_date, end_date)
    sales = 0
    for row in data:
      for sku in row["items"]:
        sales += sku['total']
    
    return sales

  def get_purchase_orders_created_between(self, start_date, end_date):
    """Retrieve all purchase orders created between the start and end date.
    
    Fetches purchase orders that were created within the specified date range,
    useful for tracking procurement activity and spend.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all purchase orders created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> pos = data_service.get_purchase_orders_created_between("2024-01-01", "2024-01-31")
    """
    options = {
        "createdOnOrAfter":_convert_date_to_api_format(start_date, self.timezone),
        "createdBefore":_convert_date_to_api_format(end_date, self.timezone)
      }
    return Endpoint("inventory", "purchase-orders", conn=self.conn).get_all(options)

  def get_jobs_modified_between(self, start_date, end_date, app_guid=None):
    """Retrieve all jobs modified between the start and end date.
    
    Fetches jobs that were updated or modified within the specified date range,
    useful for tracking changes and updates to existing jobs.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all jobs modified in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> modified_jobs = data_service.get_jobs_modified_between("2024-01-01", "2024-01-31")
    """
    options = {
      "modifiedOnOrAfter":_convert_date_to_api_format(start_date, self.timezone),
      "modifiedBefore":_convert_date_to_api_format(end_date, self.timezone)
    }
    if app_guid:
      options["externalDataApplicationGuid"] = app_guid
    data = Endpoint("jpm", "jobs", conn=self.conn).get_all(options)
    
    return data

  def get_employees(self, active="True"):
    """Retrieve employee list.
    
    Fetches the list of employees from ServiceTitan. Can filter to show
    only active employees or include inactive ones as well.
    
    Args:
        active: String indicating whether to show only active employees ("True" or "False")
        
    Returns:
        list: List of employee records
        
    Examples:
        >>> data_service = DataService(conn)
        >>> active_employees = data_service.get_employees()
        >>> all_employees = data_service.get_employees(active="False")
    """
    options = {
        "active": active
      }
    return Endpoint("settings", "employees", conn=self.conn).get_all(options)

  def get_technicians(self, active="True"):
    """Retrieve technician list.
    
    Fetches the list of technicians from ServiceTitan. Technicians are
    a subset of employees who perform field work.
    
    Args:
        active: String indicating whether to show only active technicians ("True" or "False")
        
    Returns:
        list: List of technician records
        
    Examples:
        >>> data_service = DataService(conn)
        >>> active_techs = data_service.get_technicians()
        >>> all_techs = data_service.get_technicians(active="False")
    """
    options = {
        "active": active
      }
    return Endpoint("settings", "technicians", conn=self.conn).get_all(options)

  def get_tag_types(self, active="True"):
    """Retrieve tag types list.
    
    Fetches the list of tag types configured in ServiceTitan. Tag types
    are used to categorize and organize jobs, customers, and other entities.
    
    Args:
        active: String indicating whether to show only active tag types ("True" or "False")
        
    Returns:
        list: List of tag type records
        
    Examples:
        >>> data_service = DataService(conn)
        >>> tag_types = data_service.get_tag_types()
    """
    options = {
        "active": active
      }
    return Endpoint("settings", "tag-types", conn=self.conn).get_all(options)

  def get_business_units(self, active="True"):
    """Retrieve business units list.
    
    Fetches the list of business units configured in ServiceTitan. Business
    units are used to organize operations by service type, location, or other criteria.
    
    Args:
        active: String indicating whether to show only active business units ("True" or "False")
        
    Returns:
        list: List of business unit records
        
    Examples:
        >>> data_service = DataService(conn)
        >>> business_units = data_service.get_business_units()
    """
    options = {
        "active": active
      }
    return Endpoint("settings", "business-units", conn=self.conn).get_all(options)

  def get_job_types(self, active="Any"):
    """Retrieve job types list.
    
    Fetches the list of job types configured in ServiceTitan.
    
    Args:
        active: String indicating whether to show only active job types ("True", "False", or "Any")
        
    Returns:
        list: List of job type records
        
    Examples:
        >>> data_service = DataService(conn)
        >>> job_types = data_service.get_job_types()
    """
    options = {
        "active": active
      }
    return Endpoint("jpm", "job-types", conn=self.conn).get_all(options)
  
  def get_calls_between(self, start_date, end_date):
    """Retrieve all calls between the start and end date.
    
    Fetches calls that were made or taken within the specified date range,
    regardless of their current status.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all calls created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_jobs = data_service.get_calls_between("2024-01-01", "2024-01-31")
    """
    options = {
      "createdOnOrAfter": _convert_date_to_api_format(start_date, self.timezone),
      "createdBefore": _convert_date_to_api_format(end_date, self.timezone)
    }
    return Endpoint("telecom", "calls", version="3", conn=self.conn).get_all(options)
  
  def get_bookings_between(self, start_date, end_date):
    """Retrieve all bookings between the start and end date.
    
    Fetches bookings that were made or taken within the specified date range,
    regardless of their current status.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all bookings created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_jobs = data_service.get_bookings_between("2024-01-01", "2024-01-31")
    """
    options = {
      "createdOnOrAfter": _convert_date_to_api_format(start_date, self.timezone),
      "createdBefore": _convert_date_to_api_format(end_date, self.timezone)
    }
    return Endpoint("crm", "bookings", conn=self.conn).get_all(options)
  
  def get_payments_between(self, start_date, end_date):
    """Retrieve all payments between the start and end date.
    
    Fetches payments that were made or taken within the specified date range,
    regardless of their current status.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all payments created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_jobs = data_service.get_payments_between("2024-01-01", "2024-01-31")
    """
    options = {
      "paidOnAfter": _convert_date_to_api_format(start_date, self.timezone),
      "paidOnBefore": _convert_date_to_api_format(end_date, self.timezone)
    }
    return Endpoint("accounting", "payments", conn=self.conn).get_all(options)
  
  def get_invoices_between(self, start_date, end_date):
    """Retrieve all invoices between the start and end date.
    
    Fetches invoices that were made within the specified date range,
    regardless of their current status.
    
    Args:
        start_date: Start date for the query (string or datetime object)
        end_date: End date for the query (string or datetime object)
        
    Returns:
        list: List of all invoices created in the date range
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_invoices_between("2024-01-01", "2024-01-31")
    """
    options = {
      "invoicedOnOrAfter": _convert_date_to_api_format(start_date, self.timezone),
      "invoicedOnBefore": _convert_date_to_api_format(end_date, self.timezone)
    }
    return Endpoint("accounting", "invoices", conn=self.conn).get_all(options)
  
  def get_invoices_by_id(self, ids):
    """Retrieve all invoices with the specified ids.
    
    Args:
        ids: list of invoice ids to fetch.
        
    Returns:
        list: List of all invoices with given ids
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_invoices_by_id([123456, 5634765894])
    """
    options = {
      "ids": ','.join(ids)
    }
    return Endpoint("accounting", "invoices", conn=self.conn).get_all(options)
  
  def get_estimates_by_job_id(self, job_id):
    """Retrieve all estimates with the specified job id.
    
    Args:
        job_id: the job id to query against.
        
    Returns:
        list: List of all estimates on the given job
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_estimates_by_job_id(12334456)
    """
    options = {
      "jobId": job_id
    }
    return Endpoint("sales", "estimates", conn=self.conn).get_all(options)
  
  def get_appointment_assignments_by_job_id(self, job_id):
    """Retrieve all appointment assignments with the specified job id.
    
    Args:
        job_id: the job id to query against.
        
    Returns:
        list: List of all appointment assignments on the given job 
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_appointment_assignments_by_job_id(12334456)
    """
    options = {
      "jobId": job_id
    }
    return Endpoint("dispatch", "appointment-assignments", conn=self.conn).get_all(options)
  
  def get_technician_by_id(self, tech_id):
    """Retrieve technician with the specified id.
    
    Args:
        tech_id: the id to query against.
        
    Returns:
        dict: technician response dict
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_technician_by_id(12334456)
    """
    options = {
      "ids": tech_id
    }
    return Endpoint("settings", "technicians", conn=self.conn).get_all(options)[0]
  
  def get_all_technicians(self):
    """Retrieve all technician details.
    
    Args:
        
    Returns:
        list: list of technicians response dicts
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_all_technicians()
    """
    options = {
    }
    return Endpoint("settings", "technicians", conn=self.conn).get_all(options)
  
  def get_payments_for_invoices(self, invoice_ids):
    """Retrieve all payments applied to a list of invoices
    
    Fetches payments that were applied to the specified invoice ids,
    regardless of their current status.
    
    Args:
        invoice_ids: list of ids of invoices to get payments for
        
    Returns:
        list: List of all payments applied to the given invoices
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_jobs = data_service.get_payments_for_invoices([12345, 32432])
    """
    options = {
      "appliedToInvoiceIds": ','.join(invoice_ids)
    }
    return Endpoint("accounting", "payments", conn=self.conn).get_all(options)
  
  def get_all_tag_types(self):
    """Retrieve all tag type details.
    
    Args:
        
    Returns:
        list: list of tag types response dicts
        
    Examples:
        >>> data_service = DataService(conn)
        >>> new_invoices = data_service.get_all_tag_types()
    """
    options = {
    }
    return Endpoint("settings", "tag-types", conn=self.conn).get_all(options)
  
  def get_attachment(self, attach_id):
    """Retrieve attachment.
    
    Args:
        
    Returns:
        raw attachment data
        
    Examples:
        >>> data_service = DataService(conn)
        >>> attachment = data_service.get_attachment()
    """
    return Endpoint("forms", f"jobs/attachment", conn=self.conn).get_one_raw(attach_id).content
  
  def patch_job_external_data(self, job_id, data_payload, external_guid, patch_mode="Merge"):
    """Retrieve external data from a job
    
    Args:
        job_id: ID of job
        external_guid: Application external GUID
    Returns:
        External data from job 
        
    Examples:
        >>> data_service = DataService(conn)
        >>> attachment = data_service.get_job_external_data(1451, 'fdsnfkjaj2n4jkrf-dgfmdgkfd')
    """
    payload = {
      "externalData": {
        "patchMode": patch_mode,
        "applicationGuid": external_guid,
        "externalData": data_payload
      }
    }
    return Endpoint("jpm", f"jobs", conn=self.conn).update(job_id, json_payload=payload, request_type="PATCH")
