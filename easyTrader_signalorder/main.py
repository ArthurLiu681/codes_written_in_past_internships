from model.Monitor import check_easytrader_connection, check_wind_connection
from model.Strategies import get_snapshot_data, get_holc_data, order_by_mas, order_by_time_signal, order_by_bollinger, order_by_rsi
from model import Global_variables

if __name__ == '__main__':

    scheduler = Global_variables.get_value("scheduler")

    with open(".//log.txt", "w") as f:
        scheduler.add_job(check_easytrader_connection, 'cron', day_of_week='0-4', hour='10', minute='23', second='00',
                          id='check_easytrader_connection', args=[])
        scheduler.add_job(check_wind_connection, 'cron', day_of_week='0-4', hour='10', minute='23', second='00',
                          id='check_wind_connection', args=[])
        scheduler.add_job(get_snapshot_data, 'cron', day_of_week='0-4', hour='9-16', minute='00-59', second='00-59',
                          id='get_snapshot_data', args=[])
        # scheduler.add_job(get_holc_data, 'cron', day_of_week='0-4', hour='15', minute='31', second='00',
        #                   id='get_holc_data', args=[])
        scheduler.add_job(order_by_mas, 'cron', day_of_week='0-4', hour="9-17", minute="00-59", second="00-59",
                          id='order_by_mas', args=[f])
        # scheduler.add_job(order_by_time_signal, 'cron', day_of_week='0-4', hour='9-14', minute='0, 30', second='00',
        #                   id='order_by_time_signal', args=[f])
        # scheduler.add_job(order_by_bollinger, 'cron', day_of_week='0-4', hour='09', minute='15', second='00',
        #                   id='order_by_bollinger', args=[f])
        # scheduler.add_job(order_by_rsi, 'cron', day_of_week='0-4', hour='09', minute='15', second='00',
        #                   id='order_by_rsi', args=[f])
        scheduler.start()
