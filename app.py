from src import routes
from src.setup import app
from config import DEBUG, PORT_TO_RUN
from src.schedule_system import start_schedule

start_schedule()

# start the flask loop
app.debug = DEBUG
app.run('0.0.0.0', PORT_TO_RUN)
