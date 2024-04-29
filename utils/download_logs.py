import os
import shutil
import zipfile
from datetime import datetime



def download(details):
    dev_id = details['deviceid']
    env = details['env']
    date = details['date']

    outdir = os.path.join(dev_id, date)
    print("Dowloading logs")
    cmd = 'aws s3 sync s3://idms-%s/logs_%s/%s/%s/ %s'
    os.system(cmd %(env, 0, dev_id, date, outdir))
    os.system(cmd %(env, 1, dev_id, date, outdir)) 
    os.system(cmd %(env, 2, dev_id, date, outdir))
    os.system(cmd %(env, 3, dev_id, date, outdir))
    os.system(cmd %(env, 4, dev_id, date, outdir))

    return outdir    
    
def extract_and_combine_logs(outdir):
    zip_files = os.listdir(outdir)
    for fil in zip_files:
        if ".7z" in fil:
            out_zip_dir = os.path.join(outdir, fil.split('.7z')[0])
            if os.path.exists(out_zip_dir):
                shutil.rmtree(out_zip_dir)
            cmd = "7z x ./%s.7z -o./%s"%(out_zip_dir,out_zip_dir)
            out = os.system(cmd)
            os.remove(os.path.join(outdir, fil))
        elif ".zip" in fil:
            out_zip_dir = os.path.join(outdir, fil.split('.zip')[0])
            if os.path.exists(out_zip_dir):
                shutil.rmtree(out_zip_dir)
            with zipfile.ZipFile(os.path.join(outdir, fil), 'r') as zip_ref:
                zip_ref.extractall(out_zip_dir)
            os.remove(os.path.join(outdir, fil))
            
        logs_comb = ['analytics', 'audio'] 
        new_logs_comb = ['inertialAnalyticsClient', 'inwardAnalyticsClient', 'outwardAnalyticsClient', 'inference', 'scheduler','overspeedClient']
        cmd = "cat %s/*/%s/log_* > %s/%s.log"
        for logs in logs_comb:
            os.system(cmd%(outdir,logs,outdir,logs))

        cmd = "cat %s/*/%s/%s.log* > %s/%s.log"
        for logs in new_logs_comb:
            os.system(cmd%(outdir,logs,logs,outdir,logs))
        for i in ['reboot','ndcentral','health','inference_inertial']:
                cmd = "cat {0}/*/{1}/* > {0}/{1}.log".format(outdir,i)
                os.system(cmd)
            
        # logs_comb = ['analytics', 'audio'] 
        # new_logs_comb = ['inertialAnalyticsClient', 'inwardAnalyticsClient', 'outwardAnalyticsClient', 'inference', 'scheduler','overspeedClient']
        # cmd = "cat %s/*/%s_c/log_* > %s/%s.log"
        # for logs in logs_comb:
        #     # os.makedirs("curr_"+logs)
        #     os.system(cmd%(outdir,logs,outdir,logs))
        # # print("126172")

        # cmd = "cat %s/*/%s_c/%s.log* > %s/%s.log"
        # for logs in new_logs_comb:
        #     os.system(cmd%(outdir,logs,logs,outdir,logs))
        # for i in ['reboot','ndcentral','health','inference_inertial']:
        #         cmd = "cat {0}/*/{1}_c/* > {0}/{1}.log".format(outdir,i)
        #         os.system(cmd)
    
