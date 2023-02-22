from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import create_engine, text, MetaData, Column, String, Integer, Date
from sqlalchemy.ext.declarative import declarative_base
import uuid
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import pandas as pd
from datetime import date
from enum import Enum

app = Flask(__name__)
Base = declarative_base()

# custom class for logging into server and creating engine object to database


class db_details():

    def __init__(self) -> None:
        self.pw, self.db_name = '', ''

    def set_db_details(self):
        with open('login.txt', 'r') as f:
            splitText = []
            for item in f:
                line = item.split(',')
                for piece in line:
                    splitText.append(piece.strip())
            self.pw, self.db_name = splitText[0], splitText[1]
        f.close()
        uri = "mysql+pymysql://root:" + self.pw + \
            "@" + 'localhost' + "/" + self.db_name
        return uri

# Custom Enum class for returning jobs from search parameters


class columnTitles(Enum):
    jobTitle = "Job_Title="
    company = "Company="
    location = "Location="
    salary_and_hour_info = "Salary_and_Hour_Info="
    date_added = "Date_Added_to_List="
    applied = "Applied="
    interviewed = "Interviewed="
    rejected = "Rejected="

# Gets the tables currently in the database


def tables():
    m = MetaData()
    m.reflect(engine)
    string = []
    for table in m.tables.values():
        string.append(table.name)

    return string

# method to return custom schema object for each job entry in each table designated by differences in tableName
# used for adding new jobs to specified tables


def models(tableName):

    class Job(Base, db.Model):

        __tablename__ = tableName
        __table_args__ = {'extend_existing': True}
        job_id = Column(Integer, primary_key=True)
        index = Column(Integer)
        Job_Title = Column(String)
        Company = Column(String)
        Location = Column(String)
        Salary_and_Hour_Info = Column(String)
        Job_Description = Column(String)
        Date_Added_to_List = Column(Date)
        Applied = Column(Integer)
        Interviewed = Column(Integer)
        Rejected = Column(Integer)

        def __init__(self, index, job_title, company, location,
                     salary, job_desc, date_added, applied, interviewed, rejected):
            self.index = index
            self.Job_Title = job_title
            self.Company = company
            self.Location = location
            self.Salary_and_Hour_Info = salary
            self.Job_Description = job_desc
            self.Date_Added_to_List = date_added
            self.Applied = applied
            self.Interviewed = interviewed
            self.Rejected = rejected

    return Job


details = db_details()
uri = details.set_db_details()
engine = create_engine(uri)
app.config['SQLALCHEMY_DATABASE_URI'] = uri
# app.config['JWT_SECRET_KEY'] = str(uuid.uuid4())
db = SQLAlchemy(app)
ma = Marshmallow(app)
# jwt = JWTManager(app)

# Route for getting all table names in the database


@ app.route('/jobs/searches', methods=['GET'])
def searches():
    return jsonify(tables())

# Route for getting jobs specified by whatever parameters the user provides


@ app.route('/jobs/<string:tableName>', methods=['GET'])
def parameters(tableName):

    if tableName not in tables():
        return jsonify(message="That table does not exist in the database"), 404

    filterString = " WHERE "
    andString = " AND "
    filterDict = {}
    try:
        jobTitle = ("'" + request.args.get('jobTitle') +
                    "'") if request.args.get('jobTitle') else None
        if jobTitle:
            filterDict[columnTitles.jobTitle.value] = jobTitle

        company = ("'" + request.args.get('company') +
                   "'") if request.args.get('company') else None
        if company:
            filterDict[columnTitles.company.value] = company

        location = ("'" + request.args.get('location') +
                    "'") if request.args.get('location') else None
        if location:
            filterDict[columnTitles.location.value] = location

        date_added = ("'" + request.args.get('date_added') +
                      "'") if request.args.get('date_added') else None
        if date_added:
            filterDict[columnTitles.date_added.value] = date_added

        applied = request.args.get(
            'applied') if request.args.get('applied') else None
        if applied:
            filterDict[columnTitles.applied.value] = applied

        interviewed = request.args.get(
            'interviewed') if request.args.get('interviewed') else None
        if interviewed:
            filterDict[columnTitles.interviewed.value] = interviewed

        rejected = request.args.get(
            'rejected') if request.args.get('rejected') else None
        if rejected:
            filterDict[columnTitles.rejected.value] = rejected

        if filterDict:
            if len(filterDict) == 1:
                for k, v in filterDict.items():
                    filterString = filterString + k + v
            else:
                for k, v in filterDict.items():
                    filterString = filterString + k + v + andString
                filterString = filterString.rstrip(andString)
            query = "SELECT * FROM " + tableName + filterString
        else:
            query = "SELECT * FROM " + tableName
        return pd.DataFrame(engine.connect().execute(text(query))).to_json(orient='records')

    except:
        return jsonify(message='There are no jobs in the database by these filters'), 404

# Route for adding new jobs to the specified table


@ app.route('/jobs/<string:tableName>/postJob', methods=['POST'])
# @jwt_required()
def postJob(tableName: str):
    if tableName not in tables():
        return jsonify(message="That table does not exist in the database"), 404

    job = []
    try:
        job.append(0)  # for index
        jobTitle = request.args.get(
            'jobTitle') if request.args.get('jobTitle') else None
        if jobTitle:
            job.append(jobTitle)
        else:
            return jsonify(message="You can't add a job without a job title"), 400

        company = request.args.get(
            'company') if request.args.get('company') else None
        if company:
            job.append(company)
        else:
            return jsonify(message="You can't add a job without a company name"), 400

        location = request.args.get(
            'location') if request.args.get('location') else None
        if location:
            job.append(location)
        else:
            return jsonify(message="You can't add a job without a location"), 400

        salary = request.args.get('salaryInfo') if request.args.get('salaryInfo') \
            else None
        job.append(salary) if salary else job.append("No data provided")

        job_desc = request.args.get('jobDesc') if request.args.get('jobDesc') \
            else None
        job.append(job_desc) if job_desc else job.append("No data provided")

        date_added = str(date.today())
        job.append(date_added)

        applied = request.args.get(
            'applied') if request.args.get('applied') else None
        job.append(applied) if applied else job.append(0)

        interviewed = request.args.get(
            'interviewed') if request.args.get('interviewed') else None
        job.append(interviewed) if interviewed else job.append(0)

        rejected = int(request.args.get(
            'rejected')) if request.args.get('rejected') else None
        if rejected:
            if rejected > 0:
                return jsonify(message='You cannot add a posting you have already been rejected from'), 403
        job.append(rejected) if rejected else job.append(0)

        new_job = models(tableName)
        job_entry = new_job(job[0], job[1], job[2], job[3], job[4],
                            job[5], job[6], job[7], job[8], job[9])

        db.session.add(job_entry)
        db.session.commit()
        return jsonify(message='You added a job'), 201
    except:
        return jsonify(message='An error occurred when creating the entry'), 400

# Method for updating the job contained in the jobReturn object


def update(applied, interviewed, rejected, jobReturn):

    if not applied and not interviewed and not rejected:
        return jsonify(message='Please indicate whether you have applied, interviewed, or been rejected from the selected position'), 400
    else:
        if applied:
            jobReturn.Applied = 1
            db.session.commit()
        if interviewed:
            jobReturn.Interviewed = 1
            db.session.commit()
        if rejected:
            jobReturn.Rejected = 1
            db.session.commit()
        return jsonify(message='You updated a job')

# Route to update job


@ app.route('/jobs/<string:tableName>/updateJob', methods=['PUT'])
# @jwt_required()
def updateJob(tableName: str):
    if tableName not in tables():
        return jsonify(message="That table does not exist in the database"), 404

    job_Search = models(tableName)
    jobReturn = None

    applied = request.args.get(
        'applied') if request.args.get('applied') else None

    interviewed = request.args.get(
        'interviewed') if request.args.get('interviewed') else None

    rejected = request.args.get(
        'rejected') if request.args.get('rejected') else None

    job_id = request.args.get(
        'job_id') if request.args.get('job_id') else None
    if job_id:
        jobReturn = job_Search.query.filter_by(job_id=job_id).first()
        if jobReturn:
            return update(applied, interviewed, rejected, jobReturn)
        else:
            return jsonify(message='There is no job by that id'), 404

    jobTitle = request.args.get(
        'jobTitle') if request.args.get('jobTitle') else None
    if not jobTitle:
        return jsonify(message="You can't update a job without a job title"), 400

    company = request.args.get(
        'company') if request.args.get('company') else None

    location = request.args.get(
        'location') if request.args.get('location') else None

    if company:
        if location:
            jobReturn = job_Search.query.filter_by(
                Job_Title=jobTitle, Company=company, Location=location).first()
        else:
            jobReturn = job_Search.query.filter_by(
                Job_Title=jobTitle, Company=company).first()
    else:
        jobReturn = job_Search.query.filter_by(Job_Title=jobTitle).first()
    if jobReturn:
        return update(applied, interviewed, rejected, jobReturn)
    else:
        return jsonify(message='No jobs were found to update'), 404

# Method for deleting job specified by jobReturn object


def jobDelete(jobReturn):
    db.session.delete(jobReturn)
    db.session.commit()
    return jsonify(message='You deleted a job'), 202

# Route to delete job


@ app.route('/jobs/<string:tableName>/deleteJob', methods=['DELETE'])
def delete(tableName: str):
    if tableName not in tables():
        return jsonify(message="That table does not exist in the database"), 404

    job_Search = models(tableName)
    jobReturn = None

    job_id = request.args.get(
        'job_id') if request.args.get('job_id') else None
    if job_id:
        jobReturn = job_Search.query.filter_by(job_id=job_id).first()
        if jobReturn:
            return jobDelete(jobReturn)
        else:
            return jsonify(message='There is no job by that id'), 404

    jobTitle = request.args.get(
        'jobTitle') if request.args.get('jobTitle') else None
    if not jobTitle:
        return jsonify(message="You can't update a job without a job title"), 400

    company = request.args.get(
        'company') if request.args.get('company') else None

    location = request.args.get(
        'location') if request.args.get('location') else None

    if company:
        if location:
            jobReturn = job_Search.query.filter_by(
                Job_Title=jobTitle, Company=company, Location=location).first()
        else:
            jobReturn = job_Search.query.filter_by(
                Job_Title=jobTitle, Company=company).first()
    else:
        jobReturn = job_Search.query.filter_by(Job_Title=jobTitle).first()
    if jobReturn:
        return jobDelete(jobReturn)
    else:
        return jsonify(message='No jobs were found to delete'), 404

# Schema class for returning job data using sqlalchemy


class JobSchema(ma.Schema):
    class Meta:
        fields = ('job_id', 'index', 'Job_Title', 'Company', 'Location', 'Salary_and_Hour_Info',
                  'Job_Description', 'Date_Added_to_List', 'Applied', 'interviewed', 'Rejected')


job_schema = JobSchema()
