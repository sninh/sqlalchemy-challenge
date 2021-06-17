import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: replace 'start' and 'end' with your query dates in the 'YYYY-MM-DD' format<br/>"
        f"Example: /api/v1.0/2017-01-01/2017-12-12"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve precipitation data"""
    # Query dates
    precipitation_date = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Return the JSON representation of your dictionary.
    precipitation_dict = {}
    for date, prcp in precipitation_date:
        precipitation_dict[date] = prcp

    return jsonify(precipitation_dict)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve station data"""
    # Query stations
    stations = session.query(Station.name, Station.station).join(Measurement, Station.station == Measurement.station)

    session.close()

    #Return a JSON list of stations from the dataset.

    return jsonify(dict(stations))


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date_str = session.query(func.max(Measurement.date)).first()[0]
    recent_date = dt.datetime.strptime(recent_date_str, "%Y-%m-%d").date()
    one_year = recent_date - dt.timedelta(days=365)
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).first()[0]

    # Query temperature observations for most recent year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year, Measurement.station == most_active_station)

    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    
    return jsonify(dict(results))

@app.route("/api/v1.0/<start>")
def summarize_temp_after_date(start):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # find the most recent date in the data set.
    recent_date_str = session.query(func.max(Measurement.date)).first()[0]

    # convert string date to datetime date
    recent_date = dt.datetime.strptime(recent_date_str, "%Y-%m-%d").date()

    
    #format start date 
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    
    # Query data
    results = session.query(func.max(Measurement.tobs).label('temp_max'), func.min(Measurement.tobs).label('temp_min'), func.avg(Measurement.tobs).label('temp_avg')).filter(Measurement.date >= start_date).all()

    session.close()
    
    # Create a dictionary from the data
    temperature_list = []
    for temperature_max, temperature_min, temperature_avg in results:
        temperature_dict = {}
        temperature_dict['start_date'] = str(start_date)
        temperature_dict['end_date'] = str(recent_date)
        temperature_dict["temp_max"] = temperature_max
        temperature_dict["temp_min"] = temperature_min
        temperature_dict["temp_avg"] = round(temperature_avg,2)
        temperature_list.append(temperature_dict)

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>/<end>")
def summarize_temp_between_dates(start, end):

    #Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    #When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    #format start date as datetime date
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()
    
    # Query data
    results = session.query(func.max(Measurement.tobs).label('temp_max'), func.min(Measurement.tobs).label('temp_min'), func.avg(Measurement.tobs).label('temp_avg')).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    session.close()
    
    # Create a dictionary from the data
    temperature_list = []
    for temperature_max, temperature_min, temperature_avg in results:
        temperature_dict = {}
        temperature_dict["start_date"] = str(start_date)
        temperature_dict["end_date"] = str(end_date)
        temperature_dict["temp_max"] = temperature_max
        temperature_dict["temp_min"] = temperature_min
        temperature_dict["temp_avg"] = round(temperature_avg,2)
        temperature_list.append(temperature_dict)

    return jsonify(temperature_list)

if __name__ == '__main__':
    app.run(debug=True)