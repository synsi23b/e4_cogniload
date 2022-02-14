from datetime import timedelta
import xlsxwriter
from helper import get_participant_folders, get_participant_eda, get_participant_bds_stamps

workbook = xlsxwriter.Workbook("bds_eda.xlsx")

for parti in get_participant_folders():
    eda = get_participant_eda(parti)
    stamps = get_participant_bds_stamps(parti)
    ws = workbook.add_worksheet(parti.name)
    ws.write(0, 0, "Index")
    ws.write(0, 1, "Date")
    ws.write(0, 2, "EDA")
    ws.write(0, 3, "listen start")
    ws.write(0, 4, "listen end")
    ws.write(0, 5, "answered correct")
    ws.write(0, 6, "answered incorrect")
    eda_length = len(eda[2])
    data_delta = timedelta(seconds=(1.0 / eda[1]))
    ts = eda[0]
    def row_gen(inlist):
        for x in inlist:
            yield x
        while True:
            yield None
    stamp_row_gen = row_gen(stamps)
    current_row = next(stamp_row_gen)
    # store current state and row to write on as one variable
    # start as state 4 = waiting / answered
    state = 5
    bds_challenge = 1
    for i, d in enumerate(eda[2]):
        row = i + 1
        ws.write(row, 0, row)
        ws.write(row, 1, ts.isoformat())
        ts += data_delta
        # eda
        ws.write(row, 2, d)
        # listen start
        ws.write(row, 3, 0)
        # listen end
        ws.write(row, 4, 0)
        # answered c
        ws.write(row, 5, 0)
        # answered i
        ws.write(row, 6, 0)
        # basic date filled, check appropriate state for time, than overwrite
        if current_row is not None:
            if state == 3:
                # last determined state is listening, check if its time to transition to stop listen
                if ts >= current_row["listen_end"]:
                    state = 4
            elif state == 4:
                # listen over, check for answered
                if ts >= current_row["answer_stamp"]:
                    if current_row["correct"] == "1":
                        state = 5
                    else:
                        state = 6
                    current_row = next(stamp_row_gen)
            elif state == 5 or state == 6:
                # answer was given, check for next listen
                if ts >= current_row["listen_start"]:
                    state = 3
                    bds_challenge = current_row["bds_count"]
        ws.write(row, state, bds_challenge)

workbook.close()