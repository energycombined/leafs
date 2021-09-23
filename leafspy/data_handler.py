from cellpy import cellreader
from cellpy import prmreader
import json 
import psycopg2
from psycopg2 import Error
from galvani import BioLogic
import pandas as pd
import json 
import os

def delete_file(file_name):
    try:
        os.remove(file_name)
    except:
        print("error while deleting file...")

def transform_data_galvani(file_name):

    try:
        mpr_file = BioLogic.MPRfile(rf"{file_name}")
        df = pd.DataFrame(mpr_file.data)
        df = df.iloc[0:5, :]
        out_cv_biologicmpr = json.loads(df.to_json(orient='split'))
        xx= {
            "experiment_info":{
                "test type performed":"Voltammetry",
                "Run on channel" : "6 (SN 14887)",
                "Electrode connection" : "standard",
                "Ewe ctrl range" : "min = 0.00 V, max = 5.00 V",
                "Acquisition started on" : "06/16/2016 11:52:12.000",
                "Loaded Setting File" : "NONE",
                "Saved on" :" none ",
                "File":"none ",
                "Device" : "VMP3 (SN 0711)"
                },
            "experiment_data" : out_cv_biologicmpr
        }
        delete_file(file_name)
        return (True, xx)
    except Error as err: 
        return (False, err)


def transform_data_xrd(file_name):    
    try:
        
        df =  pd.read_csv(file_name,
        sep = '\s+', 
        engine = 'python', 
        header = 0, 
        index_col = False, 
        )
        df.columns = ['2theta','intensity']
        df["intensity"]=df["intensity"]/max(df["intensity"])

        out_xrd = json.loads(df.to_json(orient='split'))

        # the json structure, four arrays in 1 json object. 
        # The experiment_info array might become bigger. We might want to read-out more data from the .res file. The auxiliary table, if existing, will be as long as the experiment_data file
        xx= {"experiment_info":{
            "device name":"unknown",
            "X-ray tube" : "unknown",
            "Position sensitive detector" : "unknown",
             "Spinning/non-spinning" : "unknown"},
        "experiment_data" : out_xrd}

        delete_file(file_name)
        return (True,xx)
    except Error as err: 
        return (False, err)


def transform_data_cellpy(file_name):
    try:
        mass = 1
        d = cellreader.CellpyData()
        d.from_raw(file_name)
        d.make_summary()
        print(d.check())
        
        c = d.cell
        df_raw= c.raw
        #multiple with 1000 for mA and mAh
        df_raw[["current","charge_capacity","discharge_capacity","charge_energy","discharge_energy"]]=df_raw[["current","charge_capacity","discharge_capacity","charge_energy","discharge_energy"]]*1000

        df_sum = c.summary
        df_sum['cycle_index']=df_sum.index
        df_sum2[['charge_capacity','discharge_capacity']]=df_sum2[['charge_capacity','discharge_capacity']]*1000
        df_sum2 = df_sum[['cycle_index','data_point', 'test_time', 'date_time', 'end_voltage_charge_u_V','end_voltage_discharge_u_V', 'charge_capacity', 'discharge_capacity','discharge_capacity_u_mAh_g', 'charge_capacity_u_mAh_g','cumulated_discharge_capacity_u_mAh_g','cumulated_charge_capacity_u_mAh_g', 'coulombic_efficiency_u_percentage', 'coulombic_difference_u_mAh_g','cumulated_coulombic_efficiency_u_percentage','cumulated_coulombic_difference_u_mAh_g','discharge_capacity_loss_u_mAh_g','cumulated_discharge_capacity_loss_u_mAh_g','charge_capacity_loss_u_mAh_g','cumulated_charge_capacity_loss_u_mAh_g', 'low_level_u_percentage','high_level_u_percentage', 'cumulated_ric_u_none','cumulated_ric_sei_u_none', 'cumulated_ric_disconnect_u_none','shifted_charge_capacity_u_mAh_g', 'shifted_discharge_capacity_u_mAh_g','normalized_cycle_index', 'charge_c_rate', 'discharge_c_rate']]

        out_summary = json.loads(df_sum2.to_json(orient='split')) # change  df_sum_small when you want to see the structure
        out_raw = json.loads(df_raw.to_json(orient='split')) # change  df_raw_small when you want to see the structure

        # the json structure, four arrays in 1 json object. 
        # The experiment_info array might become bigger. We might want to read-out more data from the .res file. The auxiliary table, if existing, will be as long as the experiment_data file
        xx={
                "experiment_info":{
                    "channel_number":c.channel_number,
                    "schedule_file_name" : c.schedule_file_name},
                "experiment_summary": out_summary,
                "auxiliary_table":{
                    "columns":["test_time","date_time"],
                    "index":[1,2,3],
                    "data":[[12029.0603495076,1572450446000],[20490.1864950906,1572458908000],[29256.6799169249,1572467675000]]},
                "experiment_data": out_raw
            }
        delete_file(file_name)
        return (True,xx)
    except Error as err: 
        return (False, err)



def insert_value(json_value):
    try:
        # Connect to an existing database
        connection = psycopg2.connect(user="postgres",
                                    password="postgres",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="flask_db")

        # Create a cursor to perform database operations
        cursor = connection.cursor()
        # Print PostgreSQL details
        print("PostgreSQL server information")
        print(connection.get_dsn_parameters(), "\n")
        # Executing a SQL query
        my_json = json.dumps(json_value)
        cursor.execute(f"INSERT into test(name, value) VALUES('test_1', '{my_json}')")
        # Fetch result
        
        connection.commit()
        # close communication with the database
        cursor.close()
        return True

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return False


functions = {'cellpy':transform_data_cellpy, 'galvani': transform_data_galvani,'xrd_custom':transform_data_xrd}

if __name__ == "__main__":
    print(transform_data_galvani(r"./uploads/example_cv.mpr"))