accepted_files = ['MPR','RES','TXT']
accepted_tests = ['VOLTAMMETRY-CYCLIC VOLTAMMETRY (CV)', 'CHARGE-DISCHARGE-GALVANOSTATIC CYCLING', 'EIS', 'XRD']
accepted_instruments = ['ARBIN-BT-2000', 'BIOLOGIC-VMP3', 'BIOLOGIC-MPG2','STOE-STADI P']


# file -> test -> instrument
accepted_combinations = {
    0:{
        0:{1,2},
    },
    1:{
        1:{0},
    },
    2:{
        3:{3}
    }
}

