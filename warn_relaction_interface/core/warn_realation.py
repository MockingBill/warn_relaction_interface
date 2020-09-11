import pandas as pd
from .. import settings
import os
from apyori import apriori
import logging

logger = logging.getLogger('log')


class warn_relation:
    def __init__(self, sup, cond, time):
        self.all_gr_data = []
        self.apro = []
        self.min_sup = sup
        self.min_cond = cond
        self.time_window = time
        self.work_id = None
        self.data_num = 0
        self.time = 0
        self.data_len = 0


    def file_deal(self, path, work_id):
        try:
            with open(os.path.join(settings.PROCESS_URL, 'process_' + work_id), 'a+') as f:
                print("[" + work_id + "]" + " 开始任务：", file=f)
            self.work_id = work_id
            suffix = str(path).split(".")[-1]
            warn_data = None
            if suffix == 'csv':
                warn_data = pd.read_csv(path, encoding='utf-8')
            elif suffix == 'xlsx' or suffix == 'xls':
                warn_data = pd.read_excel(path)
            warn_data.columns = ['TIME_OF_ALARM', 'MAJOR', 'MANUFACTURER', 'NETWORK_ELEMENT_NAME', 'TITLE']
            self.data_len = warn_data.shape[0]
            warn_data['TIME_OF_ALARM'] = pd.to_datetime(pd.to_datetime(warn_data['TIME_OF_ALARM']), unit='ms')
            warn_data.groupby(['NETWORK_ELEMENT_NAME']).apply(self.fiest_apply)
            results = self.do_apriori()
            j_resu = {'rule': [], 'support': []}
            for k, v in enumerate(results):
                # 只看有两个及以上元素的关联集合。单独一个元素的集合没有意义。
                if len(v.items) >= 2:
                    j_resu['rule'].append(' '.join(list(v.items)))
                    j_resu['support'].append(v.support)
            z_resu = pd.DataFrame(j_resu)
            z_resu.to_csv(os.path.join(settings.DWON_RESU_URL, work_id + ".csv"), encoding="utf-8",index=None)
            with open(os.path.join(settings.PROCESS_URL, 'process_' + self.work_id), 'a+') as f:
                print("[" + self.work_id + "]" + "  当前进度：100%",
                      file=f)
        except Exception as e:
            logging.error("[" + work_id + "]:核心算法处理出错" + str(e))

    def fiest_apply(self, row):
        self.data_num=self.data_num+row.shape[0]
        self.time=self.time + 1
        if int(self.time)%10000==0:
            with open(os.path.join(settings.PROCESS_URL,'process_'+self.work_id),'a+') as f:
                print("[" + self.work_id + "]" + "  当前进度：" + str(round(self.data_num / self.data_len * 100, 2)) + "%",
                      file=f)
        if row.shape[0] >= 2:


            row = row.sort_values('TIME_OF_ALARM')

            flag_row = pd.DataFrame()
            flag_array = []
            for k, v in row.iterrows():
                if not flag_row.empty:
                    differ = v['TIME_OF_ALARM'] - flag_row['TIME_OF_ALARM']
                    if differ.seconds <= self.time_window:
                        flag_array.append(v['TITLE'])
                    else:
                        flag_row = v
                        self.all_gr_data.append(flag_array)
                        flag_array = []
                else:
                    flag_row = v
                    flag_array.append(v['TITLE'])
            return None

        else:
            return None

    def do_apriori(self):
        for i in self.all_gr_data:
            if len(i) >= 2:
                self.apro.append(list(map(lambda x: str(x), i)))
        results = list(apriori(self.apro, min_confidence=0.001, min_support=0.001, min_lift=1))
        return results



