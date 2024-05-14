# Chat360 Assignment: Quality Log Control
- This app works as a query app that has filters for each of the values `level log_string timestamp metadata.source`
- Contains self-explanatory code that has 4-5 APIs that work on REST principle
- Stack used: 
  - Flask
  - flash-message
  - jinja templating engine
  - AJAX
  
## API documentation
- `/` - GET : renders the index page that is supposed to contain a form that will query the logs and display on the page itself dynamically.
- `/search` - GET : used to extract the filters that were required
- `/create_log` - GET: renders the create log form that requires the above value except timestamp(takes timestamp as current time)
- `/create_log` - POST: saves the log if all values are validated and parses the log file according to the name given.

## Note:
- Deployed using `render.com` at https://quality-log-control-n6d6.onrender.com/, might take around 30-40 seconds to load as it was deployed on free-tier :)
- PS - timestamp filter breaks occasionally, trying to figure out this one.