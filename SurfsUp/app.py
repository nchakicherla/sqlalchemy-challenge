# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt

from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def landing():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(measurement).filter(
        measurement.date >= (
            dt.datetime.strptime(session.query(func.max(measurement.date)).scalar(), "%Y-%m-%d") - dt.timedelta(days=365)
        )
    ).all()
    
    selected_data = [(x.date, x.prcp) for x in results]
    results_df = pd.DataFrame(selected_data, columns=["date", "precipitation"])
    results_df = results_df.sort_values(by="date")

    results_dict = dict(zip(results_df.date, results_df.precipitation))

    resp = jsonify(results_dict)

    return resp

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()

    return jsonify([r.station for r in results])

@app.route("/api/v1.0/tobs")
def tobs():
    results = session.query(
        measurement.station, 
        func.count(measurement.id).label("measurement_count")
    ).group_by(measurement.station).order_by(func.count(measurement.id).desc()).all()

    top_station = results[0]

    results = session.query(measurement.tobs).filter(
        measurement.date >= (
            dt.datetime.strptime(session.query(func.max(measurement.date)).scalar(), "%Y-%m-%d") - dt.timedelta(days=365)
        )
    ).filter(measurement.station == top_station[0]).all()
    
    selected_data = [(r.tobs) for r in results]

    return jsonify(selected_data)

@app.route("/api/v1.0/<lower>/")
def summary_tobs_single(lower):

    start_date = lower
    
    summary_temps = session.query(
        func.min(measurement.tobs).label("min_temp"),
        func.max(measurement.tobs).label("max_temp"),
        func.avg(measurement.tobs).label("avg_temp")
    ).filter(measurement.date >= start_date).all()

    return jsonify([s for s in summary_temps[0]])

@app.route("/api/v1.0/<start>/<end>")
def summary_tobs_double(start, end):

    start_date = start
    end_date = end
    
    summary_temps = session.query(
        func.min(measurement.tobs).label("min_temp"),
        func.max(measurement.tobs).label("max_temp"),
        func.avg(measurement.tobs).label("avg_temp")
    ).filter(
        measurement.date.between(start_date, end_date)
    ).all()

    return jsonify([s for s in summary_temps[0]])

if __name__ == '__main__':
    app.run(debug=True)








