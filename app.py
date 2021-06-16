import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
        f"Note: replace 'start' and 'end' with your query dates in the 'YYYY-MM-DD' format" 
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve precipitation data"""
    # Query dates
    precipitation_date = session.query(measurement.date, measurement.prcp).all()

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
    stations = session.query(station.id, station.station, station.name).all()

    session.close()

    #Return a JSON list of stations from the dataset.

    return jsonify(dict(stations))


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Retrieve temp data from most active station"""
    # Find the most recent date in the data set.
    recent_date_str = session.query(func.max(measurement.date)).first()[0]
    recent_date = (dt.datetime.strptime(recent_date_str, "%Y-%m-%d")).date()
    one_year = recent_date - dt.timedelta(days=365)
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
                               order_by(func.count(measurement.station).desc()).\
                               group_by(measurement.station).all()
    most_active_station = pd.DataFrame(session.query(measurement.tobs).\
                                  filter((measurement.station == most_active)\
                                          &(measurement.date>= one_year)).all()
    session.close()

    # Return a JSON list of temperature observations (TOBS) for the previous year.
    
    return jsonify(most_active_station)

@app.route("/api/v1.0/<start>")
def starting_temp(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

        # * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        # * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
        # Find the most recent date in the data set.
        recent_date_str = session.query(func.max(measurement.date)).first()[0]
        recent_date = (dt.datetime.strptime(recent_date_str, "%Y-%m-%d")).date()

    if __name__ == "__main__":
    app.run(debug=True)
